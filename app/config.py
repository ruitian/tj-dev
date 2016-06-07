import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = 'you-will-never-guess'
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@127.0.0.1/tj'

config = {
    'development': DevelopmentConfig
}
