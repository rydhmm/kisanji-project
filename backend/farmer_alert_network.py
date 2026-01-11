"""
Farmer Alert Network Module
GNN-based similarity network for disease/pest alert propagation

Each farmer is a node with features:
- Location (lat, lon)
- Soil type/pH
- Current crop
- Water source
- Farm size

Similar farmers are connected. When one farmer's crop is affected by disease/pest,
the system proactively alerts similar farmers before the issue spreads.
"""
import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory for imports
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR.parent / "AgriGraph_Optimizer"))

try:
    from torch_geometric.data import Data
    from torch_geometric.nn import GATConv, SAGEConv
    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import StandardScaler
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    logging.warning("torch_geometric not installed. Using fallback similarity methods.")

logger = logging.getLogger(__name__)


# =====================================
# FARMER GRAPH NEURAL NETWORK
# =====================================

class FarmerSimilarityGNN(nn.Module):
    """
    Graph Attention Network for farmer similarity and alert propagation
    
    Architecture:
    - Input: Farmer features (location, soil, crop, etc.)
    - GAT layers: Learn attention weights between similar farmers
    - Output: Risk embeddings for alert propagation
    """
    def __init__(self, in_channels: int = 8, hidden_channels: int = 32, 
                 out_channels: int = 16, heads: int = 4):
        super(FarmerSimilarityGNN, self).__init__()
        
        if not TORCH_GEOMETRIC_AVAILABLE:
            # Fallback to simple MLP if torch_geometric not available
            self.fallback = True
            self.mlp = nn.Sequential(
                nn.Linear(in_channels, hidden_channels),
                nn.ReLU(),
                nn.Linear(hidden_channels, out_channels)
            )
        else:
            self.fallback = False
            self.conv1 = GATConv(in_channels, hidden_channels, heads=heads, dropout=0.3)
            self.conv2 = GATConv(hidden_channels * heads, out_channels, heads=1, concat=False, dropout=0.3)
        
        self.risk_classifier = nn.Sequential(
            nn.Linear(out_channels, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()  # Risk score 0-1
        )
    
    def forward(self, x, edge_index=None):
        if self.fallback or edge_index is None:
            embeddings = self.mlp(x)
        else:
            embeddings = F.elu(self.conv1(x, edge_index))
            embeddings = F.elu(self.conv2(embeddings, edge_index))
        
        risk_scores = self.risk_classifier(embeddings)
        return embeddings, risk_scores


# =====================================
# FARMER NODE REPRESENTATION
# =====================================

class FarmerNode:
    """Represents a farmer as a node in the network"""
    
    # Encode categorical variables
    SOIL_TYPES = {
        'loamy': 0, 'clay': 1, 'sandy': 2, 'black': 3, 'red': 4, 'alluvial': 5
    }
    CROP_TYPES = {
        'rice': 0, 'wheat': 1, 'maize': 2, 'cotton': 3, 'sugarcane': 4,
        'potato': 5, 'tomato': 6, 'onion': 7, 'soybean': 8, 'groundnut': 9,
        'mango': 10, 'banana': 11, 'vegetables': 12, 'pulses': 13, 'other': 14
    }
    WATER_SOURCES = {
        'rainfall': 0, 'irrigation': 1, 'borewell': 2, 'canal': 3, 'river': 4, 'both': 5
    }
    
    def __init__(
        self,
        farmer_id: str,
        latitude: float,
        longitude: float,
        soil_type: str = 'loamy',
        soil_ph: float = 6.5,
        current_crop: str = 'wheat',
        water_source: str = 'rainfall',
        farm_size_acres: float = 5.0,
        **kwargs
    ):
        self.farmer_id = farmer_id
        self.latitude = latitude
        self.longitude = longitude
        self.soil_type = soil_type.lower()
        self.soil_ph = soil_ph
        self.current_crop = current_crop.lower()
        self.water_source = water_source.lower()
        self.farm_size = farm_size_acres
        self.extra_data = kwargs
        
        # Track disease/pest reports
        self.disease_reports: List[Dict] = []
        self.last_updated = datetime.now()
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert farmer data to numeric feature vector for GNN"""
        return np.array([
            self.latitude / 90.0,  # Normalize lat to [-1, 1]
            self.longitude / 180.0,  # Normalize lon to [-1, 1]
            self.SOIL_TYPES.get(self.soil_type, 0) / 5.0,
            self.soil_ph / 14.0,  # pH 0-14
            self.CROP_TYPES.get(self.current_crop, 14) / 14.0,
            self.WATER_SOURCES.get(self.water_source, 0) / 5.0,
            min(self.farm_size, 100) / 100.0,  # Normalize farm size
            len(self.disease_reports) / 10.0  # Recent disease count
        ], dtype=np.float32)
    
    def add_disease_report(self, disease: str, severity: float, detected_at: datetime = None):
        """Record a disease/pest detection"""
        self.disease_reports.append({
            'disease': disease,
            'severity': severity,
            'detected_at': detected_at or datetime.now(),
            'crop': self.current_crop
        })
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'farmer_id': self.farmer_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'soil_type': self.soil_type,
            'soil_ph': self.soil_ph,
            'current_crop': self.current_crop,
            'water_source': self.water_source,
            'farm_size_acres': self.farm_size,
            'disease_reports': self.disease_reports,
            'last_updated': self.last_updated.isoformat()
        }


# =====================================
# FARMER ALERT NETWORK
# =====================================

class FarmerAlertNetwork:
    """
    Main class for managing farmer similarity network and alert propagation
    
    Features:
    1. Build farmer graph based on similarity (soil, crop, location)
    2. Detect when a farmer reports disease/pest
    3. Find similar farmers who should be alerted
    4. Generate and queue alerts
    """
    
    def __init__(self, device: str = 'cpu'):
        self.device = torch.device(device)
        self.farmers: Dict[str, FarmerNode] = {}
        self.alerts_queue: List[Dict] = []
        self.model: Optional[FarmerSimilarityGNN] = None
        self.scaler = StandardScaler()
        self.similarity_threshold = 0.7
        self.distance_km_threshold = 50  # Alert farmers within 50km
        
        # Initialize model
        self._initialize_model()
        
        logger.info("✅ FarmerAlertNetwork initialized")
    
    def _initialize_model(self):
        """Initialize the GNN model"""
        self.model = FarmerSimilarityGNN(
            in_channels=8,
            hidden_channels=32,
            out_channels=16,
            heads=4
        ).to(self.device)
        self.model.eval()
    
    def register_farmer(self, farmer_data: Dict) -> FarmerNode:
        """Register a new farmer in the network"""
        farmer = FarmerNode(**farmer_data)
        self.farmers[farmer.farmer_id] = farmer
        logger.info(f"Registered farmer: {farmer.farmer_id}")
        return farmer
    
    def update_farmer_location(self, farmer_id: str, latitude: float, longitude: float) -> bool:
        """Update farmer's location"""
        if farmer_id in self.farmers:
            self.farmers[farmer_id].latitude = latitude
            self.farmers[farmer_id].longitude = longitude
            self.farmers[farmer_id].last_updated = datetime.now()
            return True
        return False
    
    def get_farmer(self, farmer_id: str) -> Optional[FarmerNode]:
        """Get farmer by ID"""
        return self.farmers.get(farmer_id)
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _calculate_similarity(self, farmer1: FarmerNode, farmer2: FarmerNode) -> float:
        """
        Calculate similarity score between two farmers
        
        Factors:
        - Same/similar crop: 40%
        - Same soil type: 25%
        - Similar location: 20%
        - Similar pH: 10%
        - Same water source: 5%
        """
        score = 0.0
        
        # Crop similarity (40%)
        if farmer1.current_crop == farmer2.current_crop:
            score += 0.4
        elif farmer1.current_crop in ['rice', 'wheat', 'maize'] and farmer2.current_crop in ['rice', 'wheat', 'maize']:
            score += 0.2  # Similar grain crops
        
        # Soil similarity (25%)
        if farmer1.soil_type == farmer2.soil_type:
            score += 0.25
        
        # Location proximity (20%) - closer = higher score
        distance = self._haversine_distance(
            farmer1.latitude, farmer1.longitude,
            farmer2.latitude, farmer2.longitude
        )
        if distance < 10:
            score += 0.2
        elif distance < 25:
            score += 0.15
        elif distance < 50:
            score += 0.1
        elif distance < 100:
            score += 0.05
        
        # pH similarity (10%)
        ph_diff = abs(farmer1.soil_ph - farmer2.soil_ph)
        if ph_diff < 0.5:
            score += 0.1
        elif ph_diff < 1.0:
            score += 0.05
        
        # Water source (5%)
        if farmer1.water_source == farmer2.water_source:
            score += 0.05
        
        return score
    
    def find_similar_farmers(
        self, 
        farmer_id: str, 
        top_k: int = 10,
        min_similarity: float = 0.5
    ) -> List[Tuple[str, float, float]]:
        """
        Find farmers similar to the given farmer
        
        Returns:
            List of (farmer_id, similarity_score, distance_km)
        """
        if farmer_id not in self.farmers:
            return []
        
        source_farmer = self.farmers[farmer_id]
        similar = []
        
        for fid, farmer in self.farmers.items():
            if fid == farmer_id:
                continue
            
            similarity = self._calculate_similarity(source_farmer, farmer)
            distance = self._haversine_distance(
                source_farmer.latitude, source_farmer.longitude,
                farmer.latitude, farmer.longitude
            )
            
            if similarity >= min_similarity:
                similar.append((fid, similarity, distance))
        
        # Sort by similarity (descending)
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:top_k]
    
    def report_disease(
        self,
        farmer_id: str,
        disease_name: str,
        severity: float = 0.5,
        crop_affected: str = None,
        description: str = ""
    ) -> Dict:
        """
        Report a disease/pest detection and alert similar farmers
        
        Args:
            farmer_id: ID of reporting farmer
            disease_name: Name of disease/pest
            severity: Severity score 0-1
            crop_affected: Crop that was affected
            description: Optional description
            
        Returns:
            Report summary with alerts generated
        """
        if farmer_id not in self.farmers:
            return {"error": "Farmer not found", "alerts_sent": 0}
        
        farmer = self.farmers[farmer_id]
        
        # Record the disease report
        farmer.add_disease_report(disease_name, severity)
        
        # Find similar farmers to alert
        similar_farmers = self.find_similar_farmers(
            farmer_id,
            top_k=20,
            min_similarity=0.4
        )
        
        # Generate alerts
        alerts_sent = []
        for sim_farmer_id, similarity, distance in similar_farmers:
            # Only alert if within distance threshold
            if distance <= self.distance_km_threshold:
                alert = self._create_alert(
                    source_farmer=farmer,
                    target_farmer_id=sim_farmer_id,
                    disease=disease_name,
                    severity=severity,
                    similarity=similarity,
                    distance=distance
                )
                self.alerts_queue.append(alert)
                alerts_sent.append(alert)
        
        report = {
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{farmer_id[:6]}",
            "farmer_id": farmer_id,
            "disease": disease_name,
            "severity": severity,
            "crop_affected": crop_affected or farmer.current_crop,
            "location": {"lat": farmer.latitude, "lon": farmer.longitude},
            "similar_farmers_found": len(similar_farmers),
            "alerts_sent": len(alerts_sent),
            "alerts": alerts_sent,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Disease reported: {disease_name} by {farmer_id}, {len(alerts_sent)} alerts sent")
        
        return report
    
    def _create_alert(
        self,
        source_farmer: FarmerNode,
        target_farmer_id: str,
        disease: str,
        severity: float,
        similarity: float,
        distance: float
    ) -> Dict:
        """Create an alert for a similar farmer"""
        target_farmer = self.farmers.get(target_farmer_id)
        
        # Calculate risk level based on similarity and distance
        risk_factor = similarity * (1 - min(distance, 50) / 50) * severity
        
        if risk_factor > 0.6:
            risk_level = "HIGH"
            priority = 1
        elif risk_factor > 0.3:
            risk_level = "MEDIUM"
            priority = 2
        else:
            risk_level = "LOW"
            priority = 3
        
        return {
            "alert_id": f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{target_farmer_id[:6]}",
            "target_farmer_id": target_farmer_id,
            "source_farmer_id": source_farmer.farmer_id,
            "type": "DISEASE_ALERT",
            "disease": disease,
            "severity": severity,
            "risk_level": risk_level,
            "risk_factor": round(risk_factor, 3),
            "priority": priority,
            "similarity_score": round(similarity, 3),
            "distance_km": round(distance, 2),
            "message": self._generate_alert_message(
                disease, risk_level, source_farmer.current_crop, distance
            ),
            "recommendations": self._get_prevention_recommendations(disease),
            "created_at": datetime.now().isoformat(),
            "read": False,
            "dismissed": False
        }
    
    def _generate_alert_message(
        self, 
        disease: str, 
        risk_level: str, 
        crop: str, 
        distance: float
    ) -> str:
        """Generate a human-readable alert message"""
        return (
            f"⚠️ {risk_level} RISK ALERT: {disease} has been detected in {crop} crops "
            f"approximately {distance:.1f} km from your farm. "
            f"A nearby farmer with similar conditions has reported this issue. "
            f"Please inspect your crops and take preventive measures."
        )
    
    def _get_prevention_recommendations(self, disease: str) -> List[str]:
        """Get prevention recommendations for a disease/pest"""
        recommendations = {
            "default": [
                "Regularly inspect your crops for early signs",
                "Maintain proper field hygiene",
                "Consult with local agricultural extension officer",
                "Consider preventive fungicide/pesticide application"
            ],
            "bacterial_blight": [
                "Use disease-free seeds",
                "Apply copper-based bactericides",
                "Avoid overhead irrigation",
                "Remove and destroy infected plants"
            ],
            "brown_spot": [
                "Apply potassium fertilizer to strengthen plants",
                "Use fungicides like Mancozeb or Carbendazim",
                "Maintain balanced fertilization",
                "Improve drainage in fields"
            ],
            "leaf_blast": [
                "Apply systemic fungicides like Tricyclazole",
                "Avoid excess nitrogen fertilization",
                "Use resistant varieties",
                "Maintain proper water management"
            ],
            "aphids": [
                "Apply neem-based pesticides",
                "Release natural predators like ladybugs",
                "Use yellow sticky traps for monitoring",
                "Apply insecticidal soap"
            ],
            "bollworm": [
                "Use pheromone traps for monitoring",
                "Apply Bt-based insecticides",
                "Practice crop rotation",
                "Destroy crop residues after harvest"
            ]
        }
        
        disease_lower = disease.lower().replace(" ", "_")
        return recommendations.get(disease_lower, recommendations["default"])
    
    def get_alerts_for_farmer(
        self, 
        farmer_id: str, 
        include_read: bool = False
    ) -> List[Dict]:
        """Get all alerts for a specific farmer"""
        alerts = [
            a for a in self.alerts_queue 
            if a["target_farmer_id"] == farmer_id
        ]
        
        if not include_read:
            alerts = [a for a in alerts if not a.get("read", False)]
        
        # Sort by priority and time
        alerts.sort(key=lambda x: (x["priority"], x["created_at"]))
        return alerts
    
    def mark_alert_read(self, alert_id: str, farmer_id: str) -> bool:
        """Mark an alert as read"""
        for alert in self.alerts_queue:
            if alert["alert_id"] == alert_id and alert["target_farmer_id"] == farmer_id:
                alert["read"] = True
                return True
        return False
    
    def get_network_stats(self) -> Dict:
        """Get statistics about the farmer network"""
        total_farmers = len(self.farmers)
        total_alerts = len(self.alerts_queue)
        unread_alerts = sum(1 for a in self.alerts_queue if not a.get("read", False))
        
        # Disease distribution
        disease_counts = {}
        for farmer in self.farmers.values():
            for report in farmer.disease_reports:
                disease = report["disease"]
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        return {
            "total_farmers": total_farmers,
            "total_alerts": total_alerts,
            "unread_alerts": unread_alerts,
            "disease_distribution": disease_counts,
            "avg_similarity_threshold": self.similarity_threshold,
            "distance_km_threshold": self.distance_km_threshold
        }
    
    def build_graph_embeddings(self) -> Optional[torch.Tensor]:
        """
        Build graph and generate farmer embeddings using GNN
        
        Returns:
            Tensor of farmer embeddings
        """
        if len(self.farmers) < 2:
            return None
        
        # Get feature vectors for all farmers
        farmer_ids = list(self.farmers.keys())
        features = np.array([
            self.farmers[fid].to_feature_vector() 
            for fid in farmer_ids
        ])
        
        # Build adjacency based on similarity
        edges = []
        for i, fid1 in enumerate(farmer_ids):
            for j, fid2 in enumerate(farmer_ids):
                if i >= j:
                    continue
                similarity = self._calculate_similarity(
                    self.farmers[fid1], 
                    self.farmers[fid2]
                )
                if similarity >= 0.4:
                    edges.append((i, j))
                    edges.append((j, i))
        
        # Convert to tensors
        x = torch.tensor(features, dtype=torch.float32).to(self.device)
        
        if edges:
            edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous().to(self.device)
        else:
            edge_index = None
        
        # Get embeddings from model
        with torch.no_grad():
            embeddings, risk_scores = self.model(x, edge_index)
        
        return embeddings


# =====================================
# REINFORCEMENT LEARNING FOR ALERT OPTIMIZATION
# =====================================

class AlertPriorityRL:
    """
    RL agent for optimizing alert priority and timing
    
    State: (farmer_similarity, distance, severity, time_since_report, weather_risk)
    Action: (priority_adjustment, send_now/delay)
    Reward: Based on farmer response and disease prevention success
    """
    
    def __init__(self, state_dim: int = 5, action_dim: int = 2, device: str = 'cpu'):
        self.device = torch.device(device)
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Simple policy network
        self.policy = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, action_dim),
            nn.Softmax(dim=-1)
        ).to(self.device)
        
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=0.001)
        self.memory = []
    
    def get_priority_action(self, state: np.ndarray) -> Tuple[int, float]:
        """Get alert priority action"""
        state_tensor = torch.tensor(state, dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            action_probs = self.policy(state_tensor)
        
        action = torch.multinomial(action_probs, 1).item()
        confidence = action_probs[action].item()
        
        return action, confidence
    
    def optimize_alert(self, alert: Dict, weather_risk: float = 0.5) -> Dict:
        """
        Optimize alert priority using RL
        
        Args:
            alert: Alert dictionary
            weather_risk: Current weather risk factor
            
        Returns:
            Optimized alert
        """
        state = np.array([
            alert.get("similarity_score", 0.5),
            alert.get("distance_km", 25) / 50.0,
            alert.get("severity", 0.5),
            0.0,  # Time since report (0 = just now)
            weather_risk
        ], dtype=np.float32)
        
        action, confidence = self.get_priority_action(state)
        
        # Adjust priority based on action
        if action == 0:  # Increase priority
            alert["priority"] = max(1, alert.get("priority", 2) - 1)
            alert["rl_recommendation"] = "URGENT - Send immediately"
        else:  # Keep or decrease
            alert["rl_recommendation"] = "Standard priority"
        
        alert["rl_confidence"] = round(confidence, 3)
        
        return alert


# =====================================
# SINGLETON INSTANCE
# =====================================

_network_instance: Optional[FarmerAlertNetwork] = None
_rl_instance: Optional[AlertPriorityRL] = None


def get_farmer_network() -> FarmerAlertNetwork:
    """Get or create the farmer alert network instance"""
    global _network_instance
    if _network_instance is None:
        _network_instance = FarmerAlertNetwork()
    return _network_instance


def get_alert_rl() -> AlertPriorityRL:
    """Get or create the alert RL agent instance"""
    global _rl_instance
    if _rl_instance is None:
        _rl_instance = AlertPriorityRL()
    return _rl_instance


# =====================================
# TEST CODE
# =====================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create network
    network = get_farmer_network()
    
    # Register sample farmers
    farmers_data = [
        {"farmer_id": "F001", "latitude": 30.3165, "longitude": 78.0322, 
         "soil_type": "loamy", "current_crop": "wheat", "soil_ph": 6.5},
        {"farmer_id": "F002", "latitude": 30.3265, "longitude": 78.0422,
         "soil_type": "loamy", "current_crop": "wheat", "soil_ph": 6.8},
        {"farmer_id": "F003", "latitude": 30.3465, "longitude": 78.0522,
         "soil_type": "clay", "current_crop": "rice", "soil_ph": 7.0},
        {"farmer_id": "F004", "latitude": 30.3565, "longitude": 78.0622,
         "soil_type": "loamy", "current_crop": "wheat", "soil_ph": 6.7},
        {"farmer_id": "F005", "latitude": 31.0000, "longitude": 79.0000,
         "soil_type": "sandy", "current_crop": "maize", "soil_ph": 5.5},
    ]
    
    for fd in farmers_data:
        network.register_farmer(fd)
    
    # Find similar farmers
    print("\n=== Similar to F001 ===")
    similar = network.find_similar_farmers("F001", top_k=5)
    for fid, sim, dist in similar:
        print(f"  {fid}: similarity={sim:.2f}, distance={dist:.2f}km")
    
    # Report disease
    print("\n=== Disease Report ===")
    report = network.report_disease(
        farmer_id="F001",
        disease_name="Brown Spot",
        severity=0.7,
        description="Brown spots appearing on rice leaves"
    )
    print(f"Report ID: {report['report_id']}")
    print(f"Alerts sent: {report['alerts_sent']}")
    
    # Check alerts for similar farmers
    print("\n=== Alerts for F002 ===")
    alerts = network.get_alerts_for_farmer("F002")
    for alert in alerts:
        print(f"  {alert['risk_level']}: {alert['message'][:100]}...")
    
    # Network stats
    print("\n=== Network Stats ===")
    stats = network.get_network_stats()
    print(stats)
