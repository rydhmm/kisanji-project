"""
Crop Recommendation Engine
Uses trained ML model with live weather data for crop recommendations

Author: Ankit Negi (@anku251)
Role: AI/ML Engineer - Crop Recommendation System & Weather API Integration
"""
import os
import sys
import logging
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for model access
PARENT_DIR = Path(__file__).parent.parent
MODEL_PATH = PARENT_DIR / "crop_recommender.pkl"

class CropRecommendationEngine:
    """
    ML-based crop recommendation engine using trained model
    with live weather data integration
    """
    
    # Crop information database
    CROP_INFO = {
        'rice': {
            'name': 'Rice (Dhaan)',
            'hindi': 'धान',
            'season': 'Kharif',
            'duration': '120-150 days',
            'yield': '45-55 quintals/hectare',
            'water_requirement': 'High',
            'image': 'https://images.pexels.com/photos/2589457/pexels-photo-2589457.jpeg'
        },
        'wheat': {
            'name': 'Wheat (Gehu)',
            'hindi': 'गेहूं',
            'season': 'Rabi',
            'duration': '120-140 days',
            'yield': '40-50 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/265216/pexels-photo-265216.jpeg'
        },
        'maize': {
            'name': 'Maize (Makka)',
            'hindi': 'मक्का',
            'season': 'Kharif/Rabi',
            'duration': '90-120 days',
            'yield': '50-60 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/547263/pexels-photo-547263.jpeg'
        },
        'chickpea': {
            'name': 'Chickpea (Chana)',
            'hindi': 'चना',
            'season': 'Rabi',
            'duration': '95-105 days',
            'yield': '15-20 quintals/hectare',
            'water_requirement': 'Low',
            'image': 'https://images.pexels.com/photos/4110251/pexels-photo-4110251.jpeg'
        },
        'kidneybeans': {
            'name': 'Kidney Beans (Rajma)',
            'hindi': 'राजमा',
            'season': 'Kharif',
            'duration': '90-120 days',
            'yield': '12-15 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/1459339/pexels-photo-1459339.jpeg'
        },
        'pigeonpeas': {
            'name': 'Pigeon Peas (Arhar)',
            'hindi': 'अरहर',
            'season': 'Kharif',
            'duration': '150-180 days',
            'yield': '10-15 quintals/hectare',
            'water_requirement': 'Low',
            'image': 'https://images.pexels.com/photos/4110256/pexels-photo-4110256.jpeg'
        },
        'mothbeans': {
            'name': 'Moth Beans',
            'hindi': 'मोठ',
            'season': 'Kharif',
            'duration': '60-75 days',
            'yield': '5-8 quintals/hectare',
            'water_requirement': 'Very Low',
            'image': 'https://images.pexels.com/photos/4110251/pexels-photo-4110251.jpeg'
        },
        'mungbean': {
            'name': 'Mung Bean (Moong)',
            'hindi': 'मूंग',
            'season': 'Kharif/Zaid',
            'duration': '60-75 days',
            'yield': '8-12 quintals/hectare',
            'water_requirement': 'Low',
            'image': 'https://images.pexels.com/photos/4110256/pexels-photo-4110256.jpeg'
        },
        'blackgram': {
            'name': 'Black Gram (Urad)',
            'hindi': 'उड़द',
            'season': 'Kharif',
            'duration': '75-90 days',
            'yield': '8-12 quintals/hectare',
            'water_requirement': 'Low',
            'image': 'https://images.pexels.com/photos/4110251/pexels-photo-4110251.jpeg'
        },
        'lentil': {
            'name': 'Lentil (Masoor)',
            'hindi': 'मसूर',
            'season': 'Rabi',
            'duration': '100-120 days',
            'yield': '10-15 quintals/hectare',
            'water_requirement': 'Low',
            'image': 'https://images.pexels.com/photos/4110256/pexels-photo-4110256.jpeg'
        },
        'pomegranate': {
            'name': 'Pomegranate (Anar)',
            'hindi': 'अनार',
            'season': 'Year-round',
            'duration': '150-180 days',
            'yield': '100-150 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/65256/pomegranate-open-cores-fruit-65256.jpeg'
        },
        'banana': {
            'name': 'Banana (Kela)',
            'hindi': 'केला',
            'season': 'Year-round',
            'duration': '12-14 months',
            'yield': '250-400 quintals/hectare',
            'water_requirement': 'High',
            'image': 'https://images.pexels.com/photos/1093038/pexels-photo-1093038.jpeg'
        },
        'mango': {
            'name': 'Mango (Aam)',
            'hindi': 'आम',
            'season': 'Summer',
            'duration': '4-5 months',
            'yield': '80-100 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/918643/pexels-photo-918643.jpeg'
        },
        'grapes': {
            'name': 'Grapes (Angoor)',
            'hindi': 'अंगूर',
            'season': 'Year-round',
            'duration': '3-4 months',
            'yield': '200-250 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/708777/pexels-photo-708777.jpeg'
        },
        'watermelon': {
            'name': 'Watermelon (Tarbooz)',
            'hindi': 'तरबूज',
            'season': 'Summer',
            'duration': '80-110 days',
            'yield': '300-400 quintals/hectare',
            'water_requirement': 'High',
            'image': 'https://images.pexels.com/photos/1313267/pexels-photo-1313267.jpeg'
        },
        'muskmelon': {
            'name': 'Muskmelon (Kharbooja)',
            'hindi': 'खरबूजा',
            'season': 'Summer',
            'duration': '80-100 days',
            'yield': '150-200 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/2063569/pexels-photo-2063569.jpeg'
        },
        'apple': {
            'name': 'Apple (Seb)',
            'hindi': 'सेब',
            'season': 'Temperate',
            'duration': '150-180 days',
            'yield': '80-120 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/209439/pexels-photo-209439.jpeg'
        },
        'orange': {
            'name': 'Orange (Santra)',
            'hindi': 'संतरा',
            'season': 'Winter',
            'duration': '9-12 months',
            'yield': '120-180 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/207085/pexels-photo-207085.jpeg'
        },
        'papaya': {
            'name': 'Papaya (Papita)',
            'hindi': 'पपीता',
            'season': 'Year-round',
            'duration': '9-11 months',
            'yield': '400-600 quintals/hectare',
            'water_requirement': 'High',
            'image': 'https://images.pexels.com/photos/5945848/pexels-photo-5945848.jpeg'
        },
        'coconut': {
            'name': 'Coconut (Nariyal)',
            'hindi': 'नारियल',
            'season': 'Year-round',
            'duration': 'Perennial',
            'yield': '100-150 nuts/tree/year',
            'water_requirement': 'High',
            'image': 'https://images.pexels.com/photos/3049900/pexels-photo-3049900.jpeg'
        },
        'cotton': {
            'name': 'Cotton (Kapas)',
            'hindi': 'कपास',
            'season': 'Kharif',
            'duration': '150-180 days',
            'yield': '15-20 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/3720370/pexels-photo-3720370.jpeg'
        },
        'jute': {
            'name': 'Jute (Pat)',
            'hindi': 'पटसन',
            'season': 'Kharif',
            'duration': '120-150 days',
            'yield': '20-25 quintals/hectare',
            'water_requirement': 'High',
            'image': 'https://images.pexels.com/photos/4503273/pexels-photo-4503273.jpeg'
        },
        'coffee': {
            'name': 'Coffee',
            'hindi': 'कॉफी',
            'season': 'Year-round',
            'duration': 'Perennial',
            'yield': '10-15 quintals/hectare',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/1695052/pexels-photo-1695052.jpeg'
        }
    }
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model"""
        try:
            if MODEL_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
                self.model_loaded = True
                logger.info(f"✅ Crop Recommender Model Loaded from {MODEL_PATH}")
            else:
                logger.warning(f"⚠️ Model not found at {MODEL_PATH}")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model_loaded = False
    
    def get_crop_info(self, crop_name: str) -> Dict[str, Any]:
        """Get detailed information about a crop"""
        crop_key = crop_name.lower().replace(' ', '')
        return self.CROP_INFO.get(crop_key, {
            'name': crop_name.title(),
            'hindi': crop_name,
            'season': 'Unknown',
            'duration': 'Unknown',
            'yield': 'Unknown',
            'water_requirement': 'Medium',
            'image': 'https://images.pexels.com/photos/2132171/pexels-photo-2132171.jpeg'
        })
    
    def predict_with_model(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float
    ) -> Dict[str, Any]:
        """
        Get crop prediction using the trained ML model
        
        Args:
            nitrogen: Nitrogen content in soil (N)
            phosphorus: Phosphorus content in soil (P)
            potassium: Potassium content in soil (K)
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            ph: Soil pH value
            rainfall: Rainfall in mm
            
        Returns:
            Prediction result with crop recommendation
        """
        if not self.model_loaded:
            return {
                "success": False,
                "error": "Model not loaded",
                "fallback": True
            }
        
        try:
            # Prepare features for model (7 features: N, P, K, temp, humidity, ph, rainfall)
            features = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
            
            # Get prediction
            prediction = self.model.predict(features)
            crop_name = prediction[0]
            
            # Get probability if available
            confidence = 90  # Default confidence
            if hasattr(self.model, 'predict_proba'):
                try:
                    probabilities = self.model.predict_proba(features)
                    confidence = round(max(probabilities[0]) * 100, 1)
                except:
                    pass
            
            # Get crop info
            crop_info = self.get_crop_info(crop_name)
            
            return {
                "success": True,
                "crop": crop_name,
                "confidence": confidence,
                "crop_info": crop_info,
                "input_features": {
                    "N": nitrogen,
                    "P": phosphorus,
                    "K": potassium,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def recommend_crops(
        self,
        temperature: float,
        humidity: float,
        soil_type: str = "loamy",
        water_source: str = "rainfall",
        ph: float = 6.5,
        nitrogen: float = 50,
        phosphorus: float = 50,
        potassium: float = 50
    ) -> List[Dict[str, Any]]:
        """
        Get multiple crop recommendations based on conditions
        """
        recommendations = []
        
        # Calculate rainfall based on water source
        rainfall_map = {
            "rainfall": 100,
            "irrigation": 180,
            "both": 250,
            "borewell": 150,
            "canal": 200
        }
        rainfall = rainfall_map.get(water_source.lower(), 100)
        
        # Adjust for soil type
        soil_adjustments = {
            "clay": {"rainfall": 50, "crops": ["rice", "wheat"]},
            "sandy": {"rainfall": -30, "crops": ["groundnut", "millet"]},
            "loamy": {"rainfall": 0, "crops": ["wheat", "maize", "vegetables"]},
            "black": {"rainfall": 20, "crops": ["cotton", "soybean"]},
            "red": {"rainfall": -10, "crops": ["groundnut", "millets"]}
        }
        
        adjustment = soil_adjustments.get(soil_type.lower(), {"rainfall": 0, "crops": []})
        rainfall += adjustment["rainfall"]
        
        # Use ML model if available
        if self.model_loaded:
            result = self.predict_with_model(
                nitrogen, phosphorus, potassium,
                temperature, humidity, ph, rainfall
            )
            
            if result.get("success"):
                crop_info = result["crop_info"]
                recommendations.append({
                    "crop": result["crop"],
                    "confidence": result["confidence"],
                    "season": crop_info.get("season", "Unknown"),
                    "duration": crop_info.get("duration", "Unknown"),
                    "yield": crop_info.get("yield", "Unknown"),
                    "water_requirement": crop_info.get("water_requirement", "Medium"),
                    "reason": f"ML model prediction based on soil (NPK: {nitrogen}/{phosphorus}/{potassium}) and weather (Temp: {temperature}°C, Humidity: {humidity}%)",
                    "image": crop_info.get("image", ""),
                    "source": "ml_model"
                })
        
        # Add rule-based recommendations as supplements
        rule_based = self._get_rule_based_recommendations(
            temperature, humidity, soil_type, rainfall
        )
        
        # Merge and deduplicate
        existing_crops = {r["crop"].lower() for r in recommendations}
        for rec in rule_based:
            if rec["crop"].lower() not in existing_crops:
                recommendations.append(rec)
                existing_crops.add(rec["crop"].lower())
        
        # Return top 5 recommendations
        return recommendations[:5]
    
    def _get_rule_based_recommendations(
        self,
        temperature: float,
        humidity: float,
        soil_type: str,
        rainfall: float
    ) -> List[Dict[str, Any]]:
        """Get rule-based crop recommendations"""
        recommendations = []
        
        # Temperature-based recommendations
        if temperature >= 25 and temperature <= 35:
            if humidity >= 60:
                recommendations.extend([
                    self._create_recommendation("Rice", 88, "High humidity suits paddy cultivation"),
                    self._create_recommendation("Sugarcane", 85, "Good moisture conditions for sugarcane"),
                ])
            else:
                recommendations.extend([
                    self._create_recommendation("Maize", 85, "Moderate humidity preferred"),
                    self._create_recommendation("Cotton", 82, "Suitable temperature range"),
                ])
        elif temperature >= 15 and temperature < 25:
            recommendations.extend([
                self._create_recommendation("Wheat", 92, "Optimal cool weather for wheat"),
                self._create_recommendation("Mustard", 85, "Suitable temperature for oil seed"),
                self._create_recommendation("Potato", 80, "Cool weather crop"),
            ])
        elif temperature < 15:
            recommendations.extend([
                self._create_recommendation("Peas", 85, "Cold tolerant crop"),
                self._create_recommendation("Cabbage", 80, "Winter vegetable"),
            ])
        else:  # > 35
            recommendations.extend([
                self._create_recommendation("Millets", 85, "Drought tolerant"),
                self._create_recommendation("Groundnut", 80, "Heat tolerant crop"),
            ])
        
        # Soil type specific
        if soil_type.lower() == "clay":
            recommendations.append(self._create_recommendation("Rice", 90, "Clay soil retains water well"))
        elif soil_type.lower() == "sandy":
            recommendations.append(self._create_recommendation("Groundnut", 88, "Sandy soil is ideal"))
        elif soil_type.lower() == "loamy":
            recommendations.append(self._create_recommendation("Vegetables", 90, "Excellent soil for vegetables"))
        
        return recommendations
    
    def _create_recommendation(self, crop: str, confidence: int, reason: str) -> Dict[str, Any]:
        """Create a recommendation dict"""
        crop_info = self.get_crop_info(crop)
        return {
            "crop": crop,
            "confidence": confidence,
            "season": crop_info.get("season", "Unknown"),
            "duration": crop_info.get("duration", "Unknown"),
            "yield": crop_info.get("yield", "Unknown"),
            "water_requirement": crop_info.get("water_requirement", "Medium"),
            "reason": reason,
            "image": crop_info.get("image", ""),
            "source": "rule_based"
        }


# Singleton instance
_engine = None

def get_crop_engine() -> CropRecommendationEngine:
    """Get or create crop recommendation engine"""
    global _engine
    if _engine is None:
        _engine = CropRecommendationEngine()
    return _engine


# Test if run directly
if __name__ == "__main__":
    engine = get_crop_engine()
    print(f"Model loaded: {engine.model_loaded}")
    
    # Test prediction
    result = engine.recommend_crops(
        temperature=28,
        humidity=70,
        soil_type="loamy",
        water_source="rainfall",
        nitrogen=50,
        phosphorus=50,
        potassium=50
    )
    
    for r in result:
        print(f"- {r['crop']}: {r['confidence']}% ({r['reason'][:50]}...)")
