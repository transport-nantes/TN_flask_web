from app import db, login
import time
from flask_login import UserMixin

def now_in_seconds():
    """Return the current time in seconds since the epoch.
    """
    return time.time()

def now_in_microseconds():
    """Return the current time in microseconds since the epoch.
    """
    return time.time() * 1000 * 1000

#### User Journeys ###################################################

class UserJourneyStep(db.Model):
    """Represent a single user visit.

    Represent one step in a users full journey through the site.

    """
    # __table_args__ = {"schema": "tn_schema"}

    # For the database, we want a guaranteed unique PK.
    id = db.Column(db.Integer, primary_key=True)
    # We will use the pair (timestamp_microseconds, ip_hash) as our
    # principle index.  It is theoretically possible that it is not
    # unique, however.
    timestamp_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)
    ip_hash = db.Column(db.String())

    # Indicate if this visit represents a site entry.
    # Note that we can't really compute an is_exit, because many clicks
    # that result in the user leaving the site do so only temporarily in
    # another window.  Also, exit isn't particularly interesting, whereas
    # entries are particularly pertinent.
    is_entry = db.Column(db.Boolean())

    # And then other fields of interest to us.
    referrer = db.Column(db.String())
    # This is the canonical host component of the REFERER.
    referrer_host = db.Column(db.String())

    # If we are the referring site, this is the visitor journey tag
    # (e.g., D/<tag>/), if it exists.
    tag = db.Column(db.String())
    this_page_url = db.Column(db.String())
    this_page_canonical = db.Column(db.String())

    # Geographic information.  We take pains not to store anything
    # that is GDPR-sensitive.
    geo_country = db.Column(db.String())
    geo_region = db.Column(db.String())
    geo_city = db.Column(db.String())

    # If we can divine the user's screen size, we'd like to note this
    # in case some screens have problems with the site.
    screen_width = db.Column(db.Integer())
    screen_height = db.Column(db.Integer())
    screen_resolution = db.Column(db.Integer())
    # Similarly, we record browser information in case some browsers
    # lead to different behaviour.
    ua_string = db.Column(db.String())
    ua_browser = db.Column(db.String())
    ua_language = db.Column(db.String())
    ua_platform = db.Column(db.String())
    ua_version = db.Column(db.String())

    def __repr__(self):
        return '<[{tag}]/[{ip}] {microsec}/{city}>'.format(
            tag=self.tag, ip=self.ip_hash,
            microsec=self.timestamp_microseconds, city=self.city)

#### Users ###########################################################

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    # Set to true once user has responded to a validation token.
    # Unvalidated user entries may be deleted after enough time has
    # passed without validation.  (We only set last_seen the first
    # time the email is noted and thereafter only on validation.)
    validated = db.Column(db.Boolean)
    last_seen = db.Column(db.Integer, default=now_in_seconds)
    # We reset remember_me each time the user has to login.  This
    # value probably won't matter except to transmit the form value to
    # the login_user call.
    remember_me = db.Column(db.Boolean)
    # When user identifies her/himself, we assign a token and an
    # expiry time, then send the token to the user's email.  If the
    # user then presents the token before the expiration time (in
    # seconds since the epoch), we login the user.
    validation_token = db.Column(db.String(120))
    validation_expiry_seconds = db.Column(db.Integer)
    ## We'll want pointers to authorised activities.
    ##   Automatically in case of gifts.
    ##   Maybe user is authorised to modify survey results.
    # posts = db.relationship('Post', backref='author', lazy='dynamic')
    # followed = db.relationship(
    #     'User', secondary=followers,
    #     primaryjoin=(followers.c.follower_id == id),
    #     secondaryjoin=(followers.c.followed_id == id),
    #     backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    #def set_password(self, password):
    #    self.password_hash = generate_password_hash(password)

    #def check_password(self, password):
    #    return check_password_hash(self.password_hash, password)

    def get_change_email_token(self, expires_in=600):
        return jwt.encode(
            {'change_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_change_email_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#### Surveys #########################################################

class Survey(db.Model):
    """Represent a survey.

    This does not represent the questions (SurveyQuestions) or
    anyone's responses.

    """
    # __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_seconds = db.Column(db.Integer, default=now_in_seconds)
    updated_seconds = db.Column(db.Integer, default=now_in_seconds)
    # A human-presentable name of the survey
    name = db.Column(db.String, unique=True)
    # More information about the survey.  For humans.
    description = db.Column(db.String)
    questions = db.relationship('SurveyQuestion', backref='survey', lazy=True)

class SurveyQuestion(db.Model):
    """Represent a set of questions (a survey).

    Generally a Survey contains several SurveyQuestion's.
    This does not represent anyone's responses.

    """
    # __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_seconds = db.Column(db.Integer, default=now_in_seconds)
    updated_seconds = db.Column(db.Integer, default=now_in_seconds)

    survey_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)
    # Question numbers are strings because we might have "3a" and
    # "3b", for example.
    question_number = db.Column(db.String)
    # For a given survey, the questions will be sorted in ascending
    # order by sort_index.  This primarily avoids having to use "09"
    # as soon as question "10" is added.
    sort_index = db.Column(db.Integer)
    question_title = db.Column(db.String)
    question_text = db.Column(db.String)

class SurveyTarget(db.Model):
    """A political list or party capable of being responsible for responses.

    The actual responders are represented by SurveyResponder's.  This
    table merely represents the entities for which the responders
    respond.  That is, a SurveyTarget may have a response to a
    SurveyQuestion, but it is the SurveyResponder that actually
    provides the response.

    """
    id = db.Column(db.Integer, primary_key=True)
    created_seconds = db.Column(db.Integer, default=now_in_seconds)
    updated_seconds = db.Column(db.Integer, default=now_in_seconds)

    # What survey does this target have the ability to respond.
    survey_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)

    # In a self-service context, we'll use validated to indicate that
    # we've confirmed that the person is authorised to reply for the
    # list.
    validated = db.Column(db.Boolean)
    commune = db.Column(db.String)
    liste = db.Column(db.String)
    tete_de_liste = db.Column(db.String)

    url = db.Column(db.String)
    twitter_liste = db.Column(db.String)
    twitter_tete_de_liste = db.Column(db.String)
    facebook = db.Column(db.String)

    responses = db.relationship('SurveyResponse', backref='responder', lazy=True)

class SurveyResponder(db.Model):
    """Represent someone who might respond to a survey or edit its results.

    We use this for tracking people who might respond to the survey.
    People may appear in this table more than once if they are
    authorised to respond to more than one survey or for more than one
    party.  Over time, it is natural to be authorised for multiple
    surveys of which some are closed.  Once a survey is closed, no
    further edits are permitted.

    """
    # __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_seconds = db.Column(db.Integer, default=now_in_seconds)
    updated_seconds = db.Column(db.Integer, default=now_in_seconds)
    # People are generally authorised only to respond for one
    # party/list and for one survey.  If they wish to respond to
    # another survey, they'll need to be revalidated.
    survey_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)
    # The target_id should not be null, but we need to transition to that.
    target_id = db.Column(db.Integer, db.ForeignKey(SurveyTarget.id), nullable=True)

    # In a self-service context, we'll use validated to indicate that
    # we've confirmed that the person is authorised to reply for the
    # list.
    validated = db.Column(db.Boolean)
    ################ These fields are obsolete and may be deleted
    ################ once transferred to SurveyTarget.
    commune = db.Column(db.String)
    liste = db.Column(db.String)
    parti_principal = db.Column(db.String)
    parti_rattaches = db.Column(db.String)
    tete_de_liste = db.Column(db.String)
    sortant = db.Column(db.Boolean)
    ################ End obsolete fields ################

    # The email_person is the specific email of the person who is
    # responding, if we know it.  When we provide self-service, the
    # intent is that email_person is the mail that will be asked to
    # verify that a contribution or change is legimiate (i.e., used
    # for login/authentication).
    email_person = db.Column(db.String)

    ################ Remaining fields are obsolete and may be deleted
    ################ once transferred to SurveyTarget.
    email_liste = db.Column(db.String)
    url = db.Column(db.String)
    twitter_liste = db.Column(db.String)
    twitter_candidat = db.Column(db.String)
    facebook = db.Column(db.String)

    ################ End obsolete fields ################

class SurveyResponse(db.Model):
    """Represent candidate/party responses to survey questions.
    """
    # __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_seconds = db.Column(db.Integer, default=now_in_seconds)
    updated_seconds = db.Column(db.Integer, default=now_in_seconds)

    survey_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)
    survey_question_id = db.Column(db.Integer, db.ForeignKey(SurveyQuestion.id), nullable=False)
    # Survey_responder_id is nullable because we haven't implemented
    # making responders yet.
    survey_responder_id = db.Column(db.Integer, db.ForeignKey(SurveyResponder.id), nullable=True)
    # survey_target_id is nullable due to history.  We have to create
    # the column before we can set the value.  But, in principle, it
    # should never be null.
    survey_target_id = db.Column(db.Integer, db.ForeignKey(SurveyTarget.id), nullable=True)

    survey_question_response = db.Column(db.String)
