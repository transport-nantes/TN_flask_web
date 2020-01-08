from app import db
import time

def now_in_microseconds():
    """Return the current time in microseconds since the epoch.
    """
    return time.time() * 1000 * 1000

class UserJourneyStep(db.Model):
    """Represent a single user visit.

    Represent one step in a users full journey through the site.

    """
    __table_args__ = {"schema": "tn_schema"}

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

class Survey(db.Model):
    """Represent a survey.

    This does not represent the questions (SurveyQuestions) or
    anyone's responses.

    """
    __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    # A human-presentable name of the survey
    name = db.Column(db.String)
    # More information about the survey.  For humans.
    description = db.Column(db.String)
    questions = db.relationship('SurveyQuestion', backref='survey', lazy=True)

class SurveyQuestion(db.Model):
    """Represent a set of questions (a survey).

    This does not represent anyone's responses.

    """
    __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)
    updated_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)

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

class SurveyResponder(db.Model):
    """Represent someone or something that might respond to a survey.

    We use this for tracking people and parties who might respond to
    the survey.  This is not fully normalised because people and lists
    join together and split apart.  So this slight denormalisation
    seemed easier to manage.

    """
    __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)
    updated_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)
    # People are generally authorised only to respond for one
    # party/list and for one survey.  If they wish to respond to
    # another survey, they'll need to be revalidated.
    survey_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)

    # In a self-service context, we'll use validated to indicate that
    # we've confirmed that the person is authorised to reply for the
    # list.
    validated = db.Column(db.Boolean)
    commune = db.Column(db.String)
    liste = db.Column(db.String)
    parti_principal = db.Column(db.String)
    parti_rattaches = db.Column(db.String)
    tete_de_liste = db.Column(db.String)
    sortant = db.Column(db.Boolean)

    # The email_liste is the official email for the list or party, if
    # we know it.  The email_person is the specific email of the
    # person who is responding, if we know it.  When we provide
    # self-service, the intent is that email_person is the mail that
    # will be asked to verify that a contribution or change is
    # legimiate (i.e., used for login/authentication).
    email_liste = db.Column(db.String)
    email_person = db.Column(db.String)

    url = db.Column(db.String)
    twitter_liste = db.Column(db.String)
    twitter_candidat = db.Column(db.String)
    facebook = db.Column(db.String)

class SurveyResponse(db.Model):
    """Represent candidate/party responses to survey questions.
    """
    __table_args__ = {"schema": "tn_schema"}

    id = db.Column(db.Integer, primary_key=True)
    created_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)
    updated_microseconds = db.Column(db.BigInteger, default=now_in_microseconds)

    survey_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)
    survey_question_id = db.Column(db.Integer, db.ForeignKey(SurveyQuestion.id), nullable=False)
    survey_responder_id = db.Column(db.Integer, db.ForeignKey(SurveyResponder.id), nullable=False)

    survey_question_response = db.Column(db.String)
