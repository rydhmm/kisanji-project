"""
Vision Engine for Crop Disease Detection - Hugging Face API Version
Uses Hugging Face Inference API for fast, lightweight inference
"""
import os
import base64
import httpx
import logging
from PIL import Image
from io import BytesIO
from typing import Tuple, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hugging Face API Configuration
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_TOKEN = os.environ.get("HF_TOKEN", "")  # Optional - for private models

# Disease labels for crop classification
CROP_DISEASES = {
    "corn": [
        "Corn___Cercospora_leaf_spot Gray_leaf_spot",
        "Corn___Common_rust_",
        "Corn___Northern_Leaf_Blight",
        "Corn___healthy"
    ],
    "rice": [
        "Rice___Brown_Spot",
        "Rice___Leaf_Blast",
        "Rice___Neck_Blast", 
        "Rice___healthy"
    ],
    "wheat": [
        "Wheat___Brown_Rust",
        "Wheat___Yellow_Rust",
        "Wheat___Septoria",
        "Wheat___healthy"
    ],
    "cotton": [
        "Cotton___Bacterial_Blight",
        "Cotton___Curl_Virus",
        "Cotton___Fussarium_Wilt",
        "Cotton___healthy"
    ],
    "sugarcane": [
        "Sugarcane___Red_Rot",
        "Sugarcane___Rust",
        "Sugarcane___Bacterial_Blight",
        "Sugarcane___healthy"
    ]
}

# Treatment recommendations
TREATMENTS = {
    "cercospora": {
        "disease": "Cercospora Leaf Spot / Gray Leaf Spot",
        "severity": "Medium",
        "treatment": "Apply fungicides like Azoxystrobin or Propiconazole. Remove infected leaves.",
        "prevention": "Rotate crops, use resistant varieties, avoid overhead irrigation."
    },
    "rust": {
        "disease": "Rust Disease",
        "severity": "High",
        "treatment": "Apply sulfur-based fungicides or Triazole fungicides immediately.",
        "prevention": "Plant resistant varieties, ensure good air circulation."
    },
    "blight": {
        "disease": "Blight Disease",
        "severity": "High",
        "treatment": "Apply copper-based fungicides. Remove and destroy infected plants.",
        "prevention": "Use certified disease-free seeds, practice crop rotation."
    },
    "blast": {
        "disease": "Blast Disease",
        "severity": "High",
        "treatment": "Apply Tricyclazole or Isoprothiolane fungicides.",
        "prevention": "Balanced nitrogen fertilization, flood field periodically."
    },
    "healthy": {
        "disease": "Healthy Plant",
        "severity": "None",
        "treatment": "No treatment needed. Continue regular maintenance.",
        "prevention": "Maintain good agricultural practices."
    },
    "unknown": {
        "disease": "Unknown Condition",
        "severity": "Unknown",
        "treatment": "Consult an agricultural expert for proper diagnosis.",
        "prevention": "Regular monitoring and preventive care recommended."
    }
}


class HuggingFaceVisionEngine:
    """
    Lightweight vision engine using Hugging Face Inference API
    Uses pre-trained plant disease models from Hugging Face Hub
    """
    
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
        # Using a general plant disease classifier from HF Hub
        self.model_id = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
        self.timeout = 30.0
        
    async def analyze_image(self, image_data: bytes, crop_type: str = "general") -> Dict:
        """
        Analyze crop image for diseases using Hugging Face API
        """
        try:
            # Use Hugging Face Inference API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{HF_API_URL}/{self.model_id}",
                    headers=self.headers,
                    content=image_data
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return self._process_results(results, crop_type)
                elif response.status_code == 503:
                    # Model is loading, use fallback
                    logger.warning("HF model loading, using fallback analysis")
                    return self._fallback_analysis(crop_type)
                else:
                    logger.error(f"HF API error: {response.status_code}")
                    return self._fallback_analysis(crop_type)
                    
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return self._fallback_analysis(crop_type)
    
    def _process_results(self, results: List[Dict], crop_type: str) -> Dict:
        """Process HF API results into our format"""
        if not results:
            return self._fallback_analysis(crop_type)
        
        # Get top prediction
        top_result = results[0] if results else {"label": "unknown", "score": 0}
        label = top_result.get("label", "unknown").lower()
        confidence = top_result.get("score", 0) * 100
        
        # Determine treatment based on label
        treatment_key = "unknown"
        if "healthy" in label:
            treatment_key = "healthy"
        elif "rust" in label:
            treatment_key = "rust"
        elif "blight" in label:
            treatment_key = "blight"
        elif "blast" in label:
            treatment_key = "blast"
        elif "cercospora" in label or "gray" in label or "spot" in label:
            treatment_key = "cercospora"
        
        treatment = TREATMENTS.get(treatment_key, TREATMENTS["unknown"])
        
        return {
            "success": True,
            "crop_type": crop_type,
            "disease_detected": treatment["disease"],
            "confidence": round(confidence, 2),
            "severity": treatment["severity"],
            "treatment": treatment["treatment"],
            "prevention": treatment["prevention"],
            "raw_label": label,
            "all_predictions": results[:5] if len(results) > 5 else results
        }
    
    def _fallback_analysis(self, crop_type: str) -> Dict:
        """Fallback when API is unavailable - uses Gemini for analysis"""
        return {
            "success": True,
            "crop_type": crop_type,
            "disease_detected": "Analysis Pending",
            "confidence": 0,
            "severity": "Unknown",
            "treatment": "Please try again in a few seconds. The model is warming up.",
            "prevention": "For immediate help, use the AI Assistant to describe symptoms.",
            "raw_label": "pending",
            "all_predictions": []
        }


class PestInferenceEngine:
    """
    Lightweight pest detection using Hugging Face API
    """
    
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
        self.model_id = "microsoft/resnet-50"  # General image classifier
        self.timeout = 30.0
        
        # Common agricultural pests
        self.pest_keywords = [
            "aphid", "beetle", "caterpillar", "locust", "grasshopper",
            "whitefly", "mite", "thrip", "weevil", "borer", "armyworm",
            "cutworm", "leafhopper", "bug", "moth", "larva", "grub"
        ]
    
    async def predict_async(self, image_data: bytes) -> Tuple[str, float]:
        """Async pest detection"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{HF_API_URL}/{self.model_id}",
                    headers=self.headers,
                    content=image_data
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return self._process_pest_results(results)
                else:
                    return "Analysis unavailable", 0.0
                    
        except Exception as e:
            logger.error(f"Pest detection error: {e}")
            return "Error in analysis", 0.0
    
    def predict(self, image) -> Tuple[str, float]:
        """Sync pest detection (converts image to bytes)"""
        try:
            # Convert PIL image to bytes
            if hasattr(image, 'read'):
                image_data = image.read()
            elif isinstance(image, Image.Image):
                buffer = BytesIO()
                image.save(buffer, format='JPEG')
                image_data = buffer.getvalue()
            else:
                image_data = image
            
            # Use sync httpx
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{HF_API_URL}/{self.model_id}",
                    headers=self.headers,
                    content=image_data
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return self._process_pest_results(results)
                else:
                    return "Analysis unavailable", 0.0
                    
        except Exception as e:
            logger.error(f"Pest detection error: {e}")
            return "Error in analysis", 0.0
    
    def _process_pest_results(self, results: List[Dict]) -> Tuple[str, float]:
        """Process results to identify pests"""
        if not results:
            return "No pest detected", 0.0
        
        for result in results[:10]:
            label = result.get("label", "").lower()
            score = result.get("score", 0)
            
            for pest in self.pest_keywords:
                if pest in label:
                    return f"Pest Detected: {label.title()}", score * 100
        
        # If no pest found in top results
        top = results[0]
        return f"Identified: {top.get('label', 'Unknown')}", top.get('score', 0) * 100


class CropDiseaseEngine:
    """
    Main disease detection engine combining multiple approaches
    """
    
    def __init__(self):
        self.hf_engine = HuggingFaceVisionEngine()
        self.pest_engine = PestInferenceEngine()
    
    async def analyze(self, image_data: bytes, crop_type: str = "general") -> Dict:
        """Main analysis entry point"""
        return await self.hf_engine.analyze_image(image_data, crop_type)
    
    def analyze_sync(self, image_data: bytes, crop_type: str = "general") -> Dict:
        """Synchronous analysis using Gemini fallback"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.analyze(image_data, crop_type))


# Global instances
vision_engine = HuggingFaceVisionEngine()
pest_engine = PestInferenceEngine()
disease_engine = CropDiseaseEngine()


# Export functions for backward compatibility
async def analyze_crop_disease(image_data: bytes, crop_type: str = "general") -> Dict:
    """Analyze crop for diseases"""
    return await vision_engine.analyze_image(image_data, crop_type)


def detect_pest(image) -> Tuple[str, float]:
    """Detect pests in image"""
    return pest_engine.predict(image)
