import logging
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask import current_app as app
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangeEmailForm
from app.models import now_in_microseconds, User
# from app.auth.email import send_password_reset_email
from secrets import token_urlsafe
from datetime import datetime, timedelta

@bp.route('/F/<tag>/<seed>/login', methods=['GET', 'POST'])
def login(tag, seed):
    """Offer to login the user.

    Login for us means send the user a mail with a token.  When the
    user presents the token back to us (say, by clicking the link), we
    login the user, because user has proven that they control their
    own email address and so are who they say they are.

    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index', tag=tag, seed=seed))
    form = LoginForm()
    if not form.validate_on_submit():
        # The failure message is provided if the user tries to
        # validate but fails.  It should explain why the failure.
        return render_template('auth/login.html', title='Vous identifier',
                               form=form, tag=tag, seed=seed,
                               message=request.args.get('message'))

    user = User.query.filter_by(email=form.email.data).one_or_none()
    if user is None:
        user = User()
        user.email = form.email.data
        # If validated is False and last_seen is too old (by some
        # operationally defined threshold), the user account is
        # subject to clean-up (deletion), since clearly nothing has
        # ever been done with it.
        user.validated = False
        user.last_seen = now_in_microseconds()

    # Should we remember the user after the session cookie expires?
    user.remember_me = form.remember_me.data
    # The 2015 python documentation of the secrets module
    # suggests that 32 bytes = 256 bits of randomness is good
    # for most purpoes.  So in 2020, let's guess that 40 bytes
    # = 320 bits of randomness is enough for us.
    user.validation_token = token_urlsafe(40)
    valid_seconds = 3600         # Seconds the user has to respond.
    now = int(datetime.utcnow().strftime('%s'))
    user.validation_expiry_seconds = now + valid_seconds
    db.session.add(user)
    db.session.commit()

    ## What I should do here is construct a login validation email
    ## to the user.  For the moment, I'll just emit the validation
    ## link to the log.  It's only on receiving that link that
    ## we'll call login_user().
    url = url_for('auth.validate_login', tag=tag, seed=seed,
                  user_id=user.id, token=user.validation_token)
    app.logger.info(url)
    return render_template('auth/thanks.html', title='Merci',
                           tag=tag, seed=seed)

@bp.route('/F/<tag>/<seed>/<user_id>/<token>/validate_login', methods=['GET', 'POST'])
def validate_login(tag, seed, user_id, token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index', tag=tag, seed=seed))
    user = User.query.filter_by(id=user_id).one_or_none()
    if user is None or token == '' or user.validation_token != token:
        # If the user doesn't exist, it makes no sense to log him in.
        # If the provided token is empty, it's not valid.
        # If the provided token doesn't match what we expect, it's not valid.
        message = """
        Votre demande ne peut pas aboutir.
        Merci de fournir une adresse mél valable ou de réessayer.
        """
        return redirect(url_for('auth.login', tag=tag, seed=seed,
                                message=message))
    now = int(datetime.utcnow().strftime('%s'))
    if user.validation_expiry_seconds < now:
        # Too late.  Offer to send a new token.  In exchange for
        # providing an email address again.  We could just
        # automatically send a new email, but we'd like to make it
        # difficult to spam people.
        message = """
        Votre demande est périmée.
        Merci de réessayer.
        """
        return redirect(url_for('auth.login', tag=tag, seed=seed,
                                message=message))
    user.validated = True
    user.last_seen = now_in_microseconds()
    user.validation_token = ''
    
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=user.remember_me, duration=timedelta(days=30))
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.index', tag=tag, seed=seed)
    return redirect(next_page)

@bp.route('/F/<tag>/<seed>/logout')
def logout(tag, seed):
    logout_user()
    return redirect(url_for('main.index', tag=tag, seed=seed))

"""
These functions should become "change email address".

The intended workflow is that the user requests to change email.  An
email is sent to _both_ addresses.  Each address gets two links: ok
and refuse.

If either refuses, the change is refused and the other address
notified of the refusal. The request then cancels.

If both accept, then the address is updated.  So we'll need a table to
track email address update requests.  Those requests should time out
after one hour.

As an anti-lockout measure, if the old address doesn't respond for 30
days, say, and the new address confirms, then we also validate the
change.

"""
"""
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            'Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
"""
