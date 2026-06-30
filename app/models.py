import token

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime
from itsdangerous import URLSafeSerializer
from flask import app

import jwt
from time import time

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(10), nullable=False)
    id_number = db.Column(db.String(13), nullable=False)
    coins = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), default='user')
    password_hash = db.Column(db.String(500), nullable=False)


    bets = db.relationship('Bet',backref = 'user',lazy = True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self,expires_in=600):

        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, 
                          app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Spin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(20), nullable=False)
    profits = db.Column(db.Float(20))
    created = db.Column(db.DateTime, default = datetime.utcnow)


    def __repr__(self):
        return f'<Spin {self.id}>'
    
class Bet(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    spin_id = db.Column(db.Integer,db.ForeignKey('spin.id'),nullable = False)
    choice = db.Column(db.String(10),nullable = False)
    amount = db.Column(db.Integer, nullable = False)

    spin = db.relationship('Spin',foreign_keys = [spin_id])

    def __repr__(self):
        return f'<Bet User:{self.user_id} Spin:{self.spin_id} Amt:{self.amount}>'
