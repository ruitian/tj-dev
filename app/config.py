import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'you-will-never-guess'
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_POSTS_PER_PAGE = 5
    CODE_FOLDER = BASE_DIR + '/code'
    HOST = '172.16.3.2'
    REGISTRY = '172.16.3.2:5000/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:tj-dev@deployment_mysql_1/tj'
    REDIS_URL = 'redis://deployment_redis_1/0'


config = {
    'development': DevelopmentConfig
}
