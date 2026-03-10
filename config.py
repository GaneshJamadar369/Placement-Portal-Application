import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY =os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'
    SQLALCHEMY_TRACK_MODIFICATION =False
    WTF_CSRF_ENABLED = True

