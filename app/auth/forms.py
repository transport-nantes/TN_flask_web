from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Mél', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

    ## These two functions are just wrong.  Instead, if the user
    ## registers with an email we already know, we should say "hey,
    ## you already have an account, we've sent you a validation
    ## email".  And then we're done, let them login by clicking the
    ## link.
    def validate_username(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ChangeEmailForm(FlaskForm):
    new_email = StringField('New email', validators=[DataRequired(), Email()])
    submit = SubmitField('Change Email')
