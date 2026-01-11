import os
import logging
import shutil
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PestInferenceEngine:
    def __init__(self, model_name="yolov8n-cls.pt", conf_threshold=0.25):
        self.conf_threshold = conf_threshold
        # Ensure weights folder exists in src/models/weights/
        self.weights_dir = os.path.join(os.path.dirname(__file__), "weights")
        os.makedirs(self.weights_dir, exist_ok=True)
        
        self.model_path = os.path.join(self.weights_dir, model_name)
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            # 1. Check if model exists locally in src/models/weights/
            if os.path.exists(self.model_path):
                logger.info(f"✅ Loading pest model from {self.model_path}")
                self.model = YOLO(self.model_path)
            else:
                # 2. If not, download it
                logger.info(f"⬇️ Model not found at {self.model_path}. Downloading YOLOv8n-cls...")
                
                # This downloads the file to the current root directory
                self.model = YOLO("yolov8n-cls.pt") 
                
                # Move it to the correct weights folder
                # FIX: Corrected typo from "yolov8n-.pt" to "yolov8n-cls.pt"
                if os.path.exists("yolov8n-cls.pt"):
                    shutil.move("yolov8n-cls.pt", self.model_path)
                    logger.info(f"✅ Model moved to {self.model_path}")
                
                # Reload from new path to be sure
                self.model = YOLO(self.model_path)

        except Exception as e:
            logger.error(f"❌ Pest model load failed: {e}")
            # Fallback: Try to load standard YOLO if classification fails
            try:
                self.model = YOLO("yolov8n.pt") 
            except:
                logger.error("Critical: Could not load any YOLO model.")
                self.model = None

    def predict(self, image_source):
        if self.model is None:
            # Try loading one last time
            self._load_model()
            if self.model is None:
                return [] # Return empty list if model is broken
        
        # Run prediction
        return self.model.predict(image_source, conf=self.conf_threshold, verbose=False)

# Singleton instance
pest_engine = PestInferenceEngine()