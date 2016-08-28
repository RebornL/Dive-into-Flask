class Config(object):
    SECRET_KEY='asdhjhjhaqlasdhh1231'

class ProdConfig(object):
    pass

class DevConfig(object):
    DEBUG = True
    SECRET_KEY='asdhjhjhaqlasdhh1231'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True