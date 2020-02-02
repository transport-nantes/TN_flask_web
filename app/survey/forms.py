from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Survey


class SurveyForm(FlaskForm):
    name = StringField('Nom du sondage', validators=[DataRequired()])
    description = StringField('Description du sondage')
    submit = SubmitField('Login')

