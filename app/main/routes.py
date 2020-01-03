from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, session
from app import db
from app.main import bp
from app.models import UserJourneyStep
from random import randint
import re

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

URL_REGEX = re.compile('https?://([^/]+)/(.*)$')
TAG_REGEX = re.compile('[DE]/([^/]+)/(.*$)')

@bp.before_app_request
def before_request():
    if 'static' == request.endpoint:
        # This should only happen in dev.  Otherwise, nginx handles static routes directly.
        return
    #print(UserJourneyStep.query.all())
    journey_step = UserJourneyStep()
    journey_step.ip_hash = '';
    journey_step.referrer = request.referrer
    if request.referrer:
        [(referrer_host, referrer_path)]  = URL_REGEX.findall(request.referrer)
        journey_step.referrer_host = referrer_host

    journey_step.this_page_url = request.url
    [(this_host, this_path)]  = URL_REGEX.findall(request.url)
    if this_path:
        [(this_page_tag, this_page_canonical)] = TAG_REGEX.findall(this_path)
        journey_step.tag = this_page_tag
        journey_step.this_page_canonical = this_page_canonical
    else:
        journey_step.tag = ''
        journey_step.this_page_canonical = '/'
    journey_step.browser = request.headers.get('User-Agent')
    db.session.add(journey_step)
    db.session.commit()

@bp.route('/')
@bp.route('/accueil')
def index_root():
    """Assign a session tag.

    Of all the *_root functions, this one is actually critical, since
    we fully expect people to come in to the root page with no
    modifiers.

    """
    return redirect(url_for('main.index', tag=make_new_tag()))

@bp.route('/municipales.html')
@bp.route('/municipales/')
def municipales_root():
    return redirect(url_for('main.municipales', tag=make_new_tag()))

@bp.route('/D/<tag>/accueil/')
@bp.route('/D/<tag>/accueil')
def index(tag):
    return render_template('index.html', title='', tag=tag)

@bp.route('/D/<tag>/chronotrain/')
@bp.route('/D/<tag>/chronotrain')
def chronotrain(tag):
    return render_template('chronotrain.html', tag=tag)

@bp.route('/D/<tag>/velopolitain/')
@bp.route('/D/<tag>/velopolitain')
def velopolitain(tag):
    return render_template('velopolitain.html', tag=tag)

@bp.route('/D/<tag>/2019/')
@bp.route('/D/<tag>/2019')
def velopolitain_2019(tag):
    return render_template('velopolitain-appeal.html', tag=tag)

@bp.route('/D/<tag>/about/')
def about_transport_nantes(tag):
    return render_template('about.html', tag=tag), 404

@bp.route('/D/<tag>/chantenay/')
def chantenay(tag):
    return render_template('chantenay.html', tag=tag), 404

@bp.route('/D/<tag>/municipales/')
@bp.route('/D/<tag>/municipales')
def municipales(tag=None):
    return render_template('municipales.html', tag=tag)

@bp.route('/D/<tag>/sponsor/')
@bp.route('/D/<tag>/sponsor')
def sponsor(tag=None):
    return render_template('sponsor.html', tag=tag)

@bp.route('/D/<tag>/aligned/')
@bp.route('/D/<tag>/aligned')
@bp.route('/D/<tag>/asso/')
@bp.route('/D/<tag>/asso')
def aligned(tag=None):
    return render_template('aligned.html', tag=tag)

@bp.route('/D/<tag>/benevole/')
@bp.route('/D/<tag>/benevole')
@bp.route('/D/<tag>/bénévole/')
@bp.route('/D/<tag>/bénévole')
def volunteer(tag=None):
    return render_template('volunteer.html', tag=tag)

@bp.route('/D/<tag>/ecole')
def ecole(tag):
    return render_template('ecole.html', tag=tag), 404

@bp.route('/D/<tag>/presse')
def presse(tag):
    return render_template('presse.html', tag=tag), 404

@bp.route('/D/<tag>/mentions_legales')
def legal(tag):
    return render_template('legale.html', tag=tag), 404

@bp.route('/D/<tag>/blog/<blog_entry>')
def blog(tag, blog_entry):
    return render_template('blog.html', tag=tag, body='Hello, world!'), 404

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
