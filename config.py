import os
class Config(object):
    SECRET_KEY=os.urandom(24).hex()
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:1232587@localhost/hms'
    SQLALCHEMY_TRACK_MODIFICATIONS = False