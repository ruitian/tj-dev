# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import config

app = Flask(__name__)
login_manager = LoginManager()
db = SQLAlchemy()

with app.app_context():

    config_name = os.getenv('FLASK_CONFIG') or 'development'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.app = app
    db.init_app(app)

    login_manager.setup_app(app)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'
    login_manager.login_message = u'请先登陆系统,若遗忘密码，请联系管理员'

from .views import *  # noqa
from .models import *  # noqa
