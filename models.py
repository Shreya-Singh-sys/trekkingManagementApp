from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'staff', 'user'
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Approved') # 'Approved', 'Pending', 'Blacklisted'
    
    # Relationships
    bookings = db.relationship('Booking', backref='trekker', lazy=True)
    assigned_treks = db.relationship('Trek', backref='assigned_staff', lazy=True)

class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) # 'Easy', 'Moderate', 'Hard'
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Open', 'Closed', 'Completed'
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    
    bookings = db.relationship('Booking', backref='trek', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))
    status = db.Column(db.String(20), default='Booked') # 'Booked', 'Cancelled', 'Completed'

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Seed Pre-existing Admin Superuser account programmatically if absent
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            admin_user = User(
                username='admin',
                password='adminpassword', # Clear text setup as specified without extra libraries
                role='admin',
                name='System Administrator',
                contact='1234567890',
                status='Approved'
            )
            db.session.add(admin_user)
            db.session.commit()