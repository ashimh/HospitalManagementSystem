import os

class Config(object):
    SECRET_KY =  os.environ.get('SECRET_KEY') or "secret_string"
    SQLALCHEMY_TRACK_MODIFICATIONS = "false"
    #SQLALCHEMY_DATABASE_URI = "mysql://root:password@localhost/hospital_management_system"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')