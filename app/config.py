import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    PUBLIC_FOLDER = os.path.join(UPLOAD_FOLDER, 'public')  # Directory for publicly accessible files
    PUBLIC_URL = '/public'  # URL path for accessing public files
