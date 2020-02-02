from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Survey


class SurveyForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom du sondage', validators=[DataRequired()])
    description = StringField('Description du sondage')

