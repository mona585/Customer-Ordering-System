# firebase_config.py
import os
import json
import firebase_admin
from firebase_admin import credentials

firebase_app = None

firebase_json = os.environ.get('FIREBASE_CREDENTIALS')

if firebase_json:
    if firebase_json.strip().startswith('{'):
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate(firebase_json)
    firebase_app = firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully")
else:
    print("WARNING: Firebase credentials not found")
