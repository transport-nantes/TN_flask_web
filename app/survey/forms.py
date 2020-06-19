from flask_wtf import FlaskForm
from wtforms import StringField, TextField, IntegerField, BooleanField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Survey


class SurveyForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom du sondage', validators=[DataRequired()])
    description = StringField('Description du sondage')

class SurveyQuestionForm(FlaskForm):
    id = HiddenField('id')
    survey_id = HiddenField('survey_id')
    question_number = StringField('Numéro')
    sort_index = IntegerField('Position de trie')
    question_title = StringField('Titre', validators=[DataRequired()])
    question_text = StringField('Titre', widget=TextArea(), validators=[DataRequired()])

class SurveyTargetForm(FlaskForm):
    id = HiddenField('id')
    survey_id = HiddenField('survey_id')
    validated = BooleanField('Validé')
    commune = StringField('Commune')
    liste = StringField('Liste')
    tete_de_liste = StringField('Tête de liste')
    url = StringField('URL')
    twitter_liste = StringField('twitter')
    facebook = StringField('facebook')

class SurveyResponseForm(FlaskForm):
    id = HiddenField('id')
    survey_id = HiddenField('survey_id')
    question_id = HiddenField('question_id')
    responder_id = HiddenField('responder_id')
    target_id = HiddenField('target_id')
    the_response = StringField('Réponse', widget=TextArea(), validators=[DataRequired()])
