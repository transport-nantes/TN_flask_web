import logging
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask import current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import Survey
from app.survey.forms import SurveyForm
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


@login_required
@bp.route('/F/<tag>/<seed>/list/survey', methods=['GET'])
def survey_list(tag, seed):
    """List most recent surveys and offer search that also adds new
    surveys.

    """
    # check_admin('survey')
    form = SurveyForm()
    surveys = Survey.query.order_by('updated_seconds').limit(5)
    return render_template('survey/list_surveys.html',
                           tag=tag, seed=seed,
                           form=form,
                           surveys=surveys)

@login_required
@bp.route('/F/<tag>/<seed>/edit/survey', methods=['GET', 'POST'])
def survey_edit(tag, seed):
    """Add or edit a Survey.
    """
    # check_admin('survey')
    form = SurveyForm()
    survey = None
    survey_id = request.args.get('survey_id', None)
    print('#### ', request.method, ' ####')
    if request.method == 'POST':
        print('#### POST ####')
        if form.validate_on_submit():
            print('#### validated ####')
            # The user may have changed the survey name, so first
            # search based on the name.
            survey = Survey.query.filter_by(name=form.name.data).one_or_none()
            if survey is None and survey_id is not None:
                print('#### no survey, yes survey_id ####', survey_id)
                # If we didn't find the survey by name but we have a
                # survey_id, then we should use that.
                survey = Survey.query.filter_by(id=survey_id).one_or_none()
            if survey is None:
                print('#### no survey ####')
                # If we still don't have a survey, then this is a new
                # survey, so we must start by creating it.
                print('#### New ####')
                survey = Survey(name=form.name.data,
                                description=form.description.data)
                db.session.add(survey)
            else:
                print('#### yes survey ####')
                survey.id = form.id.data
                survey.name = form.name.data
                survey.description = form.description.data
            try:
                print('#### Save ####')
                db.session.commit()
                print('#### Committed ####')
            except:
                # If name already exists, for example.
                # Even though we're editing, the user can change the name,
                # and changing to existing isn't permitted.
                #### How do I handle this?
                #### I want to re-present the form with explanation message.
                print('#### Exception ####')
                db.session.rollback()
        else:
            # Problem with posted survey.
            #### How do we signal to the user what the error was??
            pass
        return render_template('survey/mod_survey.html',
                               tag=tag, seed=seed,
                               form=form,
                               survey=survey,
                               questions=survey.questions)

    if survey_id is None:
        print('#### survey_id is still none ####')
        render_template(''), 404
    print('#### survey_id is not none ####', survey_id)
    survey = Survey.query.filter_by(id=survey_id).first_or_404()
    form.id.data = survey_id
    form.name.data = survey.name
    form.description.data = survey.description
    return render_template('survey/mod_survey.html',
                           tag=tag, seed=seed,
                           form=form,
                           survey=survey,
                           questions=survey.questions)
