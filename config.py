class Config(object):
    pass

class ProdConfig(object):
    pass

class DevConfig(object):
    debug = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True