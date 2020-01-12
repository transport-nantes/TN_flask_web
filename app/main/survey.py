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
