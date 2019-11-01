from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from app.main import bp
from random import randint

TAG_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
def make_new_tag():
    """Generate a new session tag.

    64^5 corresponds to a new session tag every second for 34 years.
    That should be plenty.

    We don't insist on session keys conforming to this format.  This
    is merely how we generate them.

    """
    return TAG_CHARS[randint(0,61)] + \
        TAG_CHARS[randint(0,63)] + TAG_CHARS[randint(0,63)] + \
        TAG_CHARS[randint(0,63)] + TAG_CHARS[randint(0,63)]

@bp.before_app_request
def before_request():
    print('before_request')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/accueil', methods=['GET', 'POST'])
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



@bp.route('/D/<tag>/accueil/', methods=['GET', 'POST'])
@bp.route('/D/<tag>/accueil', methods=['GET', 'POST'])
def index(tag):
    return render_template('index.html', title='', tag=tag)

@bp.route('/D/<tag>/chronotrain/')
@bp.route('/D/<tag>/chronotrain')
def chronotrain(tag):
    return render_template('chronotrain.html', tag=tag), 404

@bp.route('/D/<tag>/velopolitain/')
@bp.route('/D/<tag>/velopolitain')
def velopolitain(tag):
    return render_template('velopolitain.html', tag=tag), 404

@bp.route('/D/<tag>/about/')
def about_transport_nantes(tag):
    return render_template('about.html', tag=tag), 404

@bp.route('/D/<tag>/chantenay/')
def chantenay(tag):
    return render_template('chantenay.html', tag=tag), 404

@bp.route('/D/<tag>/municipales/')
@bp.route('/D/<tag>/municipales')
def municipales(tag=None):
    return render_template('municipales.html', tag=tag), 404

@bp.route('/D/<tag>/sponsor/')
@bp.route('/D/<tag>/sponsor')
def sponsor(tag=None):
    return render_template('sponsor.html', tag=tag), 404

@bp.route('/D/<tag>/aligned/')
@bp.route('/D/<tag>/aligned')
@bp.route('/D/<tag>/asso/')
@bp.route('/D/<tag>/asso')
def aligned(tag=None):
    return render_template('aligned.html', tag=tag), 404

@bp.route('/D/<tag>/benevole/')
@bp.route('/D/<tag>/benevole')
@bp.route('/D/<tag>/bénévole/')
@bp.route('/D/<tag>/bénévole')
def volunteer(tag=None):
    return render_template('volunteer.html', tag=tag), 404

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
@bp.route('/?page_id=397', methods=['GET', 'POST'])
@bp.route('/page_id=397.html', methods=['GET', 'POST'])
@bp.route('/?page_id=213', methods=['GET', 'POST'])
@bp.route('/page_id=213.html', methods=['GET', 'POST'])
def legacy_index():
    return redirect(url_for('index'))

@bp.route('/?page_id=363', methods=['GET', 'POST'])
@bp.route('/page_id=363.html', methods=['GET', 'POST'])
@bp.route('/?page_id=338', methods=['GET', 'POST'])
@bp.route('/page_id=338.html', methods=['GET', 'POST'])
@bp.route('/?page_id=324', methods=['GET', 'POST'])
@bp.route('/page_id=324.html', methods=['GET', 'POST'])
@bp.route('/?page_id=317', methods=['GET', 'POST'])
@bp.route('/page_id=317.html', methods=['GET', 'POST'])
def legacy_chronotrain():
    return redirect(url_for('chronotrain'))

@bp.route('/?page_id=258', methods=['GET', 'POST'])
@bp.route('/page_id=258.html', methods=['GET', 'POST'])
@bp.route('/?page_id=243', methods=['GET', 'POST'])
@bp.route('/page_id=243.html', methods=['GET', 'POST'])
@bp.route('/?page_id=258', methods=['GET', 'POST'])
@bp.route('/page_id=258.html', methods=['GET', 'POST'])
def legacy_ecole():
    return redirect(url_for('ecole'))

@bp.route('/?page_id=284', methods=['GET', 'POST'])
@bp.route('/page_id=284.html', methods=['GET', 'POST'])
def legacy_blog_european_elections():
    return redirect(url_for('blog', 'L', 'élections_européennes'))

@bp.route('/?page_id=293', methods=['GET', 'POST'])
@bp.route('/page_id=293.html', methods=['GET', 'POST'])
def legacy_blog_casque_obligatoire():
    return redirect(url_for('blog', 'L', 'casque_obligatoire'))
