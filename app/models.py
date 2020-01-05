from app import db
import time

def now_in_microseconds():
    """Return the current time in microseconds since the epoch.
    """
    return time.time() * 1000 * 1000

class UserJourneyStep(db.Model):
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

