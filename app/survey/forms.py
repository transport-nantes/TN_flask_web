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
