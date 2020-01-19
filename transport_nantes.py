from app import create_app, db, cli
from app.models import UserJourneyStep
from app.models import User
from app.models import Survey, SurveyQuestion, SurveyResponder, SurveyResponse

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'user': User,
            'UserJourneyStep': UserJourneyStep,
            'Survey': Survey,
            'SurveyQuestion': SurveyQuestion,
            'SurveyResponder': SurveyResponder,
            'SurveyResponse': SurveyResponse,
    }
