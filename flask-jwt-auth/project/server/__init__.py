# project/server/__init__.py

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mongoengine import MongoEngine

app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)

app.config['MONGODB_HOST'] = "mongodb+srv://<mongoAccountName>:<password>@cluster0.jbcfc.mongodb.net/<database_name>?retryWrites=true&w=majority"

db = MongoEngine(app)

from project.server.auth.views import auth_blueprint
from project.server.infrastructure.views import infra_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(infra_blueprint)
