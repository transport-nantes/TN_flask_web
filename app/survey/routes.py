import logging
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask import current_app as app
from flask_login import login_user, logout_user, current_user
from app import db
from app.survey import bp
from app.survey.survey_v1 import do_municipales_responses_v1

@bp.route('/D/<tag>/municipales', defaults={'seed': None})
@bp.route('/F/<tag>/<seed>/municipales')
def municipales_responses(tag, seed):
    """Display the municipal survey results.

    Or guide the user to finding the results s/he wants.

    This function is slightly borked, because it's not filtering on
    survey id.  It should.  But for the moment there's only one survey
    id, so put that off in the interests of getting this out.

    """
    return do_municipales_responses_v1(tag, seed)

@bp.route('/F/<tag>/<seed>/municipales-candidat')
def municipales_candidats(tag, seed):
    return render_template('municipales-survey.html', tag=tag, seed=g.seed)

