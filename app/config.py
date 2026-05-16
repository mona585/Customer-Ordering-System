# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-key'

    FIREBASE_WEB_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY') or ''
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS') or './firebase-service-account.json'

    MIN_ORDER_AMOUNT = 1.00
    MAX_ORDER_AMOUNT = 10000.00
    MAX_ITEMS_PER_ORDER = 100
