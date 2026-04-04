# from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
# import requests
# import random
# from datetime import datetime, timedelta
# from functools import wraps

# # Import models and analytics
# from models import db, User, Claim, MovementHistory, FraudPattern
# from analytics import BehavioralAnalyzer, RiskClassifier, PollutionIndexFetcher

# # ⚙️ Flask App Configuration
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trust_insurance.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = "trust-insurance-secret-key-change-in-production"
# app.permanent_session_lifetime = timedelta(hours=24)

# # Initialize database
# db.init_app(app)

# # 🔑 API Keys
# OPENWEATHER_API_KEY = "f7b4a3d88337ad2894d3aefc138bf5d0"

# # ✅ Create database tables
# with app.app_context():
#     db.create_all()


# # 🌦️ Fetch Weather & Pollution Data
# def get_weather_and_pollution(city, country):
#     """
#     Fetch both weather and AQI (Air Quality Index) data
#     Returns: (weather, temp, humidity, pollution_index, aqi_emoji)
#     """
#     try:
#         url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={OPENWEATHER_API_KEY}&units=metric"
#         response = requests.get(url, timeout=5).json()
        
#         if response.get("cod") != 200:
#             return "Unknown", None, None, None, "Unknown"
        
#         weather = response["weather"][0]["main"]
#         temp = response["main"]["temp"]
#         humidity = response["main"]["humidity"]
        
#         # Get AQI (using a simpler approach - in production, use dedicated AQI API)
#         if weather in ["Thunderstorm", "Tornado"]:
#             aqi = random.randint(150, 250)  # Bad to very bad
#         elif weather in ["Rain", "Drizzle"]:
#             aqi = random.randint(80, 150)  # Moderate to bad
#         elif weather in ["Mist", "Smoke", "Haze"]:
#             aqi = random.randint(100, 200)  # Bad air quality
#         else:
#             aqi = random.randint(20, 80)  # Good to moderate
        
#         aqi_category, aqi_emoji = PollutionIndexFetcher.get_aqi_category(aqi)
        
#         return weather, temp, humidity, aqi, aqi_emoji
        
#     except Exception as e:
#         print(f"Weather API Error: {e}")
#         return "Unknown", None, None, None, "Unknown"


# # 🚗 Get Traffic Conditions
# def get_traffic():
#     """Simulate realistic traffic patterns"""
#     return random.choice(["Low", "Moderate", "Heavy"])


# # 🧠 Calculate Trust Score (Enhanced with Pollution)
# def calculate_trust_score(weather, pollution_index, traffic, behavioral_score, activity=None, gps_variation=None):
#     """
#     Calculate comprehensive trust score (0-100)
#     Incorporates: Weather, Pollution, Traffic, User Behavior, Activity
#     """
#     score = 50
    
#     # Weather Impact (-30 to +25)
#     if weather in ["Thunderstorm", "Tornado"]:
#         score += 25  # Major disruption
#     elif weather in ["Rain", "Drizzle"]:
#         score += 20
#     elif weather in ["Snow", "Sleet"]:
#         score += 18
#     else:
#         score += 5  # Clear weather - less impact
    
#     # Pollution Impact (Bonus for high pollution - valid disruption)
#     pollution_boost = PollutionIndexFetcher.get_aqi_impact(pollution_index)
#     score += pollution_boost
    
#     # Traffic Impact (High traffic = more disruption = bonus)
#     if traffic == "Heavy":
#         score += 15
#     elif traffic == "Moderate":
#         score += 8
    
#     # User Behavioral Score (0-100 impact on -20 to +10)
#     if behavioral_score > 80:
#         score += 10  # Trustworthy user
#     elif behavioral_score < 30:
#         score -= 15  # Suspicious history
    
#     # Activity variations (if provided)
#     if activity:
#         if activity >= 7:
#             score += 10
#         else:
#             score += 3
    
#     if gps_variation and gps_variation <= 8:
#         score += 10
    
#     # Clamp to 0-100
#     return max(0, min(100, score))


# # 🔐 Login Required Decorator
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('auth_page'))
#         return f(*args, **kwargs)
#     return decorated_function


# # 📱 Authentication Routes
# @app.route("/auth", methods=["GET", "POST"])
# def auth_page():
#     if request.method == "POST":
#         action = request.form.get("action")

#         if action == "login":
#             email = request.form.get("email")
#             password = request.form.get("password")

#             user = User.query.filter_by(email=email).first()
            
#             if user and user.check_password(password):
#                 session["user_id"] = user.id
#                 session["user_email"] = user.email
#                 session["user_name"] = user.name
#                 session.permanent = True
#                 return redirect(url_for("index"))
#             else:
#                 flash("Invalid email or password", "error")

#         elif action == "signup":
#             name = request.form.get("name")
#             email = request.form.get("email")
#             password = request.form.get("password")
#             confirm_password = request.form.get("confirm_password")

#             if User.query.filter_by(email=email).first():
#                 flash("Email already registered", "error")
#             elif password != confirm_password:
#                 flash("Passwords do not match", "error")
#             elif len(password) < 6:
#                 flash("Password must be at least 6 characters", "error")
#             else:
#                 new_user = User(email=email, name=name)
#                 new_user.set_password(password)
#                 db.session.add(new_user)
#                 db.session.commit()
#                 flash("Account created! You can now login.", "success")

#     return render_template("login.html")


# # 📤 Logout Route
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("auth_page"))


# # 🚀 Main Insurance Claim Route (Protected)
# @app.route("/", methods=["GET", "POST"])
# @login_required
# def index():
#     result = None
#     recent_claims = []

#     # Get user from database
#     user = User.query.get(session.get('user_id'))
    
#     if request.method == "POST":
#         city = request.form.get("city")
#         country = request.form.get("country")
#         latitude = request.form.get("latitude", 0.0, type=float)
#         longitude = request.form.get("longitude", 0.0, type=float)

#         # 🌦️ Fetch environmental data
#         weather, temp, humidity, pollution_index, aqi_emoji = get_weather_and_pollution(city, country)
#         traffic = get_traffic()
        
#         # Simulate activity and GPS variation (in production, from device)
#         activity = random.randint(3, 10)
#         gps_variation = random.randint(1, 15)
        
#         # 🧠 Calculate base trust score
#         base_trust_score = calculate_trust_score(
#             weather, pollution_index, traffic, 
#             user.behavioral_score, activity, gps_variation
#         )
        
#         # 🚨 Behavioral Anomaly Detection
#         speed_anomaly, calculated_speed, anomaly_reason = BehavioralAnalyzer.detect_speed_anomaly(
#             user, latitude, longitude, datetime.utcnow()
#         )
        
#         # 🎭 Coordinated Fraud Detection
#         fraud_ring_score = BehavioralAnalyzer.detect_coordinated_fraud(city, country, datetime.utcnow(), user.id)
        
#         # 📊 Build Risk Factors
#         risk_factors = {
#             "speed_anomaly": speed_anomaly,
#             "time_jump": False,
#             "fraud_ring_detected": fraud_ring_score > 0.5,
#             "device_suspicious": False,
#             "low_behavioral_score": user.behavioral_score < 40
#         }
        
#         # Apply anomaly penalties
#         if speed_anomaly:
#             base_trust_score -= 20
#         if fraud_ring_score > 0.5:
#             base_trust_score -= 15
        
#         base_trust_score = max(0, min(100, base_trust_score))
        
#         # 🎯 Risk Classification
#         risk_level, auto_approve, risk_reason = RiskClassifier.classify_claim(
#             base_trust_score, user.behavioral_score, risk_factors
#         )
        
#         # ✅ Determine Status
#         if auto_approve:
#             status = "APPROVED ✅"
#             approval_status = "APPROVED"
#         elif risk_level == "MEDIUM":
#             status = "UNDER REVIEW ⚠️"
#             approval_status = "PENDING"
#         else:
#             status = "REJECTED ❌"
#             approval_status = "REJECTED"
        
#         # 💾 Save claim to database
#         claim = Claim(
#             user_id=user.id,
#             city=city,
#             country=country,
#             latitude=latitude,
#             longitude=longitude,
#             weather=weather,
#             pollution_index=pollution_index,
#             temperature=temp,
#             humidity=humidity,
#             traffic=traffic,
#             trust_score=int(base_trust_score),
#             risk_level=risk_level,
#             risk_factors=risk_factors,
#             speed_anomaly_detected=speed_anomaly,
#             fraud_ring_score=fraud_ring_score,
#             status=approval_status,
#             approval_reason=risk_reason
#         )
#         db.session.add(claim)
        
#         # Update user location and behavioral scoring
#         user.last_location_lat = latitude
#         user.last_location_lon = longitude
#         user.last_claim_timestamp = datetime.utcnow()
#         BehavioralAnalyzer.update_behavioral_score(user)
        
#         db.session.commit()
        
#         # Prepare result data
#         result = {
#             "claim_id": claim.id,
#             "weather": weather,
#             "pollution_index": pollution_index,
#             "aqi_emoji": aqi_emoji,
#             "temperature": temp,
#             "humidity": humidity,
#             "traffic": traffic,
#             "trust_score": int(base_trust_score),
#             "behavioral_score": user.behavioral_score,
#             "risk_level": risk_level,
#             "status": status,
#             "reason": risk_reason,
#             "activity": activity,
#             "gps": gps_variation,
#             "speed_anomaly": speed_anomaly,
#             "speed_kmh": calculated_speed,
#             "fraud_ring_likelihood": f"{fraud_ring_score * 100:.1f}%"
#         }
    
#     # Fetch recent claims for display
#     recent_claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.created_at.desc()).limit(5).all()

#     return render_template(
#         "index.html",
#         result=result,
#         user_name=user.name,
#         recent_claims=recent_claims,
#         behavioral_score=user.behavioral_score
#     )


# # 📊 Claims History Route
# @app.route("/claims-history")
# @login_required
# def claims_history():
#     user = User.query.get(session.get('user_id'))
#     all_claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.created_at.desc()).all()
    
#     return render_template(
#         "claims_history.html",
#         claims=all_claims,
#         user_name=user.name,
#         behavioral_score=user.behavioral_score
#     )


# # 📈 User Profile & Stats
# @app.route("/profile")
# @login_required
# def profile():
#     user = User.query.get(session.get('user_id'))
#     claims = Claim.query.filter_by(user_id=user.id).all()
    
#     stats = {
#         "total_claims": len(claims),
#         "approved": len([c for c in claims if c.status == "APPROVED"]),
#         "pending": len([c for c in claims if c.status == "PENDING"]),
#         "rejected": len([c for c in claims if c.status == "REJECTED"]),
#         "approval_rate": f"{(len([c for c in claims if c.status == 'APPROVED']) / len(claims) * 100 if claims else 0):.1f}%"
#     }
    
#     return render_template(
#         "profile.html",
#         user=user,
#         stats=stats
#     )


# # 🏠 Home Redirect
# @app.route("/home")
# @login_required
# def home():
#     return redirect(url_for("index"))


# # 🚀 Error Handler
# @app.errorhandler(404)
# def not_found(e):
#     return render_template("error.html", error="Page not found"), 404


# # ⚡ Run App
# if __name__ == "__main__":
#     app.run(debug=True, host='127.0.0.1', port=5000)

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import requests
import random
from datetime import datetime, timedelta
from functools import wraps
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
# Import models and analytics

from models import db, User, Claim, MovementHistory, FraudPattern
from analytics import BehavioralAnalyzer, RiskClassifier, PollutionIndexFetcher

# ⚙️ Flask App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trust_insurance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "trust-insurance-secret-key-change-in-production"
app.permanent_session_lifetime = timedelta(hours=24)

# Initialize database
db.init_app(app)
# db = SQLAlchemy()
# 🔑 API Keys
OPENWEATHER_API_KEY = "f7b4a3d88337ad2894d3aefc138bf5d0"

# ✅ Create database tables
with app.app_context():
    db.create_all()


class User(db.Model):
    """User model with behavioral tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Device & Security
    device_fingerprint = db.Column(db.String(255), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Behavioral Scoring (0-100)
    behavioral_score = db.Column(db.Float, default=50.0)
    last_location_lat = db.Column(db.Float, nullable=True)
    last_location_lon = db.Column(db.Float, nullable=True)
    last_claim_timestamp = db.Column(db.DateTime, nullable=True)
    
    # Account Info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = db.relationship('Claim', backref='user', lazy=True, cascade='all, delete-orphan')
    movement_history = db.relationship('MovementHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'behavioral_score': self.behavioral_score,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }


class Claim(db.Model):
    """Insurance claim with full audit trail"""
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Location Data
    city = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Environmental Data
    weather = db.Column(db.String(50), nullable=False)
    pollution_index = db.Column(db.Float, nullable=True)  # AQI (0-500+)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    traffic = db.Column(db.String(50), nullable=False)
    
    # Trust & Risk Assessment
    trust_score = db.Column(db.Integer, nullable=False)  # 0-100
    risk_level = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH
    risk_factors = db.Column(db.JSON, nullable=True)  # Store detailed risk information
    
    # Behavioral Analysis
    speed_anomaly_detected = db.Column(db.Boolean, default=False)
    time_jump_detected = db.Column(db.Boolean, default=False)
    fraud_ring_score = db.Column(db.Float, default=0.0)  # Likelihood of coordinated fraud
    
    # Claim Status
    status = db.Column(db.String(20), default='PENDING')  # APPROVED, PENDING, REJECTED, UNDER_REVIEW
    approval_reason = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'city': self.city,
            'country': self.country,
            'weather': self.weather,
            'pollution_index': self.pollution_index,
            'traffic': self.traffic,
            'trust_score': self.trust_score,
            'risk_level': self.risk_level,
            'status': self.status,
            'speed_anomaly_detected': self.speed_anomaly_detected,
            'time_jump_detected': self.time_jump_detected,
            'created_at': self.created_at.isoformat()
        }


class MovementHistory(db.Model):
    """Track user movement for behavioral analysis"""
    __tablename__ = 'movement_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(120), nullable=True)
    
    # Movement Analysis
    calculated_speed_kmh = db.Column(db.Float, nullable=True)  # km/h from last location
    time_since_last_location = db.Column(db.Integer, nullable=True)  # seconds
    distance_from_last_km = db.Column(db.Float, nullable=True)  # km
    
    # Detection
    is_anomalous = db.Column(db.Boolean, default=False)
    anomaly_reason = db.Column(db.String(255), nullable=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'calculated_speed_kmh': self.calculated_speed_kmh,
            'is_anomalous': self.is_anomalous,
            'timestamp': self.timestamp.isoformat()
        }


class FraudPattern(db.Model):
    """Track coordinated fraud patterns"""
    __tablename__ = 'fraud_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Suspected Fraud Ring (multiple users, same location, same time)
    users_involved = db.Column(db.JSON, nullable=False)  # List of user IDs
    city = db.Column(db.String(120), nullable=False)
    timestamp_window = db.Column(db.DateTime, nullable=False)
    
    # Pattern Details
    claim_count = db.Column(db.Integer, default=1)
    confidence_score = db.Column(db.Float, default=0.0)  # 0-1
    status = db.Column(db.String(20), default='DETECTED')  # DETECTED, INVESTIGATING, CONFIRMED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 🌦️ Fetch Weather & Pollution Data
def get_weather_and_pollution(city, country):
    """
    Fetch both weather and AQI (Air Quality Index) data
    Returns: (weather, temp, humidity, pollution_index, aqi_emoji)
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5).json()
        
        if response.get("cod") != 200:
            return "Unknown", None, None, None, "Unknown"
        
        weather = response["weather"][0]["main"]
        temp = response["main"]["temp"]
        humidity = response["main"]["humidity"]
        
        # Get AQI (using a simpler approach - in production, use dedicated AQI API)
        if weather in ["Thunderstorm", "Tornado"]:
            aqi = random.randint(150, 250)  # Bad to very bad
        elif weather in ["Rain", "Drizzle"]:
            aqi = random.randint(80, 150)  # Moderate to bad
        elif weather in ["Mist", "Smoke", "Haze"]:
            aqi = random.randint(100, 200)  # Bad air quality
        else:
            aqi = random.randint(20, 80)  # Good to moderate
        
        aqi_category, aqi_emoji = PollutionIndexFetcher.get_aqi_category(aqi)
        
        return weather, temp, humidity, aqi, aqi_emoji
        
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "Unknown", None, None, None, "Unknown"


# 🚗 Get Traffic Conditions
def get_traffic():
    """Simulate realistic traffic patterns"""
    return random.choice(["Low", "Moderate", "Heavy"])


# 🧠 Calculate Trust Score (Enhanced with Pollution)
def calculate_trust_score(weather, pollution_index, traffic, behavioral_score, activity=None, gps_variation=None):
    """
    Calculate comprehensive trust score (0-100)
    Incorporates: Weather, Pollution, Traffic, User Behavior, Activity
    """
    score = 50
    
    # Weather Impact (-30 to +25)
    if weather in ["Thunderstorm", "Tornado"]:
        score += 25  # Major disruption
    elif weather in ["Rain", "Drizzle"]:
        score += 20
    elif weather in ["Snow", "Sleet"]:
        score += 18
    else:
        score += 5  # Clear weather - less impact
    
    # Pollution Impact (Bonus for high pollution - valid disruption)
    pollution_boost = PollutionIndexFetcher.get_aqi_impact(pollution_index)
    score += pollution_boost
    
    # Traffic Impact (High traffic = more disruption = bonus)
    if traffic == "Heavy":
        score += 15
    elif traffic == "Moderate":
        score += 8
    
    # User Behavioral Score (0-100 impact on -20 to +10)
    if behavioral_score > 80:
        score += 10  # Trustworthy user
    elif behavioral_score < 30:
        score -= 15  # Suspicious history
    
    # Activity variations (if provided)
    if activity:
        if activity >= 7:
            score += 10
        else:
            score += 3
    
    if gps_variation and gps_variation <= 8:
        score += 10
    
    # Clamp to 0-100
    return max(0, min(100, score))


# 🔐 Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function


# 📱 Authentication Routes
@app.route("/auth", methods=["GET", "POST"])
def auth_page():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "login":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                session["user_id"] = user.id
                session["user_email"] = user.email
                session["user_name"] = user.name
                session.permanent = True
                return redirect(url_for("index"))
            else:
                flash("Invalid email or password", "error")

        elif action == "signup":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if User.query.filter_by(email=email).first():
                flash("Email already registered", "error")
            elif password != confirm_password:
                flash("Passwords do not match", "error")
            elif len(password) < 6:
                flash("Password must be at least 6 characters", "error")
            else:
                new_user = User(email=email, name=name)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash("Account created! You can now login.", "success")

    return render_template("login.html")


# 📤 Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_page"))


# 🚀 Main Insurance Claim Route (Protected)
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    result = None
    recent_claims = []

    # Get user from database
    user = User.query.get(session.get('user_id'))
    
    if request.method == "POST":
        city = request.form.get("city")
        country = request.form.get("country")
        latitude = request.form.get("latitude", 0.0, type=float)
        longitude = request.form.get("longitude", 0.0, type=float)

        # 🌦️ Fetch environmental data
        weather, temp, humidity, pollution_index, aqi_emoji = get_weather_and_pollution(city, country)
        traffic = get_traffic()
        
        # Simulate activity and GPS variation (in production, from device)
        activity = random.randint(3, 10)
        gps_variation = random.randint(1, 15)
        
        # 🧠 Calculate base trust score
        base_trust_score = calculate_trust_score(
            weather, pollution_index, traffic, 
            user.behavioral_score, activity, gps_variation
        )
        
        # 🚨 Behavioral Anomaly Detection
        speed_anomaly, calculated_speed, anomaly_reason = BehavioralAnalyzer.detect_speed_anomaly(
            user, latitude, longitude, datetime.utcnow()
        )
        
        # 🎭 Coordinated Fraud Detection
        fraud_ring_score = BehavioralAnalyzer.detect_coordinated_fraud(city, country, datetime.utcnow(), user.id)
        
        # 📊 Build Risk Factors
        risk_factors = {
            "speed_anomaly": speed_anomaly,
            "time_jump": False,
            "fraud_ring_detected": fraud_ring_score > 0.5,
            "device_suspicious": False,
            "low_behavioral_score": user.behavioral_score < 40
        }
        
        # Apply anomaly penalties
        if speed_anomaly:
            base_trust_score -= 20
        if fraud_ring_score > 0.5:
            base_trust_score -= 15
        
        base_trust_score = max(0, min(100, base_trust_score))
        
        # 🎯 Risk Classification
        risk_level, auto_approve, risk_reason = RiskClassifier.classify_claim(
            base_trust_score, user.behavioral_score, risk_factors
        )
        
        # ✅ Determine Status
        if auto_approve:
            status = "APPROVED ✅"
            approval_status = "APPROVED"
        elif risk_level == "MEDIUM":
            status = "UNDER REVIEW ⚠️"
            approval_status = "PENDING"
        else:
            status = "REJECTED ❌"
            approval_status = "REJECTED"
        
        # 💾 Save claim to database
        claim = Claim(
            user_id=user.id,
            city=city,
            country=country,
            latitude=latitude,
            longitude=longitude,
            weather=weather,
            pollution_index=pollution_index,
            temperature=temp,
            humidity=humidity,
            traffic=traffic,
            trust_score=int(base_trust_score),
            risk_level=risk_level,
            risk_factors=risk_factors,
            speed_anomaly_detected=speed_anomaly,
            fraud_ring_score=fraud_ring_score,
            status=approval_status,
            approval_reason=risk_reason
        )
        db.session.add(claim)
        
        # Update user location and behavioral scoring
        user.last_location_lat = latitude
        user.last_location_lon = longitude
        user.last_claim_timestamp = datetime.utcnow()
        BehavioralAnalyzer.update_behavioral_score(user)
        
        db.session.commit()
        
        # Prepare result data
        result = {
            "claim_id": claim.id,
            "weather": weather,
            "pollution_index": pollution_index,
            "aqi_emoji": aqi_emoji,
            "temperature": temp,
            "humidity": humidity,
            "traffic": traffic,
            "trust_score": int(base_trust_score),
            "behavioral_score": user.behavioral_score,
            "risk_level": risk_level,
            "status": status,
            "reason": risk_reason,
            "activity": activity,
            "gps": gps_variation,
            "speed_anomaly": speed_anomaly,
            "speed_kmh": calculated_speed,
            "fraud_ring_likelihood": f"{fraud_ring_score * 100:.1f}%"
        }
    
    # Fetch recent claims for display
    recent_claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.created_at.desc()).limit(5).all()

    return render_template(
        "index.html",
        result=result,
        user_name=user.name,
        recent_claims=recent_claims,
        behavioral_score=user.behavioral_score
    )


# 📊 Claims History Route
@app.route("/claims-history")
@login_required
def claims_history():
    user = User.query.get(session.get('user_id'))
    all_claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.created_at.desc()).all()
    
    return render_template(
        "claims_history.html",
        claims=all_claims,
        user_name=user.name,
        behavioral_score=user.behavioral_score
    )


# 📈 User Profile & Stats
@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session.get('user_id'))
    claims = Claim.query.filter_by(user_id=user.id).all()
    
    stats = {
        "total_claims": len(claims),
        "approved": len([c for c in claims if c.status == "APPROVED"]),
        "pending": len([c for c in claims if c.status == "PENDING"]),
        "rejected": len([c for c in claims if c.status == "REJECTED"]),
        "approval_rate": f"{(len([c for c in claims if c.status == 'APPROVED']) / len(claims) * 100 if claims else 0):.1f}%"
    }
    
    return render_template(
        "profile.html",
        user=user,
        stats=stats
    )


# 🏠 Home Redirect
@app.route("/home")
@login_required
def home():
    return redirect(url_for("index"))


# 🚀 Error Handler
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found"), 404


# ⚡ Run App
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
