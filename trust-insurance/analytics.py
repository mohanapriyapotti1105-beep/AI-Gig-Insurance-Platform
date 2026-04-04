"""
Advanced Analytics & Fraud Detection
"""
import math
from datetime import datetime
from models import db, Claim, MovementHistory, FraudPattern


class BehavioralAnalyzer:
    """Detect suspicious behavior patterns"""
    
    # Realistic speed thresholds (km/h)
    MAX_REALISTIC_SPEED = 150  # Maximum speed for road vehicles
    TELEPORTATION_THRESHOLD = 500  # Impossible speed (km/h)
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def detect_speed_anomaly(user, current_lat, current_lon, current_time):
        """
        Detect if the user moved at impossible speeds
        Returns: (is_anomalous, calculated_speed_kmh, reason)
        """
        if not user.last_location_lat or not user.last_location_lon or not user.last_claim_timestamp:
            return False, 0, None
        
        # Calculate distance
        distance_km = BehavioralAnalyzer.haversine_distance(
            user.last_location_lat, user.last_location_lon,
            current_lat, current_lon
        )
        
        # Calculate time difference
        time_diff = (current_time - user.last_claim_timestamp).total_seconds()
        
        if time_diff < 10:  # Less than 10 seconds - ignore
            return False, 0, None
        
        # Calculate speed
        speed_kmh = (distance_km / (time_diff / 3600))
        
        # Detection logic
        if speed_kmh > BehavioralAnalyzer.TELEPORTATION_THRESHOLD:
            return True, speed_kmh, "TELEPORTATION_DETECTED"
        elif speed_kmh > BehavioralAnalyzer.MAX_REALISTIC_SPEED:
            return True, speed_kmh, "UNREALISTIC_SPEED"
        
        return False, speed_kmh, None
    
    @staticmethod
    def detect_coordinated_fraud(city, country, timestamp, exclude_user_id=None):
        """
        Detect if multiple users claim from same location within short timeframe
        Returns: fraud_ring_likelihood (0-1)
        """
        # Look for claims in same city within 30 minutes
        time_window_minutes = 30
        
        claims = db.session.query(Claim).filter(
            Claim.city == city,
            Claim.country == country,
            (datetime.utcnow() - Claim.created_at).cast(db.Integer) <= (time_window_minutes * 60)
        ).all()
        
        if exclude_user_id:
            claims = [c for c in claims if c.user_id != exclude_user_id]
        
        if len(claims) == 0:
            return 0.0
        elif len(claims) >= 5:
            return 0.9  # High likelihood of fraud ring
        elif len(claims) >= 3:
            return 0.7
        elif len(claims) >= 2:
            return 0.5
        
        return 0.0
    
    @staticmethod
    def update_behavioral_score(user):
        """Update user's behavioral score based on history"""
        # Fetch recent claims
        recent_claims = db.session.query(Claim).filter(
            Claim.user_id == user.id
        ).order_by(Claim.created_at.desc()).limit(10).all()
        
        if not recent_claims:
            user.behavioral_score = 50.0
            return
        
        score = 50.0
        
        # Positive factors
        approved_count = sum(1 for c in recent_claims if c.status == 'APPROVED')
        score += approved_count * 3  # +3 per legitimate claim
        
        # Negative factors
        rejected_count = sum(1 for c in recent_claims if c.status == 'REJECTED')
        score -= rejected_count * 5  # -5 per rejected claim
        
        anomalies = sum(1 for c in recent_claims if c.speed_anomaly_detected or c.time_jump_detected)
        score -= anomalies * 8  # -8 per anomaly detected
        
        # Clamp between 0 and 100
        user.behavioral_score = max(0, min(100, score))


class RiskClassifier:
    """Classify claims as LOW/MEDIUM/HIGH risk"""
    
    @staticmethod
    def classify_claim(trust_score, behavioral_score, risk_factors):
        """
        Classify claim risk and determine auto-approval threshold
        Returns: (risk_level, auto_approve, reason)
        """
        risk_level = None
        auto_approve = False
        reason = ""
        
        # Count negative risk factors
        negative_factors = sum(1 for v in risk_factors.values() if v is True)
        
        # Composite score: 60% trust, 30% behavior, 10% negative factors
        composite_score = (trust_score * 0.6) + (behavioral_score * 0.3) - (negative_factors * 3)
        
        if composite_score >= 75 and negative_factors == 0:
            risk_level = "LOW"
            auto_approve = True
            reason = "✅ Genuine disruption + excellent history + device verified"
        elif composite_score >= 60 and negative_factors <= 1:
            risk_level = "MEDIUM"
            auto_approve = False
            reason = "⚠️ Moderate risk - requires verification"
        else:
            risk_level = "HIGH"
            auto_approve = False
            reason = "❌ High risk - manual review required"
        
        return risk_level, auto_approve, reason


class PollutionIndexFetcher:
    """Fetch and analyze air quality data"""
    
    @staticmethod
    def get_aqi_impact(aqi_value):
        """
        Convert AQI value to trust score impact
        AQI categories: 0-50 (good), 51-100 (moderate), 101-150 (bad), 151-200 (very bad), 201+ (hazardous)
        """
        if aqi_value is None:
            return 0
        
        if aqi_value <= 50:
            return 0  # No impact
        elif aqi_value <= 100:
            return 5  # Slight impact
        elif aqi_value <= 150:
            return 15  # Moderate impact (+15 to trust score)
        elif aqi_value <= 200:
            return 20  # High impact
        else:
            return 25  # Severe pollution impact
    
    @staticmethod
    def get_aqi_category(aqi_value):
        """Get AQI category name and emoji"""
        if aqi_value is None:
            return "Unknown", "❓"
        
        if aqi_value <= 50:
            return "Good", "🟢"
        elif aqi_value <= 100:
            return "Moderate", "🟡"
        elif aqi_value <= 150:
            return "Bad", "🟠"
        elif aqi_value <= 200:
            return "Very Bad", "🔴"
        else:
            return "Hazardous", "⚫"
