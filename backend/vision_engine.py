"""
Vision Engine for Crop Disease Detection
Supports multiple ONNX models for crop-specific disease detection
"""
import os
import sys
import numpy as np
import logging
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import onnxruntime
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    logger.warning("onnxruntime not installed. ONNX models will not work.")
    ONNX_AVAILABLE = False

# Try to import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    logger.warning("ultralytics not installed. YOLO models will not work.")
    YOLO_AVAILABLE = False


class PestInferenceEngine:
    """Engine for pest detection using YOLOv8"""
    
    def __init__(self, model_path: str = None, conf_threshold: float = 0.25):
        self.conf_threshold = conf_threshold
        self.model = None
        
        # Look for model in parent directory or current directory
        if model_path:
            self.model_path = model_path
        else:
            # Check multiple locations
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "..", "yolov8n-cls.pt"),
                os.path.join(os.path.dirname(__file__), "yolov8n-cls.pt"),
                "yolov8n-cls.pt"
            ]
            self.model_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.model_path = path
                    break
        
        if YOLO_AVAILABLE and self.model_path:
            self._load_model()
    
    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                logger.info(f"✅ Loading pest model from {self.model_path}")
                self.model = YOLO(self.model_path)
            else:
                logger.warning(f"⚠️ Model not found at {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Pest model load failed: {e}")
            self.model = None
    
    def predict(self, image) -> Tuple[str, float]:
        """
        Detect pests in image
        Returns: (pest_name, confidence)
        """
        if self.model is None:
            return "Model not available", 0.0
        
        try:
            results = self.model.predict(image, conf=self.conf_threshold, verbose=False)
            
            # Handle classification results
            if results and results[0].probs is not None:
                probs = results[0].probs
                top1_idx = probs.top1
                top1_conf = float(probs.top1conf)
                class_name = results[0].names[top1_idx]
                return class_name, top1_conf
            
            # Handle detection results
            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                best_idx = np.argmax(boxes.conf.cpu().numpy())
                best_conf = float(boxes.conf[best_idx].cpu().numpy())
                cls_id = int(boxes.cls[best_idx].cpu().numpy())
                name = results[0].names[cls_id]
                return f"Pest: {name}", best_conf
            
            return "No pest detected", 0.0
            
        except Exception as e:
            logger.error(f"Pest detection error: {e}")
            return f"Error: {str(e)}", 0.0


class PlantDoctor:
    """
    Multi-crop disease detection engine using ONNX models
    Supports: Cotton, Corn, Sugarcane, Wheat, Rice
    """
    
    def __init__(self, models_dir: str = None):
        # Set base path for models
        if models_dir:
            self.base_path = models_dir
        else:
            # Check parent directory first (where models actually are)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Models are in parent directory
            self.base_path = parent_dir
        
        logger.info(f"PlantDoctor base path: {self.base_path}")
        
        # ONNX MODEL MAP
        self.onnx_map = {
            "cotton": "cotton_disease_v2.onnx",
            "corn": "corn_mobile_v2.onnx",
            "sugarcane": "sugarcane_mobile_v2.onnx",
            "wheat": "wheat_mobile_v2.onnx",
            "rice": "rice_mobile_v2.onnx"
        }
        
        # YOLO MODEL MAP
        self.yolo_map = {
            "general": "plant_doctor.pt"
        }
        
        # CLASS LABELS for each crop model
        self.class_indices = {
            "cotton": ['Bacterial Blight', 'Curl Virus', 'Fusarium Wilt', 'Healthy'],
            "corn": ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy'],
            "sugarcane": ['Mosaic', 'Red Rot', 'Rust', 'Healthy'],
            "wheat": ['Brown Rust', 'Healthy', 'Yellow Rust'],
            "rice": ['Blast', 'Blight', 'Tungro']
        }
        
        # Disease descriptions and treatments
        self.disease_info = {
            # Cotton diseases
            'Bacterial Blight': {
                'description': 'Bacterial disease causing water-soaked lesions on leaves that turn brown with yellow halos.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Streptocycline', 'dosage': '100 ppm', 'timing': 'At first symptoms'},
                    {'name': 'Copper Oxychloride 50% WP', 'dosage': '2.5 kg/ha', 'timing': 'Every 10-15 days'}
                ],
                'preventions': [
                    'Use disease-free seeds',
                    'Treat seeds with Streptocycline 100 ppm',
                    'Avoid overhead irrigation',
                    'Remove and destroy infected plants'
                ]
            },
            'Curl Virus': {
                'description': 'Viral disease transmitted by whiteflies causing leaf curling and stunted growth.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Imidacloprid 17.8% SL', 'dosage': '100 ml/ha', 'timing': 'For whitefly control'},
                    {'name': 'Thiamethoxam 25% WG', 'dosage': '100 g/ha', 'timing': 'Every 15 days'}
                ],
                'preventions': [
                    'Control whitefly population',
                    'Use virus-resistant varieties',
                    'Remove infected plants immediately',
                    'Avoid planting near infected fields'
                ]
            },
            'Fusarium Wilt': {
                'description': 'Soil-borne fungal disease causing wilting, yellowing and vascular discoloration.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Carbendazim 50% WP', 'dosage': '2 g/L water', 'timing': 'Soil drench at planting'},
                    {'name': 'Trichoderma viride', 'dosage': '4 kg/ha', 'timing': 'Before sowing'}
                ],
                'preventions': [
                    'Use resistant varieties',
                    'Practice crop rotation',
                    'Soil solarization',
                    'Good drainage'
                ]
            },
            # Corn diseases
            'Blight': {
                'description': 'Fungal disease causing large tan lesions on leaves, reducing photosynthesis.',
                'severity': 'Moderate to High',
                'treatments': [
                    {'name': 'Mancozeb 75% WP', 'dosage': '2.5 kg/ha', 'timing': 'At disease onset'},
                    {'name': 'Propiconazole 25% EC', 'dosage': '500 ml/ha', 'timing': 'Every 10-14 days'}
                ],
                'preventions': [
                    'Plant resistant hybrids',
                    'Rotate crops',
                    'Destroy crop residues',
                    'Balanced fertilization'
                ]
            },
            'Common Rust': {
                'description': 'Fungal disease producing reddish-brown pustules on leaves.',
                'severity': 'Moderate',
                'treatments': [
                    {'name': 'Mancozeb 75% WP', 'dosage': '2.5 kg/ha', 'timing': 'Early detection'},
                    {'name': 'Hexaconazole 5% SC', 'dosage': '1 L/ha', 'timing': 'Repeat after 15 days'}
                ],
                'preventions': [
                    'Use rust-resistant varieties',
                    'Early planting',
                    'Adequate plant spacing'
                ]
            },
            'Gray Leaf Spot': {
                'description': 'Fungal disease causing rectangular gray to tan lesions.',
                'severity': 'Moderate to High',
                'treatments': [
                    {'name': 'Azoxystrobin 23% SC', 'dosage': '500 ml/ha', 'timing': 'At first symptoms'},
                    {'name': 'Propiconazole 25% EC', 'dosage': '500 ml/ha', 'timing': 'Every 14 days'}
                ],
                'preventions': [
                    'Resistant hybrids',
                    'Crop rotation (2+ years)',
                    'Tillage to bury residue'
                ]
            },
            # Sugarcane diseases
            'Mosaic': {
                'description': 'Viral disease causing yellow-green mottling pattern on leaves.',
                'severity': 'Moderate',
                'treatments': [
                    {'name': 'Imidacloprid 17.8% SL', 'dosage': '100 ml/ha', 'timing': 'Vector control'},
                    {'name': 'Dimethoate 30% EC', 'dosage': '1 L/ha', 'timing': 'For aphid control'}
                ],
                'preventions': [
                    'Use virus-free setts',
                    'Roguing of infected plants',
                    'Control aphid vectors',
                    'Resistant varieties'
                ]
            },
            'Red Rot': {
                'description': 'Fungal disease causing red internal tissue with white spots.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Carbendazim 50% WP', 'dosage': '500 g/ha', 'timing': 'Sett treatment'},
                    {'name': 'Thiophanate Methyl', 'dosage': '500 g/ha', 'timing': 'Before planting'}
                ],
                'preventions': [
                    'Use disease-free setts',
                    'Hot water treatment (50°C for 2 hours)',
                    'Resistant varieties',
                    'Remove ratoon of infected fields'
                ]
            },
            'Rust': {
                'description': 'Fungal disease producing orange-brown pustules on leaves.',
                'severity': 'Moderate',
                'treatments': [
                    {'name': 'Mancozeb 75% WP', 'dosage': '2 kg/ha', 'timing': 'At first symptoms'},
                    {'name': 'Propiconazole 25% EC', 'dosage': '500 ml/ha', 'timing': 'Every 15 days'}
                ],
                'preventions': [
                    'Resistant varieties',
                    'Avoid excess nitrogen',
                    'Good field drainage'
                ]
            },
            # Wheat diseases
            'Brown Rust': {
                'description': 'Fungal disease causing orange-brown pustules on leaves and stems.',
                'severity': 'Moderate to High',
                'treatments': [
                    {'name': 'Propiconazole 25% EC', 'dosage': '500 ml/ha', 'timing': 'At first symptoms'},
                    {'name': 'Tebuconazole 25% EC', 'dosage': '500 ml/ha', 'timing': 'Repeat after 15 days'}
                ],
                'preventions': [
                    'Grow resistant varieties',
                    'Early sowing',
                    'Avoid late nitrogen application',
                    'Destroy volunteer wheat'
                ]
            },
            'Yellow Rust': {
                'description': 'Fungal disease causing yellow stripes of pustules along leaf veins.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Propiconazole 25% EC', 'dosage': '500 ml/ha', 'timing': 'Immediately on detection'},
                    {'name': 'Tebuconazole 250 EC', 'dosage': '500 ml/ha', 'timing': 'Every 10-14 days'}
                ],
                'preventions': [
                    'Use resistant varieties',
                    'Early sowing',
                    'Balanced fertilization',
                    'Monitor regularly'
                ]
            },
            # Rice diseases
            'Blast': {
                'description': 'Fungal disease causing diamond-shaped lesions with gray centers.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Tricyclazole 75% WP', 'dosage': '300 g/ha', 'timing': 'At first symptoms'},
                    {'name': 'Isoprothiolane 40% EC', 'dosage': '750 ml/ha', 'timing': 'Every 10-15 days'}
                ],
                'preventions': [
                    'Resistant varieties',
                    'Avoid excess nitrogen',
                    'Maintain water level',
                    'Seed treatment with Carbendazim'
                ]
            },
            'Blight': {
                'description': 'Bacterial leaf blight causing water-soaked lesions that turn yellow.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Streptocycline', 'dosage': '150 ppm', 'timing': 'At first symptoms'},
                    {'name': 'Copper Hydroxide', 'dosage': '2 kg/ha', 'timing': 'Every 10 days'}
                ],
                'preventions': [
                    'Use certified seeds',
                    'Balanced NPK fertilization',
                    'Good drainage',
                    'Avoid excess nitrogen'
                ]
            },
            'Tungro': {
                'description': 'Viral disease causing yellow-orange discoloration and stunting.',
                'severity': 'High',
                'treatments': [
                    {'name': 'Carbofuran 3G', 'dosage': '25 kg/ha', 'timing': 'Before transplanting'},
                    {'name': 'Imidacloprid 17.8% SL', 'dosage': '100 ml/ha', 'timing': 'Vector control'}
                ],
                'preventions': [
                    'Resistant varieties',
                    'Synchronous planting',
                    'Control green leafhopper',
                    'Remove infected plants'
                ]
            },
            # Healthy
            'Healthy': {
                'description': 'No disease detected. The plant appears healthy.',
                'severity': 'None',
                'treatments': [],
                'preventions': [
                    'Continue regular monitoring',
                    'Maintain proper nutrition',
                    'Ensure adequate water management',
                    'Practice good field hygiene'
                ]
            }
        }
        
        # Initialize pest engine
        pest_model_path = os.path.join(self.base_path, "yolov8n-cls.pt")
        self.pest_engine = PestInferenceEngine(model_path=pest_model_path)
        
        # Log available models
        self._check_available_models()
    
    def _check_available_models(self):
        """Check which models are available"""
        self.available_models = {}
        
        for crop, filename in self.onnx_map.items():
            path = os.path.join(self.base_path, filename)
            self.available_models[crop] = os.path.exists(path)
            if self.available_models[crop]:
                logger.info(f"✅ Found model: {filename}")
            else:
                logger.warning(f"⚠️ Missing model: {filename}")
        
        # Check YOLO model
        yolo_path = os.path.join(self.base_path, self.yolo_map["general"])
        self.available_models["general"] = os.path.exists(yolo_path)
        
        # Check pest model
        self.available_models["pest"] = self.pest_engine.model is not None
    
    def get_available_crops(self) -> List[Dict]:
        """Get list of crops with available models"""
        crops = []
        
        for crop, available in self.available_models.items():
            if crop in self.onnx_map:
                crops.append({
                    "id": crop,
                    "name": crop.capitalize(),
                    "model": self.onnx_map[crop],
                    "available": available,
                    "diseases": self.class_indices.get(crop, [])
                })
        
        # Add special detection types
        crops.append({
            "id": "general",
            "name": "General Plant Scan",
            "model": self.yolo_map.get("general", ""),
            "available": self.available_models.get("general", False),
            "diseases": []
        })
        
        crops.append({
            "id": "pest",
            "name": "Pest Detection 🐛",
            "model": "yolov8n-cls.pt",
            "available": self.available_models.get("pest", False),
            "diseases": []
        })
        
        return crops
    
    def preprocess_onnx(self, image: Image.Image) -> np.ndarray:
        """Prepare PIL image for ONNX Runtime"""
        # Resize to 224x224
        img = image.resize((224, 224)).convert('RGB')
        img_data = np.array(img).astype(np.float32)
        
        # Normalize (0-1)
        img_data = img_data / 255.0
        
        # Add batch dimension: (224, 224, 3) -> (1, 224, 224, 3)
        img_data = np.expand_dims(img_data, axis=0)
        return img_data
    
    def predict(self, image: Image.Image, crop_type: str) -> Dict:
        """
        Main prediction method
        
        Args:
            image: PIL Image object
            crop_type: String (e.g., 'rice', 'wheat', 'pest', 'general')
        
        Returns:
            Dict with disease info, confidence, treatments, etc.
        """
        crop_key = crop_type.lower().strip()
        
        # --- ROUTE 1: PEST DETECTION ---
        if crop_key == "pest" or "pest" in crop_key:
            return self._detect_pest(image)
        
        # --- ROUTE 2: GENERAL PLANT SCAN ---
        if crop_key == "general":
            return self._general_scan(image)
        
        # --- ROUTE 3: SPECIFIC CROP DISEASE (ONNX) ---
        if crop_key in self.onnx_map:
            return self._detect_crop_disease(image, crop_key)
        
        return {
            "success": False,
            "error": f"No model found for crop: {crop_type}",
            "disease": None,
            "confidence": 0.0
        }
    
    def _detect_pest(self, image: Image.Image) -> Dict:
        """Detect pests using YOLO model"""
        if not self.available_models.get("pest", False):
            return {
                "success": False,
                "error": "Pest detection model not available",
                "disease": None,
                "confidence": 0.0
            }
        
        try:
            pest_name, confidence = self.pest_engine.predict(image)
            
            return {
                "success": True,
                "disease": pest_name,
                "confidence": round(confidence * 100, 2),
                "severity": "Moderate" if confidence > 0.5 else "Low",
                "description": f"Detected: {pest_name}",
                "crop_type": "pest",
                "treatments": [
                    {"name": "Neem Oil", "dosage": "5 ml/L water", "timing": "Evening spray"},
                    {"name": "Imidacloprid 17.8% SL", "dosage": "100 ml/ha", "timing": "Morning application"}
                ],
                "preventions": [
                    "Regular field monitoring",
                    "Use pheromone traps",
                    "Maintain field hygiene",
                    "Encourage natural predators"
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "disease": None,
                "confidence": 0.0
            }
    
    def _general_scan(self, image: Image.Image) -> Dict:
        """General plant health scan using YOLO"""
        if not YOLO_AVAILABLE:
            return {
                "success": False,
                "error": "YOLO not available",
                "disease": None,
                "confidence": 0.0
            }
        
        model_path = os.path.join(self.base_path, self.yolo_map["general"])
        
        if not os.path.exists(model_path):
            return {
                "success": False,
                "error": f"General model not found at {model_path}",
                "disease": None,
                "confidence": 0.0
            }
        
        try:
            model = YOLO(model_path)
            results = model.predict(image, conf=0.4, verbose=False)
            
            if results[0].probs is not None:
                probs = results[0].probs
                top1_idx = probs.top1
                disease_name = results[0].names[top1_idx]
                confidence = float(probs.top1conf)
                
                info = self.disease_info.get(disease_name, {})
                
                return {
                    "success": True,
                    "disease": disease_name,
                    "confidence": round(confidence * 100, 2),
                    "severity": info.get("severity", "Unknown"),
                    "description": info.get("description", f"Detected: {disease_name}"),
                    "crop_type": "general",
                    "treatments": info.get("treatments", []),
                    "preventions": info.get("preventions", [])
                }
            
            return {
                "success": True,
                "disease": "Healthy",
                "confidence": 90.0,
                "severity": "None",
                "description": "No disease detected. Plant appears healthy.",
                "crop_type": "general",
                "treatments": [],
                "preventions": ["Continue regular monitoring"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "disease": None,
                "confidence": 0.0
            }
    
    def _detect_crop_disease(self, image: Image.Image, crop_key: str) -> Dict:
        """Detect disease for specific crop using ONNX model"""
        if not ONNX_AVAILABLE:
            return {
                "success": False,
                "error": "ONNX Runtime not available",
                "disease": None,
                "confidence": 0.0
            }
        
        filename = self.onnx_map[crop_key]
        model_path = os.path.join(self.base_path, filename)
        
        if not os.path.exists(model_path):
            return {
                "success": False,
                "error": f"Model file {filename} not found",
                "disease": None,
                "confidence": 0.0
            }
        
        try:
            # Preprocess image
            input_tensor = self.preprocess_onnx(image)
            
            # Create ONNX session
            session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            
            # Run inference
            input_name = session.get_inputs()[0].name
            outputs = session.run(None, {input_name: input_tensor})
            
            # Decode results
            predictions = outputs[0][0]
            predicted_idx = np.argmax(predictions)
            confidence = float(predictions[predicted_idx])
            
            # Map index to class name
            labels = self.class_indices.get(crop_key, [])
            if predicted_idx < len(labels):
                disease_name = labels[predicted_idx]
            else:
                disease_name = f"Unknown Class {predicted_idx}"
            
            # Get disease info
            info = self.disease_info.get(disease_name, {})
            
            return {
                "success": True,
                "disease": disease_name,
                "confidence": round(confidence * 100, 2),
                "severity": info.get("severity", "Unknown"),
                "description": info.get("description", f"Detected: {disease_name} in {crop_key.capitalize()}"),
                "crop_type": crop_key,
                "treatments": info.get("treatments", []),
                "preventions": info.get("preventions", [])
            }
            
        except Exception as e:
            logger.error(f"ONNX inference error: {e}")
            return {
                "success": False,
                "error": str(e),
                "disease": None,
                "confidence": 0.0
            }


# Singleton instance
_plant_doctor = None

def get_plant_doctor() -> PlantDoctor:
    """Get or create PlantDoctor instance"""
    global _plant_doctor
    if _plant_doctor is None:
        _plant_doctor = PlantDoctor()
    return _plant_doctor
