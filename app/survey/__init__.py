from flask import Blueprint

bp = Blueprint('survey', __name__)

from app.survey import routes
from app.survey import survey_v1
