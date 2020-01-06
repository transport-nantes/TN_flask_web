from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, session
from app import db
from app.main import bp
from app.models import UserJourneyStep
from app.models import Survey, SurveyQuestion, SurveyResponder, SurveyResponse
from random import randint
import re
# md5 takes about 2-3 ns to run on my laptop, whilst sha1 takes 8-10
# ns to run.  In both cases, this is negligible, but it seems prudent
# to choose the faster, since a 128 bit md5 hash of a 32 bit ip
# address is good enough for our non-cryptographic purposes.
from hashlib import md5

TAG_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
def make_new_tag():
    """Generate a new session tag.

    64^5 corresponds to a new session tag every second for 34 years.
    That should be plenty.

    We don't insist on session keys conforming to this format.  This
    is merely how we generate them.

    """
    tag_char_end = len(TAG_CHARS) - 1
    return TAG_CHARS[randint(0,tag_char_end)] + \
        TAG_CHARS[randint(0,tag_char_end)] + TAG_CHARS[randint(0,tag_char_end)] + \
        TAG_CHARS[randint(0,tag_char_end)] + TAG_CHARS[randint(0,tag_char_end)]

def make_new_seed():
    """Generate a new seed.

    We use seeds to stitch together user journeys.  In a perfect
    world, the (ip_hash, tag) pair would be unique to a visitor, even
    though IP address may change be over time.  But it is quite
    reasonable to imagine multiple visitors arriving from behind the
    same NAT address.  In such a case, we'd like to be able to knit
    together the pages each individual visited.

    Our strategy is to generate a new seed on each visit.  All
    outgoing links, whether local (/D/...) or exit (/E/...) take a tag
    and then a seed.  On each visit we record referrer and the URL
    requested.  When stitching user journeys, we process (ip_hash,
    tag) pair threads and then construct the forest of trees that have
    the property that child nodes record as referrer the this_page_url
    of the parent.

    This has the perverse effect that we don't actually make use of
    the seeds we receive.  We are forced to parse them in order to
    deconstruct the actual URL root that we'd use, for example, in
    calling url_for().

    Finally, note that because seed-less URLs already exist in the
    wild, we have to be prepared to accept URLs with tag but no seed.
    Realistically, we need to do that forever.

    """
    tag_char_end = len(TAG_CHARS) - 1
    return TAG_CHARS[randint(0,tag_char_end)] + \
        TAG_CHARS[randint(0,tag_char_end)]

URL_REGEX = re.compile('https?://([^/]+)/(.*)$')
TAG_REGEX = re.compile('[DEF]/([^/]+)/(.*$)')

@bp.before_app_request
def before_request():
    g.seed = make_new_seed()
    if 'static' == request.endpoint:
        # This should only happen in dev.  Otherwise, nginx handles static routes directly.
        return
    #print(UserJourneyStep.query.all())
    journey_step = UserJourneyStep()
    journey_step.ip_hash = md5(request.remote_addr.encode()).hexdigest();
    journey_step.referrer = request.referrer
    if request.referrer:
        [(referrer_host, referrer_path)]  = URL_REGEX.findall(request.referrer)
        journey_step.referrer_host = referrer_host

    journey_step.this_page_url = request.url
    [(this_host, this_path)]  = URL_REGEX.findall(request.url)
    if this_path:
        # We don't need to pull out seed, because we only use it to
        # match current URL against referrer in computing threads.
        [(this_page_tag, this_page_canonical)] = TAG_REGEX.findall(this_path)
        journey_step.tag = this_page_tag
        journey_step.this_page_canonical = this_page_canonical
    else:
        journey_step.tag = ''
        journey_step.this_page_canonical = '/'
    journey_step.is_entry = (this_host != journey_step.referrer_host)

    journey_step.ua_string = request.headers.get('User-Agent')
    journey_step.ua_browser = request.user_agent.browser
    journey_step.ua_language = request.user_agent.language
    journey_step.ua_platform = request.user_agent.platform
    journey_step.ua_version = request.user_agent.version
    db.session.add(journey_step)
    db.session.commit()

"""
Route policy:

The only route that may have no prefix is the root itself.  Anything
else is assumed to be a click or scan, not a user typing something by
hand.

The /D/ routes are followed by a tag.  They are deprecated, but we
must support them, basically forever, so that links in the wild will
continue to resolve.

The /E/ routes are followed by a tag and seed.  They represent site exit only.

The /F/ routes are followed by a tag and seed.  They replace /D/ routes.

"""

@bp.route('/')
@bp.route('/accueil')
@bp.route('/index')
@bp.route('/index.html')
def index_root():
    """Assign a session tag.

    Of all the *_root functions, this one is actually critical, since
    we fully expect people to come in to the root page with no
    modifiers.

    """
    return redirect(url_for('main.index', tag=make_new_tag(), seed=g.seed))

@bp.route('/F/<tag>/<seed>/accueil')
@bp.route('/D/<tag>/accueil')
def index(tag, seed=None):
    return render_template('index.html', title='', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/chronotrain')
@bp.route('/D/<tag>/chronotrain')
def chronotrain(tag, seed=None):
    return render_template('chronotrain.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/velopolitain')
@bp.route('/D/<tag>/velopolitain')
def velopolitain(tag, seed=None):
    return render_template('velopolitain.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/2019')
@bp.route('/D/<tag>/2019')
def velopolitain_2019(tag, seed=None):
    return render_template('velopolitain-appeal.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/about')
@bp.route('/D/<tag>/about')
def about_transport_nantes(tag, seed=None):
    return render_template('about.html', tag=tag, seed=g.seed), 404

@bp.route('/F/<tag>/<seed>/chantenay')
@bp.route('/D/<tag>/chantenay')
def chantenay(tag, seed=None):
    return render_template('chantenay.html', tag=tag, seed=g.seed), 404

@bp.route('/D/<tag>/municipales', defaults={'seed': None})
@bp.route('/F/<tag>/<seed>/municipales')
def municipales_responses(tag, seed):
    """Display the municipal survey results.

    Or guide the user to finding the results s/he wants.

    This function is slightly borked, because it's not filtering on
    survey id.  It should.  But for the moment there's only one survey
    id, so put that off in the interests of getting this out.

    """
    commune = request.args.get('commune')
    liste = request.args.get('liste')
    question = request.args.get('question')

    communes = db.session.query(SurveyResponder.commune.distinct()).all()
    communes = [x[0] for x in communes]
    if commune is None:
        # Provide a choice of commune.
        if len(communes) != 1:
            return render_template('municipales-choose-commune.html', tag=tag, seed=g.seed, communes=communes)
        commune = communes[0]

    # We have a unique commune.
    lists = db.session.query(
        SurveyResponder.liste.distinct(), SurveyResponder.tete_de_liste).filter_by(
            commune=commune).all()
    if liste is None:
        # Got commune but not party/liste, so provide a list of lists.
        if len(lists) != 1:
            return render_template('municipales-choose-list.html', tag=tag, seed=g.seed,
                                   communes=communes, commune=commune, lists=lists)
        liste = lists[0][0]

    # We have a unique commune and a unique list.
    questions = db.session.query(SurveyQuestion.question_number, SurveyQuestion.question_title).order_by(
        SurveyQuestion.sort_index.asc()).all()
    if question is None:
        # We know commune and list/party, but not the question of
        # interest.  Display all questions.
        return render_template('municipales-choose-question.html', tag=tag, seed=g.seed,
                               communes=communes, commune=commune, lists=lists, liste=liste,
                               questions=questions)

    question_contents = db.session.query(SurveyQuestion.question_title,
                                         SurveyQuestion.question_text).filter_by(
                                             question_number=question).one()
    survey_response = db.session.query(SurveyResponse.survey_question_response).filter_by(
        survey_question_id=question).one_or_none()
    # We know the question, so just display that one response.
    return render_template('municipales-show-question.html', tag=tag, seed=g.seed,
                           communes=communes, commune=commune,
                           lists=lists,liste=liste,
                           questions=questions, question=question,
                           question_contents=question_contents,
                           survey_response=survey_response)

@bp.route('/F/<tag>/<seed>/municipales-candidat')
def municipales_candidats(tag, seed):
    return render_template('municipales-survey.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/sponsor')
@bp.route('/D/<tag>/sponsor')
def sponsor(tag, seed=None):
    return render_template('sponsor.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/asso')
@bp.route('/D/<tag>/asso')
def aligned(tag, seed=None):
    return render_template('aligned.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/bénévole')
@bp.route('/D/<tag>/bénévole')
def volunteer(tag, seed=None):
    return render_template('volunteer.html', tag=tag, seed=g.seed)

@bp.route('/F/<tag>/<seed>/ecole')
@bp.route('/D/<tag>/ecole')
def ecole(tag, seed=None):
    return render_template('ecole.html', tag=tag, seed=g.seed), 404

@bp.route('/F/<tag>/<seed>/presse')
@bp.route('/D/<tag>/presse')
def presse(tag, seed=None):
    return render_template('presse.html', tag=tag, seed=g.seed), 404

@bp.route('/F/<tag>/<seed>/mentions_legales')
@bp.route('/D/<tag>/mentions_legales')
def legal(tag, seed=None):
    return render_template('legale.html', tag=tag, seed=g.seed), 404

@bp.route('/F/<tag>/<seed>/blog/<blog_entry>')
@bp.route('/D/<tag>/blog/<blog_entry>')
def blog(tag, blog_entry):
    return render_template('blog.html', tag=tag, seed=g.seed, body='Hello, world!'), 404

## Legacy paths from old wordpress site.
@bp.route('/?page_id=397')
@bp.route('/page_id=397.html')
@bp.route('/?page_id=213')
@bp.route('/page_id=213.html')
def legacy_index():
    return redirect(url_for('index'))

@bp.route('/?page_id=363')
@bp.route('/page_id=363.html')
@bp.route('/?page_id=338')
@bp.route('/page_id=338.html')
@bp.route('/?page_id=324')
@bp.route('/page_id=324.html')
@bp.route('/?page_id=317')
@bp.route('/page_id=317.html')
def legacy_chronotrain():
    return redirect(url_for('chronotrain'))

@bp.route('/?page_id=258')
@bp.route('/page_id=258.html')
@bp.route('/?page_id=243')
@bp.route('/page_id=243.html')
@bp.route('/?page_id=258')
@bp.route('/page_id=258.html')
def legacy_ecole():
    return redirect(url_for('ecole'))

@bp.route('/?page_id=284')
@bp.route('/page_id=284.html')
def legacy_blog_european_elections():
    return redirect(url_for('blog', 'L', 'élections_européennes'))

@bp.route('/?page_id=293')
@bp.route('/page_id=293.html')
def legacy_blog_casque_obligatoire():
    return redirect(url_for('blog', 'L', 'casque_obligatoire'))
