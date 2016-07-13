import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'you-will-never-guess'
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_POSTS_PER_PAGE = 5
    CODE_FOLDER = BASE_DIR + '/code'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:tj-dev@127.0.0.1:13306/tj'
    REDIS_URL = 'redis://127.0.0.1:6379/0'


config = {
    'development': DevelopmentConfig
}
