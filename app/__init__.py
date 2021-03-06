# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_oauthlib.client import OAuth
from flask_redis import Redis
from flask_moment import Moment

from .config import config

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()


app = Flask(__name__)
login_manager = LoginManager()
db = SQLAlchemy()
socketio = SocketIO()
oauth = OAuth(app)
redis = Redis()
moment = Moment()

with app.app_context():

    config_name = os.getenv('FLASK_CONFIG') or 'development'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.app = app
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'
    login_manager.login_message = u'请先登陆系统,若遗忘密码，请联系管理员'
    login_manager.login_message_category = 'warning'

    socketio.init_app(app, async_mode=async_mode)
    redis.init_app(app)
    moment.init_app(app)

from .views import *  # noqa
from .models import *  # noqa
