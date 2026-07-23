from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'active': self.active
        }

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(15), default='Available', nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reservations = db.relationship('Reservation', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'type': self.type,
            'rate': self.rate,
            'status': self.status,
            'active': self.active
        }

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    guest_name = db.Column(db.String(50), nullable=False, index=True)
    checkin = db.Column(db.Date, nullable=False)
    checkout = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Booked', nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'res_id': self.res_id,
            'room_id': self.room_id,
            'guest_name': self.guest_name,
            'checkin': self.checkin.strftime('%Y-%m-%d') if self.checkin else None,
            'checkout': self.checkout.strftime('%Y-%m-%d') if self.checkout else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'active': self.active
        }

class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        }
