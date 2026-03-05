"""
Vision Engine - Crop Disease Detection using ONNX & YOLO Models
Author: Ankit Negi (@anku251)
Role: AI/ML Engineer - Computer Vision & Disease Detection Models

Supported Models:
- corn_mobile_v2.onnx: Corn diseases (Blight, Rust)
- cotton_disease_v2.onnx: Cotton diseases (Bacterial Blight, Curl Virus)
- rice_mobile_v2.onnx: Rice diseases (Blast, Tungro)
- wheat_mobile_v2.onnx: Wheat diseases (Rust)
- sugarcane_mobile_v2.onnx: Sugarcane detection
- plant_doctor.pt: General YOLOv8 model for leaf scanning
"""

import os
import numpy as np
import onnxruntime as ort
from PIL import Image
from ultralytics import YOLO

# Robust import for pest_engine
try:
    from .pest_detection import pest_engine
except ImportError:
    try:
        from models.pest_detection import pest_engine
    except ImportError:
        pest_engine = None  # Handle gracefully if module is missing

class PlantDoctor:
    def __init__(self):
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(current_dir, "crop_models")
        
        # 1. ONNX MODEL MAP (Matches your files)
        self.onnx_map = {
            "cotton": "cotton_disease_v2.onnx",
            "corn": "corn_mobile_v2.onnx",
            "sugarcane": "sugarcane_mobile_v2.onnx", 
            "wheat": "wheat_mobile_v2.onnx",
            "rice": "rice_mobile_v2.onnx"
        }

        # 2. YOLO MODEL MAP
        self.yolo_map = {
            "general": "plant_doctor.pt"
        }

        # 3. CLASS LABELS
        self.class_indices = {
            "cotton": ['Bacterial Blight', 'Curl Virus', 'Fusarium Wilt', 'Healthy'],
            "corn": ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy'],
            "sugarcane": ['Mosaic', 'Red Rot', 'Rust', 'Healthy'],
            "wheat": ['Brown Rust', 'Healthy', 'Yellow Rust'],
            "rice": ['Blast', 'Blight', 'Tungro']
        }

    def preprocess_onnx(self, image):
        """
        Prepare PIL image for ONNX Runtime (Batch, Height, Width, Channels)
        """
        # Resize to 224x224
        img = image.resize((224, 224)).convert('RGB')
        img_data = np.array(img).astype(np.float32)
        
        # Normalize (1/255.0)
        img_data = img_data / 255.0
        
        # Add Batch Dimension: (224, 224, 3) -> (1, 224, 224, 3)
        img_data = np.expand_dims(img_data, axis=0)
        return img_data

    def predict(self, image, crop_type):
        """
        Main entry point. 
        Args:
            image: PIL Image object (from Streamlit)
            crop_type: String (e.g., 'Rice', 'Pest Detection 🐛')
        """
        crop_key = crop_type.lower().split(" ")[0] # Clean string "Rice" -> "rice"

        # --- ROUTE 1: PEST DETECTION ---
        if "pest" in crop_key:
            if pest_engine is None:
                return "Error: Pest Engine not found", 0.0
            try:
                results = pest_engine.predict(image)
                if results and results[0].boxes.cls.numel() > 0:
                    boxes = results[0].boxes
                    best_conf = boxes.conf.cpu().numpy().max()
                    cls_id = int(boxes.cls.cpu().numpy()[np.argmax(boxes.conf.cpu().numpy())])
                    name = results[0].names[cls_id]
                    return f"Pest: {name}", float(best_conf)
                return "No pest detected", 0.0
            except Exception as e:
                return f"Pest Error: {str(e)}", 0.0

        # --- ROUTE 2: GENERAL PLANT SCAN ---
        if "general" in crop_key:
            path = os.path.join(self.base_path, self.yolo_map["general"])
            if not os.path.exists(path):
                return "Error: General model missing", 0.0
            
            try:
                model = YOLO(path)
                results = model.predict(image, conf=0.4, verbose=False)
                if results[0].probs is not None:
                    probs = results[0].probs
                    top1_idx = probs.top1
                    return results[0].names[top1_idx], float(probs.top1conf)
                return "Healthy", 0.9
            except Exception as e:
                return f"YOLO Error: {str(e)}", 0.0

        # --- ROUTE 3: SPECIFIC CROP DISEASE (ONNX EXPERTS) ---
        if crop_key in self.onnx_map:
            filename = self.onnx_map[crop_key]
            model_path = os.path.join(self.base_path, filename)
            
            if not os.path.exists(model_path):
                return f"Error: Model file {filename} missing", 0.0

            try:
                # 1. Preprocess
                input_tensor = self.preprocess_onnx(image)
                
                # 2. Load ONNX Session (WITH EXPLICIT PROVIDERS)
                # This fixes the "providers required" error
                session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
                
                # 3. Run Inference
                input_name = session.get_inputs()[0].name
                outputs = session.run(None, {input_name: input_tensor})
                
                # 4. Decode Results
                predictions = outputs[0][0]
                predicted_idx = np.argmax(predictions)
                confidence = float(predictions[predicted_idx])
                
                # Map index to class name
                labels = self.class_indices.get(crop_key, [])
                if predicted_idx < len(labels):
                    result_class = labels[predicted_idx]
                else:
                    result_class = f"Unknown Class {predicted_idx}"
                
                return result_class, confidence

            except Exception as e:
                return f"ONNX Error: {str(e)}", 0.0

        return f"Error: No expert found for {crop_key}", 0.0