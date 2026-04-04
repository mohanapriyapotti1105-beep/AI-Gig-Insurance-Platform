# """
# Database Models for Trust Insurance System
# """
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# import json

# db = SQLAlchemy()


# class User(db.Model):
#     """User model with behavioral tracking"""
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     name = db.Column(db.String(120), nullable=False)
#     password_hash = db.Column(db.String(255), nullable=False)
    
#     # Device & Security
#     device_fingerprint = db.Column(db.String(255), nullable=True)
#     is_verified = db.Column(db.Boolean, default=False)
    
#     # Behavioral Scoring (0-100)
#     behavioral_score = db.Column(db.Float, default=50.0)
#     last_location_lat = db.Column(db.Float, nullable=True)
#     last_location_lon = db.Column(db.Float, nullable=True)
#     last_claim_timestamp = db.Column(db.DateTime, nullable=True)
    
#     # Account Info
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     claims = db.relationship('Claim', backref='user', lazy=True, cascade='all, delete-orphan')
#     movement_history = db.relationship('MovementHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
#     def set_password(self, password):
#         """Hash and set password"""
#         self.password_hash = generate_password_hash(password)
    
#     def check_password(self, password):
#         """Verify password"""
#         return check_password_hash(self.password_hash, password)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'email': self.email,
#             'name': self.name,
#             'behavioral_score': self.behavioral_score,
#             'is_verified': self.is_verified,
#             'created_at': self.created_at.isoformat()
#         }


# class Claim(db.Model):
#     """Insurance claim with full audit trail"""
#     __tablename__ = 'claims'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
#     # Location Data
#     city = db.Column(db.String(120), nullable=False)
#     country = db.Column(db.String(120), nullable=False)
#     latitude = db.Column(db.Float, nullable=True)
#     longitude = db.Column(db.Float, nullable=True)
    
#     # Environmental Data
#     weather = db.Column(db.String(50), nullable=False)
#     pollution_index = db.Column(db.Float, nullable=True)  # AQI (0-500+)
#     temperature = db.Column(db.Float, nullable=True)
#     humidity = db.Column(db.Float, nullable=True)
#     traffic = db.Column(db.String(50), nullable=False)
    
#     # Trust & Risk Assessment
#     trust_score = db.Column(db.Integer, nullable=False)  # 0-100
#     risk_level = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH
#     risk_factors = db.Column(db.JSON, nullable=True)  # Store detailed risk information
    
#     # Behavioral Analysis
#     speed_anomaly_detected = db.Column(db.Boolean, default=False)
#     time_jump_detected = db.Column(db.Boolean, default=False)
#     fraud_ring_score = db.Column(db.Float, default=0.0)  # Likelihood of coordinated fraud
    
#     # Claim Status
#     status = db.Column(db.String(20), default='PENDING')  # APPROVED, PENDING, REJECTED, UNDER_REVIEW
#     approval_reason = db.Column(db.String(255), nullable=True)
    
#     # Timestamps
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'city': self.city,
#             'country': self.country,
#             'weather': self.weather,
#             'pollution_index': self.pollution_index,
#             'traffic': self.traffic,
#             'trust_score': self.trust_score,
#             'risk_level': self.risk_level,
#             'status': self.status,
#             'speed_anomaly_detected': self.speed_anomaly_detected,
#             'time_jump_detected': self.time_jump_detected,
#             'created_at': self.created_at.isoformat()
#         }


# class MovementHistory(db.Model):
#     """Track user movement for behavioral analysis"""
#     __tablename__ = 'movement_history'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
#     # Location
#     latitude = db.Column(db.Float, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)
#     city = db.Column(db.String(120), nullable=True)
    
#     # Movement Analysis
#     calculated_speed_kmh = db.Column(db.Float, nullable=True)  # km/h from last location
#     time_since_last_location = db.Column(db.Integer, nullable=True)  # seconds
#     distance_from_last_km = db.Column(db.Float, nullable=True)  # km
    
#     # Detection
#     is_anomalous = db.Column(db.Boolean, default=False)
#     anomaly_reason = db.Column(db.String(255), nullable=True)
    
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'latitude': self.latitude,
#             'longitude': self.longitude,
#             'city': self.city,
#             'calculated_speed_kmh': self.calculated_speed_kmh,
#             'is_anomalous': self.is_anomalous,
#             'timestamp': self.timestamp.isoformat()
#         }


# class FraudPattern(db.Model):
#     """Track coordinated fraud patterns"""
#     __tablename__ = 'fraud_patterns'
    
#     id = db.Column(db.Integer, primary_key=True)
    
#     # Suspected Fraud Ring (multiple users, same location, same time)
#     users_involved = db.Column(db.JSON, nullable=False)  # List of user IDs
#     city = db.Column(db.String(120), nullable=False)
#     timestamp_window = db.Column(db.DateTime, nullable=False)
    
#     # Pattern Details
#     claim_count = db.Column(db.Integer, default=1)
#     confidence_score = db.Column(db.Float, default=0.0)  # 0-1
#     status = db.Column(db.String(20), default='DETECTED')  # DETECTED, INVESTIGATING, CONFIRMED
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
