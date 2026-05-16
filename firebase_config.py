# firebase_config.py
import os
from firebase_admin import credentials, initialize_app

cred_path = os.environ.get('FIREBASE_CREDENTIALS') or 'firebase-service-account.json'

if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_app = initialize_app(cred)
    print("Firebase initialized successfully")
else:
    print(f"WARNING: Firebase credentials not found at: {cred_path}")
    firebase_app = None
