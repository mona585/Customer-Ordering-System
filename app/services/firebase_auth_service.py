# app/services/firebase_auth_service.py
"""Firebase Authentication service for server-side operations"""

import requests
from firebase_admin import auth as firebase_auth
from app.services.base_service import BaseService, ServiceResult


class FirebaseAuthService(BaseService):
    """Handles Firebase Authentication operations via REST API and Admin SDK"""

    FIREBASE_REST_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

    @staticmethod
    def sign_up_with_email_password(email, password, display_name=None):
        """Create a new Firebase user using Admin SDK"""
        try:
            user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            return ServiceResult.ok(data={
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name
            }, message="Account created successfully")
        except Exception as e:
            return ServiceResult.fail(str(e))

    @staticmethod
    def sign_in_with_email_password(email, password, api_key):
        """Sign in via Firebase REST API (returns tokens)"""
        url = f"{FirebaseAuthService.FIREBASE_REST_URL}:signInWithPassword"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            response = requests.post(url, params={"key": api_key}, json=payload)
            data = response.json()

            if 'error' in data:
                return ServiceResult.fail(data['error']['message'])

            return ServiceResult.ok(data={
                'id_token': data['idToken'],
                'refresh_token': data['refreshToken'],
                'local_id': data['localId'],
                'email': data['email']
            })
        except Exception as e:
            return ServiceResult.fail(f"Authentication failed: {str(e)}")

    @staticmethod
    def verify_id_token(id_token):
        """Verify Firebase ID token and return user info"""
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            return ServiceResult.ok(data=decoded)
        except Exception as e:
            return ServiceResult.fail(f"Invalid token: {str(e)}")

    @staticmethod
    def get_user_by_uid(uid):
        """Get Firebase user by UID"""
        try:
            user = firebase_auth.get_user(uid)
            return ServiceResult.ok(data={
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'phone_number': user.phone_number,
                'email_verified': user.email_verified
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

    @staticmethod
    def send_password_reset_email(email, api_key):
        """Send password reset email via Firebase"""
        url = f"{FirebaseAuthService.FIREBASE_REST_URL}:sendOobCode"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        try:
            response = requests.post(url, params={"key": api_key}, json=payload)
            data = response.json()

            if 'error' in data:
                return ServiceResult.fail(data['error']['message'])

            return ServiceResult.ok(message="Password reset email sent")
        except Exception as e:
            return ServiceResult.fail(str(e))
