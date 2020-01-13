from app import db
from app.models import Survey, SurveyQuestion, SurveyResponder, SurveyResponse
from flask import render_template, request, g, current_app, session

def do_municipales_responses(tag, seed):
    """Display the municipal survey results.

    Or guide the user to finding the results s/he wants.

    This function is slightly borked, because it's not filtering on
    survey id.  It should.  But for the moment there's only one survey
    id, so put that off in the interests of getting this out.

    """
    commune = request.args.get('commune')
    communes = db.session.query(SurveyResponder.commune.distinct()).order_by(
        SurveyResponder.commune.asc()).all()
    liste = request.args.get('liste')
    listes = []
    question = request.args.get('question')
    questions = []
    question_contents = None
    survey_response = None

    if commune is None:
        # User has not yet selected a commune.  Unless there's not
        # choice to make, start by offering that choice.
        if len(communes) != 1:
            return render_template('municipales-question.html', tag=tag, seed=g.seed,
                                   communes=communes, this_commune=commune,
                                   listes=listes, this_liste=liste,
                                   questions=questions, this_question=question,
                                   question_contents=question_contents,
                                   survey_response=survey_response)
        commune = communes[0]

    # We have a unique commune.
    listes = db.session.query(
        SurveyResponder.liste.distinct(), SurveyResponder.tete_de_liste).filter_by(
            commune=commune).order_by(
                SurveyResponder.liste.asc()).all()
    if liste is None:
        # Got commune but not liste, so provide a list of lists.
        # Unless there's only one liste, in which case might as well
        # just choose it and be on our way.
        if len(listes) != 1:
            return render_template('municipales-question.html', tag=tag, seed=g.seed,
                                   communes=communes, this_commune=commune,
                                   listes=listes, this_liste=liste,
                                   questions=questions, this_question=question,
                                   question_contents=question_contents,
                                   survey_response=survey_response)
        liste = listes[0][0]

    # We have a unique commune and a unique list.
    questions = db.session.query(SurveyQuestion.question_number, \
                                 SurveyQuestion.question_title).order_by(
                                    SurveyQuestion.sort_index.asc()).all()
    if question is None or '' == question:
        # We know commune and list/party, but not the question of
        # interest.  Request user to pick a question.
        return render_template('municipales-question.html', tag=tag, seed=g.seed,
                                   communes=communes, this_commune=commune,
                                   listes=listes, this_liste=liste,
                                   questions=questions, this_question=question,
                                   question_contents=question_contents,
                                   survey_response=survey_response)

    question_contents = db.session.query(SurveyQuestion.question_title,
                                         SurveyQuestion.question_text).filter_by(
                                             question_number=question).one()
    survey_response = db.session.query(SurveyResponse.survey_question_response).filter_by(
        survey_question_id=question,
        ).one_or_none()
    # We know the question, so just display that one response.
    return render_template('municipales-question.html', tag=tag, seed=g.seed,
                           communes=communes, this_commune=commune,
                           listes=listes, this_liste=liste,
                           questions=questions, this_question=question,
                           question_contents=question_contents,
                           survey_response=survey_response)
