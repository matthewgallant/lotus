import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LOTUS_ENVIRONMENT = os.environ.get('LOTUS_ENVIRONMENT')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if LOTUS_ENVIRONMENT == 'prod':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI_PROD')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI_DEV')
