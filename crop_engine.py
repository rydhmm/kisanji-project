import os
import joblib
import numpy as np
from utils.weather_api import get_weather_data

class CropRecommender:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'crop_recommender.pkl')
        
        try:
            self.model = joblib.load(model_path)
            print("✅ Crop Recommender Model Loaded!")
        except FileNotFoundError:
            print(f"❌ Error: Model not found at {model_path}")
            self.model = None

    def predict_crop(self, n, p, k, ph, city, water_sources):
        if not self.model:
            return {"error": "Model not loaded"}

        # 1. Get Live Weather
        weather = get_weather_data(city)
        temp = weather['temperature'] if weather else 25.0
        humidity = weather['humidity'] if weather else 80.0

        # 2. INTERNAL WATER LOGIC (Fixes the TypeError)
        # Instead of float(water_sources), we calculate based on the list contents
        final_rainfall = 0.0
        
        if "Rainfall" in water_sources:
            final_rainfall += 100.0  # Moderate rain value
            
        if "Borewell" in water_sources:
            final_rainfall += 150.0  # Irrigation value
            
        # If both are selected, final_rainfall will be 250.0

        # 3. Predict using the 7 features required by the model
        features = np.array([[n, p, k, temp, humidity, ph, final_rainfall]])
        prediction = self.model.predict(features)
        
        return {
            'crop': prediction[0],
            'temp': temp,
            'humidity': humidity,
            'rainfall_simulated': final_rainfall,
            'water_logic': " + ".join(water_sources) if water_sources else "None"
        }