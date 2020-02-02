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
    survey_id = request.args.get('survey_id', None)
    if survey_id is None:
        print('#### survey_id is None ####')
        # This is a new survey, so we must start by creating it.
        survey = Survey(name=form.name.data,
                        description=form.description.data)
        if form.validate_on_submit():
            print('#### validated ####')
            try:
                print('#### saving ####')
                db.session.add(survey)
                db.session.commit()
                print('#### committed ####')
            except:
                # If name already exists, for example.
                # Even though we're editing, the user can change the name,
                # and changing to existing isn't permitted.
                #### How do I handle this?
                #### I want to re-present the form with explanation message.
                print('#### exception ####')
                db.session.rollback()
        else:
            # Problem with posted survey.
            #### How do we signal to the user what the error was??
            return render_template('survey/mod_survey.html',
                                   tag=tag, seed=seed,
                                   form=form,
                                   survey=survey,
                                   questions=[])
    else:
        print('#### id is not none ####')
        survey = Survey.query.filter_by(id=survey_id).first_or_404()
        form.name.data = survey.name
        form.description.data = survey.description
    # We have a survey, so display it.
    questions = survey.questions
    return render_template('survey/mod_survey.html',
                           tag=tag, seed=seed,
                           form=form,
                           survey=survey,
                           questions=questions)
