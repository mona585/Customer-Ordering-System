# app/models/user.py

from flask_login import UserMixin
from app.extensions import db
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    firebase_uid  = db.Column(db.String(128), unique=True, nullable=True)  # NEW: Firebase UID
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # Now nullable - Firebase handles passwords
    phone         = db.Column(db.String(20))
    address       = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    orders  = db.relationship('Order',  back_populates='customer', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='customer', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email, firebase_uid=None, password_hash=None, phone=None, address=None):
        self.username      = username
        self.email         = email
        self.firebase_uid  = firebase_uid  # NEW
        self.password_hash = password_hash
        self.phone         = phone
        self.address       = address

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id':          self.id,
            'firebase_uid': self.firebase_uid,
            'username':    self.username,
            'email':       self.email,
            'phone':       self.phone,
            'address':     self.address,
            'created_at':  self.created_at.isoformat() if self.created_at else None
        }
