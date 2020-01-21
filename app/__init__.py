import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    try:
        # On linodes we expect to find our local config in /var/transport-nantes/.
        config_filename = "/var/p27/config_tn_schema.py"
        print("Trying {fn}".format(fn=config_filename))
        app.config.from_pyfile(config_filename)
    except FileNotFoundError:
        # On dev hosts, we expect to find local config locally.
        try:
            config_filename = "../config_local.py"
            print("Trying {fn}".format(fn=config_filename))
            app.config.from_pyfile(config_filename)
        except FileNotFoundError:
            print('No local config found.')
    except:
        print('Unexpected error on app.config.from_pyfile()')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.survey import bp as survey_bp
    app.register_blueprint(survey_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if app.debug or app.testing:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/transport_nantes.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Transport Nantes startup')

    return app

from app import models
