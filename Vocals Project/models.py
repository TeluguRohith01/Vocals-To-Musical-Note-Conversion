from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(150))
    is_verified = db.Column(db.Boolean, default=False)