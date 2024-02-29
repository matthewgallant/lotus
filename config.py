import os

class Config:
    LOTUS_ENVIRONMENT = os.environ.get('LOTUS_ENVIRONMENT')
    if LOTUS_ENVIRONMENT == 'prod':
        SQLALCHEMY_DATABASE_URI = "sqlite:////database/collection.db"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
