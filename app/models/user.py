# app/models/user.py

from flask_login import UserMixin
from app.extensions import db
from datetime import datetime


class User(UserMixin, db.Model):   # UserMixin provides correct Flask-Login integration
    __tablename__ = 'users'

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone        = db.Column(db.String(20))
    address      = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    orders  = db.relationship('Order',  back_populates='customer', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='customer', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email, password_hash, phone=None, address=None):
        self.username      = username
        self.email         = email
        self.password_hash = password_hash
        self.phone         = phone
        self.address       = address

    # UserMixin already provides correct implementations of:
    #   is_authenticated, is_active, is_anonymous, get_id
    # Only override if you need custom logic (e.g. banned accounts → is_active = False).
    # The original code defined them as plain methods, which Flask-Login ignores
    # because it accesses them as properties. UserMixin fixes this correctly.

    # # Flask-Login required methods
    # def is_authenticated(self):
    #     return True
    
    # def is_active(self):
    #     return True
    
    # def is_anonymous(self):
    #     return False
    
    # def get_id(self):
    #     return str(self.id)


    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'email':      self.email,
            'phone':      self.phone,
            'address':    self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
