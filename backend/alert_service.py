"""
Alert Service Module
Manages farmer alerts, notifications, and location storage

Author: Rajat Pundir (@Rajatpundir7)
Role: Full Stack Developer & Database Architect
Features: Weather Alerts, Disease Outbreak Notifications, Government Schemes
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
import asyncio

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent


# =====================================
# PYDANTIC MODELS
# =====================================

class FarmerLocationUpdate(BaseModel):
    """Model for location update request"""
    farmer_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    timestamp: Optional[str] = None


class FarmerRegistration(BaseModel):
    """Model for farmer registration"""
    farmer_id: str
    name: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    soil_type: str = "loamy"
    soil_ph: float = Field(6.5, ge=0, le=14)
    current_crop: str = "wheat"
    water_source: str = "rainfall"
    farm_size_acres: float = Field(5.0, ge=0)
    phone: Optional[str] = None
    notification_enabled: bool = True


class DiseaseReport(BaseModel):
    """Model for disease/pest report"""
    farmer_id: str
    disease_name: str
    severity: float = Field(0.5, ge=0, le=1)
    crop_affected: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class NotificationPreferences(BaseModel):
    """Model for notification preferences"""
    farmer_id: str
    push_enabled: bool = True
    sms_enabled: bool = False
    email_enabled: bool = False
    alert_threshold: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    quiet_hours_start: Optional[int] = None  # Hour 0-23
    quiet_hours_end: Optional[int] = None


# =====================================
# LOCATION SERVICE
# =====================================

class LocationService:
    """Service for managing farmer locations"""
    
    def __init__(self):
        self.locations_file = ROOT_DIR / "data" / "farmer_locations.json"
        self.locations: Dict[str, Dict] = {}
        self._load_locations()
    
    def _load_locations(self):
        """Load saved locations from file"""
        try:
            if self.locations_file.exists():
                with open(self.locations_file, 'r') as f:
                    self.locations = json.load(f)
                logger.info(f"Loaded {len(self.locations)} farmer locations")
        except Exception as e:
            logger.error(f"Error loading locations: {e}")
            self.locations = {}
    
    def _save_locations(self):
        """Save locations to file"""
        try:
            self.locations_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.locations_file, 'w') as f:
                json.dump(self.locations, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving locations: {e}")
    
    def update_location(self, update: FarmerLocationUpdate) -> Dict:
        """Update farmer's location"""
        location_data = {
            "latitude": update.latitude,
            "longitude": update.longitude,
            "accuracy": update.accuracy,
            "updated_at": update.timestamp or datetime.now().isoformat(),
            "history": self.locations.get(update.farmer_id, {}).get("history", [])
        }
        
        # Keep last 10 location history
        location_data["history"].append({
            "lat": update.latitude,
            "lon": update.longitude,
            "time": datetime.now().isoformat()
        })
        location_data["history"] = location_data["history"][-10:]
        
        self.locations[update.farmer_id] = location_data
        self._save_locations()
        
        return {
            "success": True,
            "farmer_id": update.farmer_id,
            "location": {"lat": update.latitude, "lon": update.longitude}
        }
    
    def get_location(self, farmer_id: str) -> Optional[Dict]:
        """Get farmer's last known location"""
        return self.locations.get(farmer_id)
    
    def get_nearby_farmers(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 50
    ) -> List[Dict]:
        """Find farmers within radius of a location"""
        nearby = []
        
        for farmer_id, loc in self.locations.items():
            if "latitude" not in loc:
                continue
            
            distance = self._haversine_distance(
                latitude, longitude,
                loc["latitude"], loc["longitude"]
            )
            
            if distance <= radius_km:
                nearby.append({
                    "farmer_id": farmer_id,
                    "latitude": loc["latitude"],
                    "longitude": loc["longitude"],
                    "distance_km": round(distance, 2)
                })
        
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate distance between two points in km"""
        import math
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c


# =====================================
# NOTIFICATION SERVICE
# =====================================

class NotificationService:
    """Service for managing push notifications"""
    
    def __init__(self):
        self.notifications_file = ROOT_DIR / "data" / "notifications.json"
        self.preferences_file = ROOT_DIR / "data" / "notification_preferences.json"
        self.notifications: Dict[str, List[Dict]] = {}
        self.preferences: Dict[str, Dict] = {}
        self._load_data()
    
    def _load_data(self):
        """Load notifications and preferences"""
        try:
            if self.notifications_file.exists():
                with open(self.notifications_file, 'r') as f:
                    self.notifications = json.load(f)
            
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
        except Exception as e:
            logger.error(f"Error loading notification data: {e}")
    
    def _save_notifications(self):
        """Save notifications to file"""
        try:
            self.notifications_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.notifications_file, 'w') as f:
                json.dump(self.notifications, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")
    
    def _save_preferences(self):
        """Save preferences to file"""
        try:
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
    
    def set_preferences(self, prefs: NotificationPreferences) -> Dict:
        """Set notification preferences for a farmer"""
        self.preferences[prefs.farmer_id] = {
            "push_enabled": prefs.push_enabled,
            "sms_enabled": prefs.sms_enabled,
            "email_enabled": prefs.email_enabled,
            "alert_threshold": prefs.alert_threshold,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "updated_at": datetime.now().isoformat()
        }
        self._save_preferences()
        
        return {"success": True, "farmer_id": prefs.farmer_id}
    
    def get_preferences(self, farmer_id: str) -> Dict:
        """Get notification preferences"""
        return self.preferences.get(farmer_id, {
            "push_enabled": True,
            "sms_enabled": False,
            "email_enabled": False,
            "alert_threshold": "MEDIUM"
        })
    
    def add_notification(
        self,
        farmer_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        priority: int = 2
    ) -> Dict:
        """Add a notification for a farmer"""
        notification = {
            "id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{farmer_id[:6]}",
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "read": False,
            "delivered": False
        }
        
        if farmer_id not in self.notifications:
            self.notifications[farmer_id] = []
        
        self.notifications[farmer_id].insert(0, notification)
        
        # Keep only last 100 notifications per farmer
        self.notifications[farmer_id] = self.notifications[farmer_id][:100]
        
        self._save_notifications()
        
        return notification
    
    def get_notifications(
        self, 
        farmer_id: str, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Get notifications for a farmer"""
        notifications = self.notifications.get(farmer_id, [])
        
        if unread_only:
            notifications = [n for n in notifications if not n.get("read", False)]
        
        return notifications[:limit]
    
    def mark_as_read(self, farmer_id: str, notification_id: str) -> bool:
        """Mark a notification as read"""
        if farmer_id not in self.notifications:
            return False
        
        for notif in self.notifications[farmer_id]:
            if notif["id"] == notification_id:
                notif["read"] = True
                notif["read_at"] = datetime.now().isoformat()
                self._save_notifications()
                return True
        
        return False
    
    def mark_all_read(self, farmer_id: str) -> int:
        """Mark all notifications as read"""
        if farmer_id not in self.notifications:
            return 0
        
        count = 0
        for notif in self.notifications[farmer_id]:
            if not notif.get("read", False):
                notif["read"] = True
                notif["read_at"] = datetime.now().isoformat()
                count += 1
        
        self._save_notifications()
        return count
    
    def get_unread_count(self, farmer_id: str) -> int:
        """Get count of unread notifications"""
        if farmer_id not in self.notifications:
            return 0
        
        return sum(1 for n in self.notifications[farmer_id] if not n.get("read", False))
    
    def should_send_notification(self, farmer_id: str, risk_level: str) -> bool:
        """Check if notification should be sent based on preferences"""
        prefs = self.get_preferences(farmer_id)
        
        if not prefs.get("push_enabled", True):
            return False
        
        # Check quiet hours
        quiet_start = prefs.get("quiet_hours_start")
        quiet_end = prefs.get("quiet_hours_end")
        
        if quiet_start is not None and quiet_end is not None:
            current_hour = datetime.now().hour
            if quiet_start <= current_hour < quiet_end:
                # Unless it's HIGH priority
                if risk_level != "HIGH":
                    return False
        
        # Check threshold
        threshold = prefs.get("alert_threshold", "MEDIUM")
        levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        
        return levels.get(risk_level, 2) >= levels.get(threshold, 2)


# =====================================
# ALERT SERVICE (Integration)
# =====================================

class AlertService:
    """
    Main alert service that integrates:
    - Farmer network for similarity detection
    - Location service for geo-based alerts
    - Notification service for delivering alerts
    """
    
    def __init__(self):
        self.location_service = LocationService()
        self.notification_service = NotificationService()
        self._farmer_network = None
    
    @property
    def farmer_network(self):
        """Lazy load farmer network"""
        if self._farmer_network is None:
            from farmer_alert_network import get_farmer_network
            self._farmer_network = get_farmer_network()
        return self._farmer_network
    
    def register_farmer(self, registration: FarmerRegistration) -> Dict:
        """Register a new farmer in the system"""
        # Register in farmer network
        farmer = self.farmer_network.register_farmer({
            "farmer_id": registration.farmer_id,
            "latitude": registration.latitude,
            "longitude": registration.longitude,
            "soil_type": registration.soil_type,
            "soil_ph": registration.soil_ph,
            "current_crop": registration.current_crop,
            "water_source": registration.water_source,
            "farm_size_acres": registration.farm_size_acres
        })
        
        # Store location
        self.location_service.update_location(FarmerLocationUpdate(
            farmer_id=registration.farmer_id,
            latitude=registration.latitude,
            longitude=registration.longitude
        ))
        
        # Set default notification preferences
        self.notification_service.set_preferences(NotificationPreferences(
            farmer_id=registration.farmer_id,
            push_enabled=registration.notification_enabled
        ))
        
        # Send welcome notification
        self.notification_service.add_notification(
            farmer_id=registration.farmer_id,
            notification_type="WELCOME",
            title="Welcome to Kisan.JI! 🌾",
            message="You're now part of the farmer alert network. You'll receive alerts about crop diseases and pests in your area.",
            priority=3
        )
        
        return {
            "success": True,
            "farmer_id": registration.farmer_id,
            "message": "Farmer registered successfully"
        }
    
    def report_disease(self, report: DiseaseReport) -> Dict:
        """Report a disease and trigger alerts to similar farmers"""
        # Create disease report in network
        result = self.farmer_network.report_disease(
            farmer_id=report.farmer_id,
            disease_name=report.disease_name,
            severity=report.severity,
            crop_affected=report.crop_affected,
            description=report.description or ""
        )
        
        # Create notifications for alerted farmers
        notifications_sent = 0
        for alert in result.get("alerts", []):
            target_farmer = alert["target_farmer_id"]
            
            # Check if should send based on preferences
            if self.notification_service.should_send_notification(
                target_farmer, 
                alert["risk_level"]
            ):
                self.notification_service.add_notification(
                    farmer_id=target_farmer,
                    notification_type="DISEASE_ALERT",
                    title=f"⚠️ {alert['risk_level']} Risk: {report.disease_name}",
                    message=alert["message"],
                    data={
                        "alert_id": alert["alert_id"],
                        "disease": report.disease_name,
                        "severity": report.severity,
                        "distance_km": alert["distance_km"],
                        "recommendations": alert["recommendations"]
                    },
                    priority=alert["priority"]
                )
                notifications_sent += 1
        
        result["notifications_sent"] = notifications_sent
        
        return result
    
    def get_farmer_dashboard(self, farmer_id: str) -> Dict:
        """Get dashboard data for a farmer"""
        # Get farmer info
        farmer = self.farmer_network.get_farmer(farmer_id)
        
        # Get alerts
        alerts = self.farmer_network.get_alerts_for_farmer(farmer_id)
        
        # Get notifications
        notifications = self.notification_service.get_notifications(
            farmer_id, 
            unread_only=False, 
            limit=20
        )
        
        # Get similar farmers
        similar = self.farmer_network.find_similar_farmers(farmer_id, top_k=5)
        
        # Get location
        location = self.location_service.get_location(farmer_id)
        
        return {
            "farmer": farmer.to_dict() if farmer else None,
            "alerts": alerts[:5],
            "notifications": notifications[:10],
            "unread_count": self.notification_service.get_unread_count(farmer_id),
            "similar_farmers": [
                {"farmer_id": f[0], "similarity": f[1], "distance_km": f[2]}
                for f in similar
            ],
            "location": location,
            "network_stats": self.farmer_network.get_network_stats()
        }


# =====================================
# SINGLETON INSTANCES
# =====================================

_location_service: Optional[LocationService] = None
_notification_service: Optional[NotificationService] = None
_alert_service: Optional[AlertService] = None


def get_location_service() -> LocationService:
    """Get location service instance"""
    global _location_service
    if _location_service is None:
        _location_service = LocationService()
    return _location_service


def get_notification_service() -> NotificationService:
    """Get notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


def get_alert_service() -> AlertService:
    """Get alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


# =====================================
# TEST
# =====================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = get_alert_service()
    
    # Register farmers
    service.register_farmer(FarmerRegistration(
        farmer_id="TEST001",
        name="Test Farmer 1",
        latitude=30.3165,
        longitude=78.0322,
        soil_type="loamy",
        current_crop="wheat"
    ))
    
    service.register_farmer(FarmerRegistration(
        farmer_id="TEST002",
        name="Test Farmer 2",
        latitude=30.3265,
        longitude=78.0422,
        soil_type="loamy",
        current_crop="wheat"
    ))
    
    # Report disease
    result = service.report_disease(DiseaseReport(
        farmer_id="TEST001",
        disease_name="Brown Spot",
        severity=0.7
    ))
    
    print(f"Disease reported, {result['notifications_sent']} notifications sent")
    
    # Check dashboard
    dashboard = service.get_farmer_dashboard("TEST002")
    print(f"Unread notifications: {dashboard['unread_count']}")
