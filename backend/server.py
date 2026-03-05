"""
KisanJi FastAPI Server - Main Application Entry Point
Authors: Saurav Beri (@sauravberi16), Rajat Pundir (@Rajatpundir7)
Roles: Backend API Development, Database Integration, Feature Routing
"""

from fastapi import FastAPI, APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import certifi
import httpx
import shutil

# Add backend directory to path for local imports
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Import custom engines (after path setup)
from crop_recommender import get_crop_engine
from translation_service import get_translation_service
from farmer_alert_network import get_farmer_network, get_alert_rl
from alert_service import (
    get_alert_service, get_location_service, get_notification_service,
    FarmerLocationUpdate, FarmerRegistration, DiseaseReport, NotificationPreferences
)

load_dotenv(ROOT_DIR / '.env')

# Create directories for voice files
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
MARKET_API_KEY = os.environ.get('MARKET_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# MongoDB connection with TLS certificate for Atlas
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Kisan.JI API", description="Smart Agriculture Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# =====================================
# PYDANTIC MODELS
# =====================================

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# User Models
class UserCreate(BaseModel):
    name: str
    phone: str
    password: Optional[str] = None
    role: str = "farmer"
    preferred_language: str = "en"
    voice_enabled: bool = True

class UserLogin(BaseModel):
    phone: str
    password: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    phone: str
    role: str
    preferred_language: str
    voice_enabled: bool
    created_at: Optional[datetime] = None

class FarmerProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    land_size_hectare: float
    soil_type: str
    irrigation_type: str

# Market Price Model
class MarketPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    crop_name: str
    mandi_name: str
    price_per_quintal: int
    date: str

# Weather Model
class WeatherData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    village_id: str
    date: str
    rainfall_mm: int
    temperature: int
    alert: Optional[str] = None

# Scheme Model
class Scheme(BaseModel):
    model_config = ConfigDict(extra="ignore")
    scheme_name: str
    description: str

# Village Model
class Village(BaseModel):
    model_config = ConfigDict(extra="ignore")
    village_name: str
    district: str
    state: str
    latitude: float
    longitude: float

# Crop Model
class Crop(BaseModel):
    model_config = ConfigDict(extra="ignore")
    crop_name: str
    season: str

# Disease Model
class Disease(BaseModel):
    model_config = ConfigDict(extra="ignore")
    crop_name: str
    disease_name: str
    disease_image_url: List[str]

# Advisory Model
class Advisory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    farmer_id: str
    field_id: str
    advice_type: str
    message: str
    created_at: str


# =====================================
# HEALTH CHECK ROUTES
# =====================================

@api_router.get("/")
async def root():
    return {"message": "Kisan.JI API is running!", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    try:
        # Test database connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# =====================================
# USER / AUTH ROUTES
# =====================================

@api_router.post("/auth/register")
async def register_user(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"phone": user.phone})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this phone number already exists")
    
    user_dict = user.model_dump()
    user_dict["created_at"] = datetime.now(timezone.utc)
    result = await db.users.insert_one(user_dict)
    
    return {
        "id": str(result.inserted_id),
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "preferred_language": user.preferred_language,
        "voice_enabled": user.voice_enabled,
        "message": "Registration successful"
    }

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    user = await db.users.find_one({"phone": login_data.phone})
    if not user:
        # For demo purposes, create a user if not found
        return {
            "id": "demo_user",
            "name": "Farmer",
            "phone": login_data.phone,
            "role": "farmer",
            "preferred_language": "en",
            "voice_enabled": True,
            "message": "Demo login successful"
        }
    
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "phone": user["phone"],
        "role": user.get("role", "farmer"),
        "preferred_language": user.get("preferred_language", "en"),
        "voice_enabled": user.get("voice_enabled", True),
        "message": "Login successful"
    }

@api_router.get("/users")
async def get_users():
    users = await db.users.find({}).to_list(1000)
    for user in users:
        user["id"] = str(user.pop("_id"))
    return users

@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    from bson import ObjectId
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user["id"] = str(user.pop("_id"))
        return user
    except:
        raise HTTPException(status_code=404, detail="User not found")

@api_router.get("/farmer-profile/{user_id}")
async def get_farmer_profile(user_id: str):
    profile = await db.farmer_profile.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        return {"message": "No profile found", "user_id": user_id}
    return profile

@api_router.post("/farmer-profile")
async def create_farmer_profile(profile: FarmerProfile):
    profile_dict = profile.model_dump()
    await db.farmer_profile.update_one(
        {"user_id": profile.user_id},
        {"$set": profile_dict},
        upsert=True
    )
    return {"message": "Profile saved successfully", **profile_dict}


# =====================================
# MARKET PRICES ROUTES
# =====================================

@api_router.get("/market-prices")
async def get_market_prices(
    crop_name: Optional[str] = Query(None, description="Filter by crop name"),
    mandi_name: Optional[str] = Query(None, description="Filter by mandi name")
):
    query = {}
    if crop_name:
        query["crop_name"] = {"$regex": crop_name, "$options": "i"}
    if mandi_name:
        query["mandi_name"] = {"$regex": mandi_name, "$options": "i"}
    
    prices = await db.market_prices.find(query, {"_id": 0}).to_list(1000)
    return prices

@api_router.post("/market-prices")
async def add_market_price(price: MarketPrice):
    price_dict = price.model_dump()
    await db.market_prices.insert_one(price_dict)
    return {"message": "Market price added successfully", **price_dict}


# =====================================
# WEATHER ROUTES
# =====================================

@api_router.get("/weather")
async def get_weather_data(village_id: Optional[str] = None):
    query = {}
    if village_id:
        query["village_id"] = village_id
    
    weather = await db.weather_data.find(query, {"_id": 0}).to_list(100)
    return weather

@api_router.post("/weather")
async def add_weather_data(weather: WeatherData):
    weather_dict = weather.model_dump()
    await db.weather_data.insert_one(weather_dict)
    return {"message": "Weather data added successfully", **weather_dict}


# =====================================
# SCHEMES ROUTES
# =====================================

@api_router.get("/schemes")
async def get_schemes():
    schemes = await db.schemes.find({}, {"_id": 0}).to_list(100)
    return schemes

@api_router.post("/schemes")
async def add_scheme(scheme: Scheme):
    scheme_dict = scheme.model_dump()
    await db.schemes.insert_one(scheme_dict)
    return {"message": "Scheme added successfully", **scheme_dict}


# =====================================
# VILLAGES ROUTES
# =====================================

@api_router.get("/villages")
async def get_villages(
    state: Optional[str] = None,
    district: Optional[str] = None
):
    query = {}
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    if district:
        query["district"] = {"$regex": district, "$options": "i"}
    
    villages = await db.villages.find(query, {"_id": 0}).to_list(1000)
    return villages


# =====================================
# CROPS ROUTES
# =====================================

@api_router.get("/crops")
async def get_crops(season: Optional[str] = None):
    query = {}
    if season:
        query["season"] = {"$regex": season, "$options": "i"}
    
    crops = await db.crops.find(query, {"_id": 0}).to_list(100)
    return crops

@api_router.get("/gan")
async def get_gan_mapping():
    """Get the crop to disease collection mapping (GAN table)"""
    gan = await db.gan.find({}, {"_id": 0}).to_list(100)
    return gan


# =====================================
# DISEASE ROUTES - COMPREHENSIVE
# =====================================

@api_router.get("/diseases")
async def get_all_diseases():
    """Get all diseases from all crop collections"""
    gan_mappings = await db.gan.find({}, {"_id": 0}).to_list(100)
    all_diseases = []
    
    for mapping in gan_mappings:
        collection_name = mapping.get("disease_collection")
        crop_type = mapping.get("crop_type")
        if collection_name:
            diseases = await db[collection_name].find({}, {"_id": 0}).to_list(100)
            for disease in diseases:
                disease["crop_type"] = crop_type
            all_diseases.extend(diseases)
    
    return all_diseases

@api_router.get("/diseases/{crop_name}")
async def get_diseases_by_crop(crop_name: str):
    """Get all diseases for a specific crop"""
    # First, find the collection name from GAN table
    gan_entry = await db.gan.find_one(
        {"crop_type": {"$regex": f"^{crop_name}$", "$options": "i"}},
        {"_id": 0}
    )
    
    if not gan_entry:
        # Try direct collection lookup
        collection_name = f"{crop_name.lower()}_disease"
        diseases = await db[collection_name].find({}, {"_id": 0}).to_list(100)
        if diseases:
            return diseases
        raise HTTPException(status_code=404, detail=f"No diseases found for crop: {crop_name}")
    
    collection_name = gan_entry.get("disease_collection")
    diseases = await db[collection_name].find({}, {"_id": 0}).to_list(100)
    return diseases

@api_router.get("/disease-collections")
async def get_disease_collections():
    """Get list of all available disease collections with crop types"""
    gan = await db.gan.find({}, {"_id": 0}).to_list(100)
    return [{"crop_type": g["crop_type"], "collection": g["disease_collection"]} for g in gan]


# =====================================
# DISEASE DETECTION RESULT ROUTES
# =====================================

@api_router.get("/disease-results")
async def get_disease_results(farmer_id: Optional[str] = None):
    query = {}
    if farmer_id:
        query["farmer_id"] = farmer_id
    
    results = await db.disease_results.find(query, {"_id": 0}).to_list(100)
    return results

@api_router.post("/disease-results")
async def add_disease_result(result: Dict[str, Any]):
    await db.disease_results.insert_one(result)
    return {"message": "Disease result saved successfully"}


# =====================================
# ADVISORIES ROUTES
# =====================================

@api_router.get("/advisories")
async def get_advisories(farmer_id: Optional[str] = None):
    query = {}
    if farmer_id:
        query["farmer_id"] = farmer_id
    
    advisories = await db.advisories.find(query, {"_id": 0}).to_list(100)
    return advisories

@api_router.post("/advisories")
async def add_advisory(advisory: Advisory):
    advisory_dict = advisory.model_dump()
    await db.advisories.insert_one(advisory_dict)
    return {"message": "Advisory added successfully", **advisory_dict}


# =====================================
# FIELDS ROUTES
# =====================================

@api_router.get("/fields")
async def get_fields(farmer_id: Optional[str] = None):
    query = {}
    if farmer_id:
        query["farmer_id"] = farmer_id
    
    fields = await db.fields.find(query, {"_id": 0}).to_list(100)
    return fields


# =====================================
# CROP IMAGES ROUTES
# =====================================

@api_router.get("/crop-images")
async def get_crop_images(farmer_id: Optional[str] = None):
    query = {}
    if farmer_id:
        query["farmer_id"] = farmer_id
    
    images = await db.crop_images.find(query, {"_id": 0}).to_list(100)
    return images


# =====================================
# VOICE QUERIES ROUTES
# =====================================

@api_router.get("/voice-queries")
async def get_voice_queries(farmer_id: Optional[str] = None):
    query = {}
    if farmer_id:
        query["farmer_id"] = farmer_id
    
    queries = await db.voice_queries.find(query, {"_id": 0}).to_list(100)
    return queries


# =====================================
# SCHEME NOTIFICATIONS ROUTES
# =====================================

@api_router.get("/scheme-notifications")
async def get_scheme_notifications():
    notifications = await db.scheme_notifications.find({}, {"_id": 0}).to_list(100)
    return notifications


# =====================================
# EXTERNAL WEATHER API ROUTES
# =====================================

# Mock weather data for fallback
MOCK_WEATHER_DATA = {
    "current": {
        "temp": 28,
        "feels_like": 30,
        "humidity": 65,
        "wind_speed": 12,
        "weather": [{"main": "Clouds", "description": "partly cloudy", "icon": "02d"}],
        "uvi": 7,
        "rainfall": 5
    },
    "daily": [
        {"dt": 1735257600, "temp": {"day": 28, "min": 22, "max": 30}, "humidity": 65, "weather": [{"main": "Clear", "icon": "01d"}], "pop": 0},
        {"dt": 1735344000, "temp": {"day": 26, "min": 21, "max": 28}, "humidity": 70, "weather": [{"main": "Clouds", "icon": "02d"}], "pop": 20},
        {"dt": 1735430400, "temp": {"day": 24, "min": 20, "max": 26}, "humidity": 80, "weather": [{"main": "Rain", "icon": "10d"}], "pop": 80},
        {"dt": 1735516800, "temp": {"day": 27, "min": 21, "max": 27}, "humidity": 68, "weather": [{"main": "Clouds", "icon": "03d"}], "pop": 30},
        {"dt": 1735603200, "temp": {"day": 29, "min": 22, "max": 29}, "humidity": 60, "weather": [{"main": "Clear", "icon": "01d"}], "pop": 0},
        {"dt": 1735689600, "temp": {"day": 31, "min": 23, "max": 31}, "humidity": 55, "weather": [{"main": "Clear", "icon": "01d"}], "pop": 0},
        {"dt": 1735776000, "temp": {"day": 30, "min": 22, "max": 30}, "humidity": 62, "weather": [{"main": "Clouds", "icon": "02d"}], "pop": 10},
    ],
    "location": "Dehradun, Uttarakhand"
}

@api_router.get("/weather/forecast")
async def get_weather_forecast(
    lat: float = Query(30.3165, description="Latitude"),
    lon: float = Query(78.0322, description="Longitude"),
    location_name: str = Query("Dehradun", description="Location name")
):
    """Get 7-day weather forecast from OpenWeatherMap API"""
    try:
        async with httpx.AsyncClient() as client:
            # Get current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            current_response = await client.get(current_url, timeout=10.0)
            
            # Get 7-day forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            forecast_response = await client.get(forecast_url, timeout=10.0)
            
            if current_response.status_code == 200 and forecast_response.status_code == 200:
                current_data = current_response.json()
                forecast_data = forecast_response.json()
                
                # Process current weather
                current = {
                    "temp": round(current_data["main"]["temp"]),
                    "feels_like": round(current_data["main"]["feels_like"]),
                    "humidity": current_data["main"]["humidity"],
                    "wind_speed": round(current_data["wind"]["speed"] * 3.6),  # Convert m/s to km/h
                    "weather": current_data["weather"],
                    "rainfall": current_data.get("rain", {}).get("1h", 0),
                    "pressure": current_data["main"]["pressure"],
                    "visibility": current_data.get("visibility", 10000) / 1000,  # Convert to km
                }
                
                # Process 7-day forecast (group by day)
                daily_forecasts = {}
                for item in forecast_data["list"]:
                    date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                    if date not in daily_forecasts:
                        daily_forecasts[date] = {
                            "dt": item["dt"],
                            "temp": {"day": round(item["main"]["temp"]), "min": round(item["main"]["temp_min"]), "max": round(item["main"]["temp_max"])},
                            "humidity": item["main"]["humidity"],
                            "weather": item["weather"],
                            "pop": int(item.get("pop", 0) * 100),
                            "wind_speed": round(item["wind"]["speed"] * 3.6),
                        }
                
                daily = list(daily_forecasts.values())[:7]
                
                # Calculate spray condition based on humidity and wind
                spray_condition = "Good" if current["humidity"] < 70 and current["wind_speed"] < 15 else "Poor"
                
                return {
                    "current": current,
                    "daily": daily,
                    "location": location_name,
                    "spray_condition": spray_condition,
                    "source": "live"
                }
            else:
                # Return mock data if API fails
                return {**MOCK_WEATHER_DATA, "source": "mock", "location": location_name}
                
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        return {**MOCK_WEATHER_DATA, "source": "mock", "error": str(e), "location": location_name}


# =====================================
# EXTERNAL MANDI/MARKET API ROUTES
# =====================================

# Mock market data for fallback
MOCK_MARKET_PRICES = [
    {"crop": "Wheat (Gehu)", "price": 2250, "change": "+5%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=100"},
    {"crop": "Rice (Dhaan)", "price": 3100, "change": "-2%", "market": "Haridwar Mandi", "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100"},
    {"crop": "Sugarcane", "price": 340, "change": "+0%", "market": "Roorkee Mandi", "image": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=100"},
    {"crop": "Tomato", "price": 1800, "change": "+12%", "market": "Vikasnagar Mandi", "image": "https://images.unsplash.com/photo-1546470427-227c7369676e?w=100"},
    {"crop": "Potato", "price": 1200, "change": "-3%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1518977676601-b53f82ber48?w=100"},
    {"crop": "Onion", "price": 2500, "change": "+8%", "market": "Haridwar Mandi", "image": "https://images.unsplash.com/photo-1618512496248-a07c36a9497b?w=100"},
    {"crop": "Maize (Makka)", "price": 1850, "change": "+2%", "market": "Roorkee Mandi", "image": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=100"},
    {"crop": "Soybean", "price": 4200, "change": "-1%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100"},
    {"crop": "Mustard", "price": 5100, "change": "+4%", "market": "Haridwar Mandi", "image": "https://images.unsplash.com/photo-1597916829826-02e5bb4a54e0?w=100"},
    {"crop": "Groundnut", "price": 5500, "change": "+6%", "market": "Vikasnagar Mandi", "image": "https://images.unsplash.com/photo-1567892737950-30c4db37cd89?w=100"},
    {"crop": "Cotton", "price": 6200, "change": "-2%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1594897030264-ab7d87efc473?w=100"},
    {"crop": "Chilli", "price": 8500, "change": "+15%", "market": "Roorkee Mandi", "image": "https://images.unsplash.com/photo-1588252303782-cb80119abd1f?w=100"},
    {"crop": "Turmeric", "price": 7200, "change": "+3%", "market": "Haridwar Mandi", "image": "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?w=100"},
    {"crop": "Ginger", "price": 3800, "change": "+7%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1615485020960-b2137ea21fc5?w=100"},
    {"crop": "Garlic", "price": 4500, "change": "-5%", "market": "Vikasnagar Mandi", "image": "https://images.unsplash.com/photo-1540148426945-6cf22a6b2f85?w=100"},
    {"crop": "Banana", "price": 1500, "change": "+1%", "market": "Haridwar Mandi", "image": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=100"},
    {"crop": "Mango", "price": 4000, "change": "+10%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=100"},
    {"crop": "Apple", "price": 8000, "change": "+2%", "market": "Dehradun Mandi", "image": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=100"},
    {"crop": "Grapes", "price": 6500, "change": "-4%", "market": "Roorkee Mandi", "image": "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=100"},
    {"crop": "Cabbage", "price": 800, "change": "+9%", "market": "Vikasnagar Mandi", "image": "https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?w=100"},
]

# Historical price data for graphs (mock)
MOCK_PRICE_HISTORY = {
    "Wheat (Gehu)": [2100, 2150, 2180, 2200, 2220, 2250, 2250],
    "Rice (Dhaan)": [3200, 3180, 3150, 3120, 3100, 3080, 3100],
    "Tomato": [1500, 1600, 1650, 1700, 1750, 1780, 1800],
    "Potato": [1250, 1240, 1230, 1220, 1210, 1200, 1200],
    "Onion": [2300, 2350, 2400, 2420, 2450, 2480, 2500],
}

@api_router.get("/mandi/prices")
async def get_mandi_prices(
    state: str = Query(None, description="State name (optional, leave empty for all states)"),
    limit: int = Query(20, description="Number of results")
):
    """Get live mandi prices from data.gov.in API"""
    try:
        async with httpx.AsyncClient() as client:
            # data.gov.in API for mandi prices
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                "api-key": MARKET_API_KEY,
                "format": "json",
                "limit": limit * 2  # Fetch more to ensure we have enough after filtering
            }
            
            # Add state filter if provided
            if state:
                params["filters[state]"] = state
            
            response = await client.get(url, params=params, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                # If no records for specific state, try without filter
                if not records and state:
                    del params["filters[state]"]
                    response = await client.get(url, params=params, timeout=15.0)
                    if response.status_code == 200:
                        data = response.json()
                        records = data.get("records", [])
                
                if records:
                    # Transform API data to our format
                    prices = []
                    crop_images = {
                        "wheat": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=100",
                        "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100",
                        "paddy": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100",
                        "tomato": "https://images.unsplash.com/photo-1546470427-227c7369676e?w=100",
                        "potato": "https://images.unsplash.com/photo-1518977676601-b53f82ber48?w=100",
                        "onion": "https://images.unsplash.com/photo-1618512496248-a07c36a9497b?w=100",
                        "maize": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=100",
                        "sugarcane": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=100",
                        "cotton": "https://images.unsplash.com/photo-1594897030264-ab7d87efc473?w=100",
                        "mustard": "https://images.unsplash.com/photo-1597916829826-02e5bb4a54e0?w=100",
                        "groundnut": "https://images.unsplash.com/photo-1567892737950-30c4db37cd89?w=100",
                        "soybean": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100",
                    }
                    
                    for record in records[:limit]:
                        commodity = record.get("commodity", "Unknown")
                        commodity_lower = commodity.lower()
                        
                        # Find matching image
                        image_url = None
                        for crop_key, img_url in crop_images.items():
                            if crop_key in commodity_lower:
                                image_url = img_url
                                break
                        if not image_url:
                            image_url = f"https://source.unsplash.com/100x100/?{commodity_lower.replace(' ', '+')},vegetable"
                        
                        prices.append({
                            "crop": commodity,
                            "variety": record.get("variety", ""),
                            "price": int(float(record.get("modal_price", 0) or 0)),
                            "min_price": int(float(record.get("min_price", 0) or 0)),
                            "max_price": int(float(record.get("max_price", 0) or 0)),
                            "market": record.get("market", "Unknown Mandi"),
                            "district": record.get("district", ""),
                            "state": record.get("state", state or "All India"),
                            "arrival_date": record.get("arrival_date", ""),
                            "image": image_url
                        })
                    
                    return {
                        "prices": prices,
                        "count": len(prices),
                        "total_available": data.get("total", len(prices)),
                        "source": "live",
                        "requested_state": state,
                        "last_updated": datetime.now().isoformat()
                    }
            
            # Return mock data if API fails
            return {
                "prices": MOCK_MARKET_PRICES[:limit],
                "count": len(MOCK_MARKET_PRICES[:limit]),
                "source": "mock",
                "reason": "API returned no data",
                "last_updated": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Mandi API error: {str(e)}")
        return {
            "prices": MOCK_MARKET_PRICES[:limit],
            "count": len(MOCK_MARKET_PRICES[:limit]),
            "source": "mock",
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }

@api_router.get("/mandi/price-history/{crop}")
async def get_price_history(crop: str):
    """Get price history for a specific crop (for graphs)"""
    # Generate mock historical data with fluctuations
    import random
    base_prices = {
        "wheat": 2200, "rice": 3100, "tomato": 1800, "potato": 1200,
        "onion": 2500, "maize": 1850, "soybean": 4200, "mustard": 5100,
        "sugarcane": 340, "cotton": 6200, "chilli": 8500, "turmeric": 7200
    }
    
    base = base_prices.get(crop.lower(), 2000)
    history = []
    dates = []
    
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        dates.append(date.strftime("%d %b"))
        variation = random.uniform(-0.05, 0.08)
        price = int(base * (1 + variation))
        history.append(price)
    
    # Different mandi prices
    mandis = ["Dehradun", "Haridwar", "Roorkee", "Rishikesh", "Vikasnagar"]
    mandi_prices = {}
    for mandi in mandis:
        mandi_prices[mandi] = [int(h * random.uniform(0.95, 1.05)) for h in history]
    
    return {
        "crop": crop,
        "dates": dates,
        "history": history,
        "mandi_prices": mandi_prices,
        "current_price": history[-1]
    }


# =====================================
# CROP RECOMMENDATION WITH WEATHER
# =====================================

@api_router.get("/crop-recommendation")
async def get_crop_recommendation(
    lat: float = Query(30.3165, description="Latitude"),
    lon: float = Query(78.0322, description="Longitude"),
    soil_type: str = Query("loamy", description="Soil type"),
    water_source: str = Query("rainfall", description="Water source"),
    nitrogen: float = Query(50, description="Nitrogen content (N)"),
    phosphorus: float = Query(50, description="Phosphorus content (P)"),
    potassium: float = Query(50, description="Potassium content (K)"),
    ph: float = Query(6.5, description="Soil pH value")
):
    """Get crop recommendations based on weather, soil conditions, and ML model"""
    try:
        # Get current weather
        weather_data = await get_weather_forecast(lat, lon, "Location")
        current = weather_data.get("current", {})
        
        temp = current.get("temp", 28)
        humidity = current.get("humidity", 65)
        
        # Get the ML engine
        engine = get_crop_engine()
        
        # Get recommendations using the ML model
        recommendations = engine.recommend_crops(
            temperature=temp,
            humidity=humidity,
            soil_type=soil_type,
            water_source=water_source,
            ph=ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium
        )
        
        return {
            "recommendations": recommendations[:5],
            "weather": {
                "temperature": temp,
                "humidity": humidity,
            },
            "soil_type": soil_type,
            "water_source": water_source,
            "npk": {"nitrogen": nitrogen, "phosphorus": phosphorus, "potassium": potassium, "ph": ph},
            "model_used": engine.model_loaded
        }
        
    except Exception as e:
        logger.error(f"Crop recommendation error: {e}")
        return {
            "recommendations": [
                {"crop": "Wheat", "confidence": 85, "season": "Rabi", "reason": "Default recommendation"},
                {"crop": "Rice", "confidence": 80, "season": "Kharif", "reason": "Default recommendation"},
            ],
            "error": str(e)
        }


# =====================================
# FERTILIZER CALCULATOR ROUTES
# =====================================

# Initialize fertilizer calculator (lazy loaded)
_fertilizer_calculator = None

def get_fertilizer_calculator():
    """Get or create FertilizerCalculator instance"""
    global _fertilizer_calculator
    if _fertilizer_calculator is None:
        try:
            from advanced_fertilizer_calculator import AdvancedFertilizerCalculator
            crop_db = ROOT_DIR / "crop_database.json"
            fert_db = ROOT_DIR / "fertilizer_database.json"
            _fertilizer_calculator = AdvancedFertilizerCalculator(
                crop_db_path=str(crop_db),
                fertilizer_db_path=str(fert_db)
            )
            logger.info("✅ Fertilizer Calculator initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize fertilizer calculator: {e}")
    return _fertilizer_calculator


class FertilizerCalculateRequest(BaseModel):
    crop: str
    quantity: float
    unit_type: Optional[str] = None  # tree, plant, or hectare


class FertilizerResponse(BaseModel):
    success: bool
    nutrients: Optional[Dict[str, Any]] = None
    fertilizers: Optional[Dict[str, float]] = None
    costs: Optional[Dict[str, float]] = None
    error: Optional[str] = None


@api_router.get("/fertilizer/crops")
async def get_crop_list():
    """
    Get all available crops organized by category
    """
    calculator = get_fertilizer_calculator()
    
    if not calculator:
        # Return mock data if calculator not available
        return {
            "categories": {
                "cereal": [
                    {"id": "wheat", "name": "Wheat"},
                    {"id": "rice", "name": "Rice (Paddy)"},
                    {"id": "maize", "name": "Maize (Corn)"},
                    {"id": "barley", "name": "Barley"},
                    {"id": "sorghum", "name": "Sorghum (Jowar)"},
                ],
                "pulse": [
                    {"id": "chickpea", "name": "Chickpea (Chana)"},
                    {"id": "lentil", "name": "Lentil (Masoor)"},
                    {"id": "pigeon_pea", "name": "Pigeon Pea (Arhar)"},
                ],
                "oilseed": [
                    {"id": "groundnut", "name": "Groundnut (Peanut)"},
                    {"id": "mustard", "name": "Mustard (Sarson)"},
                    {"id": "soybean", "name": "Soybean"},
                ],
                "vegetable": [
                    {"id": "tomato", "name": "Tomato"},
                    {"id": "potato", "name": "Potato"},
                    {"id": "onion", "name": "Onion"},
                ],
                "fruit": [
                    {"id": "mango", "name": "Mango"},
                    {"id": "banana", "name": "Banana"},
                    {"id": "apple", "name": "Apple"},
                ]
            }
        }
    
    try:
        categories = calculator.get_crop_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting crops: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fertilizer/crop/{crop_id}")
async def get_crop_details(crop_id: str):
    """
    Get detailed information about a specific crop
    """
    calculator = get_fertilizer_calculator()
    
    if not calculator or crop_id not in calculator.crop_data:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_id}' not found")
    
    crop_info = calculator.crop_data[crop_id]
    
    # Determine unit type
    if 'nutrients_per_tree_g' in crop_info:
        unit_type = 'tree'
        nutrients = crop_info['nutrients_per_tree_g']
    elif 'nutrients_per_plant_g' in crop_info:
        unit_type = 'plant'
        nutrients = crop_info['nutrients_per_plant_g']
    else:
        unit_type = 'hectare'
        nutrients = crop_info['nutrients_per_hectare_kg']
    
    return {
        "id": crop_id,
        "name": crop_info['name'],
        "category": crop_info.get('category', 'other'),
        "unit_type": unit_type,
        "nutrients_per_unit": nutrients
    }


@api_router.post("/fertilizer/calculate")
async def calculate_fertilizer(request: FertilizerCalculateRequest):
    """
    Calculate fertilizer requirements for a crop
    
    - **crop**: Crop ID (e.g., 'wheat', 'rice', 'apple')
    - **quantity**: Number of trees/plants or hectares
    - **unit_type**: Optional - will be auto-detected from crop type
    """
    calculator = get_fertilizer_calculator()
    
    if not calculator:
        raise HTTPException(
            status_code=503, 
            detail="Fertilizer calculator is not available. Please ensure crop_database.json and fertilizer_database.json exist."
        )
    
    try:
        # Calculate nutrient requirements
        nutrients = calculator.calculate_nutrient_requirement(
            crop=request.crop,
            quantity=request.quantity
        )
        
        # Calculate fertilizer recommendations
        fertilizers = calculator.calculate_basic_fertilizers(nutrients['total_kg'])
        
        # Calculate costs
        costs = calculator.calculate_cost(fertilizers)
        
        # Store calculation in database
        calc_record = {
            "calculation_id": str(uuid.uuid4()),
            "crop": request.crop,
            "crop_name": calculator.crop_data[request.crop]['name'],
            "quantity": request.quantity,
            "unit_type": nutrients['unit_type'],
            "nutrients": nutrients,
            "fertilizers": fertilizers,
            "costs": costs,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.fertilizer_calculations.insert_one(calc_record)
        
        return {
            "success": True,
            "calculation_id": calc_record["calculation_id"],
            "crop": {
                "id": request.crop,
                "name": calculator.crop_data[request.crop]['name'],
                "category": calculator.crop_data[request.crop].get('category', 'other')
            },
            "quantity": request.quantity,
            "unit_type": nutrients['unit_type'],
            "nutrients": {
                "per_unit": nutrients['per_unit'],
                "total_kg": nutrients['total_kg'],
                "total_g": nutrients['total_g']
            },
            "fertilizers": fertilizers,
            "costs": costs,
            "application_schedule": {
                "split_1": {"timing": "Early Growth", "percentage": 30},
                "split_2": {"timing": "Active Growth", "percentage": 30},
                "split_3": {"timing": "Reproductive", "percentage": 25},
                "split_4": {"timing": "Maintenance", "percentage": 15}
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Fertilizer calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fertilizer/history")
async def get_fertilizer_history(limit: int = 20):
    """
    Get recent fertilizer calculations
    """
    calculations = await db.fertilizer_calculations.find(
        {}, 
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {"calculations": calculations, "count": len(calculations)}


@api_router.get("/fertilizer/fertilizers")
async def get_fertilizer_list():
    """
    Get all available fertilizers with their composition and prices
    """
    calculator = get_fertilizer_calculator()
    
    if not calculator:
        # Return mock data
        return {
            "fertilizers": {
                "urea": {"name": "Urea", "type": "nitrogenous", "N": 46, "price": 6},
                "dap": {"name": "DAP", "type": "phosphatic", "N": 18, "P": 46, "price": 25},
                "mop": {"name": "MOP", "type": "potassic", "K": 60, "price": 17},
                "npk": {"name": "NPK 19:19:19", "type": "complex", "N": 19, "P": 19, "K": 19, "price": 30}
            }
        }
    
    fertilizers = {}
    for fert_id, fert_data in calculator.fertilizer_data.items():
        fertilizers[fert_id] = {
            "name": fert_data['name'],
            "type": fert_data.get('type', 'other'),
            "composition": fert_data['composition_percent'],
            "price_per_kg": fert_data.get('price_per_kg_inr', 0),
            "description": fert_data.get('description', '')
        }
    
    return {"fertilizers": fertilizers}


# =====================================
# VISION / DISEASE DETECTION ROUTES
# =====================================

# Initialize Vision Engine (HuggingFace API - lightweight)
_disease_engine = None

def get_plant_doctor():
    """Get or create Disease Engine instance"""
    global _disease_engine
    if _disease_engine is None:
        try:
            from vision_engine_hf import CropDiseaseEngine
            _disease_engine = CropDiseaseEngine()
            logger.info("✅ Disease Engine (HuggingFace) initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Disease Engine: {e}")
            return None
    return _disease_engine


@api_router.get("/detection/models")
async def get_available_models():
    """Get list of available crop detection models"""
    doctor = get_plant_doctor()
    
    if not doctor:
        # Return fallback data if model not available
        return {
            "crops": [
                {"id": "cotton", "name": "Cotton", "available": True, "diseases": ["Bacterial Blight", "Curl Virus", "Fusarium Wilt", "Healthy"]},
                {"id": "corn", "name": "Corn", "available": True, "diseases": ["Blight", "Common Rust", "Gray Leaf Spot", "Healthy"]},
                {"id": "sugarcane", "name": "Sugarcane", "available": True, "diseases": ["Mosaic", "Red Rot", "Rust", "Healthy"]},
                {"id": "wheat", "name": "Wheat", "available": True, "diseases": ["Brown Rust", "Healthy", "Yellow Rust"]},
                {"id": "rice", "name": "Rice", "available": True, "diseases": ["Blast", "Blight", "Tungro"]},
                {"id": "general", "name": "General Plant Scan", "available": True, "diseases": []},
                {"id": "pest", "name": "Pest Detection 🐛", "available": True, "diseases": []}
            ]
        }
    
    try:
        crops = doctor.get_available_crops()
        return {"crops": crops}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/detection/analyze")
async def analyze_crop_image(
    file: UploadFile = File(...),
    crop_type: str = Form("general")
):
    """
    Analyze crop image for disease detection
    
    Args:
        file: Image file (JPG, PNG)
        crop_type: Crop type (cotton, corn, sugarcane, wheat, rice, general, pest)
    
    Returns:
        Detection results with disease info, confidence, treatments
    """
    from PIL import Image
    import io
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    doctor = get_plant_doctor()
    
    if not doctor:
        # Return mock data if model not available
        return {
            "success": True,
            "disease": "Leaf Rust (Demo)",
            "confidence": 87.5,
            "severity": "Moderate",
            "description": "Demo mode: PlantDoctor model not loaded. This is a simulated response.",
            "crop_type": crop_type,
            "treatments": [
                {"name": "Mancozeb 75% WP", "dosage": "2.5 kg/ha", "timing": "At first symptoms"},
                {"name": "Propiconazole 25% EC", "dosage": "500 ml/ha", "timing": "Every 10-14 days"}
            ],
            "preventions": [
                "Use disease-resistant varieties",
                "Practice crop rotation",
                "Maintain proper spacing",
                "Regular field monitoring"
            ]
        }
    
    try:
        # Read image bytes
        contents = await file.read()
        
        # Run detection using HuggingFace API
        result = await doctor.analyze(contents, crop_type)
        
        # Save to database
        detection_record = {
            "crop_type": crop_type,
            "disease": result.get("disease_detected"),
            "confidence": result.get("confidence"),
            "severity": result.get("severity"),
            "timestamp": datetime.utcnow(),
            "success": result.get("success", False)
        }
        await db.detection_history.insert_one(detection_record)
        
        return result
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/detection/history")
async def get_detection_history(limit: int = 20):
    """Get recent detection history"""
    try:
        history = await db.detection_history.find(
            {}, 
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting detection history: {e}")
        return {"history": []}


@api_router.get("/detection/disease-info/{disease_name}")
async def get_disease_info(disease_name: str):
    """Get detailed information about a specific disease"""
    doctor = get_plant_doctor()
    
    if doctor and hasattr(doctor, 'disease_info'):
        info = doctor.disease_info.get(disease_name)
        if info:
            return {
                "disease": disease_name,
                "description": info.get("description", ""),
                "severity": info.get("severity", "Unknown"),
                "treatments": info.get("treatments", []),
                "preventions": info.get("preventions", [])
            }
    
    # Fallback to database
    try:
        for mapping in CROP_DISEASE_MAPPING:
            collection = mapping.get("disease_collection")
            if collection:
                disease = await db[collection].find_one(
                    {"disease_name": {"$regex": disease_name, "$options": "i"}},
                    {"_id": 0}
                )
                if disease:
                    return disease
    except Exception as e:
        logger.error(f"Database error: {e}")
    
    raise HTTPException(status_code=404, detail=f"Disease '{disease_name}' not found")


# =====================================
# PESTICIDE CALCULATOR ROUTES
# =====================================

# Initialize pesticide calculator (lazy loaded)
_pesticide_calculator = None

def get_pesticide_calculator():
    """Get or create PesticideCalculator instance"""
    global _pesticide_calculator
    if _pesticide_calculator is None:
        try:
            from pesticide_calculator import PesticideCalculator
            formulations_db = ROOT_DIR / "formulations.json"
            _pesticide_calculator = PesticideCalculator(str(formulations_db))
            logger.info("✅ Pesticide Calculator initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize pesticide calculator: {e}")
    return _pesticide_calculator


class PesticideCalculateRequest(BaseModel):
    pesticide_id: str
    crop: str
    pest: str
    area: float
    area_unit: str = "hectare"
    pump_capacity: float = 16.0
    custom_dosage: Optional[float] = None
    custom_water: Optional[float] = None


@api_router.get("/pesticide/types")
async def get_pesticide_types():
    """
    Get all pesticides organized by type (Insecticide, Fungicide, etc.)
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        return {
            "types": {
                "Insecticide": [{"id": "imidacloprid", "name": "Imidacloprid 17.8% SL", "crops": ["Rice", "Cotton"]}],
                "Fungicide": [{"id": "tricyclazole", "name": "Tricyclazole 75% WP", "crops": ["Rice", "Wheat"]}],
                "Herbicide": [{"id": "glyphosate", "name": "Glyphosate 41% SL", "crops": ["General"]}],
                "Acaricide": [{"id": "dicofol", "name": "Dicofol 18.5% EC", "crops": ["Tea", "Apple"]}]
            }
        }
    
    try:
        by_type = calculator.get_pesticides_by_type()
        return {"types": by_type}
    except Exception as e:
        logger.error(f"Error getting pesticide types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/pesticide/all")
async def get_all_pesticides():
    """
    Get list of all pesticides
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        raise HTTPException(status_code=503, detail="Pesticide calculator not available")
    
    try:
        pesticides = calculator.get_all_pesticides()
        return {"pesticides": pesticides, "count": len(pesticides)}
    except Exception as e:
        logger.error(f"Error getting pesticides: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/pesticide/crops")
async def get_pesticide_crops():
    """
    Get list of all crops that have pesticide data
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        return {"crops": ["Rice", "Cotton", "Wheat", "Soybean", "Tomato", "Mango", "Grapes"]}
    
    try:
        crops = calculator.get_crops_list()
        return {"crops": crops, "count": len(crops)}
    except Exception as e:
        logger.error(f"Error getting crops: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/pesticide/search")
async def search_pesticides(q: str = Query(..., min_length=2)):
    """
    Search pesticides by name, crop, or pest
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        raise HTTPException(status_code=503, detail="Pesticide calculator not available")
    
    try:
        results = calculator.search_pesticides(q)
        return {"results": results, "query": q, "count": len(results)}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/pesticide/for-crop/{crop}")
async def get_pesticides_for_crop(crop: str):
    """
    Get all pesticides available for a specific crop
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        raise HTTPException(status_code=503, detail="Pesticide calculator not available")
    
    try:
        pesticides = calculator.get_pesticides_for_crop(crop)
        return {"crop": crop, "pesticides": pesticides, "count": len(pesticides)}
    except Exception as e:
        logger.error(f"Error getting pesticides for crop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/pesticide/{pesticide_id}")
async def get_pesticide_details(pesticide_id: str):
    """
    Get detailed information about a specific pesticide
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        raise HTTPException(status_code=503, detail="Pesticide calculator not available")
    
    details = calculator.get_pesticide_details(pesticide_id)
    
    if not details:
        raise HTTPException(status_code=404, detail=f"Pesticide '{pesticide_id}' not found")
    
    return details


@api_router.get("/pesticide/{pesticide_id}/pests")
async def get_pests_for_pesticide(pesticide_id: str, crop: str = None):
    """
    Get pests that a pesticide can treat, optionally filtered by crop
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        raise HTTPException(status_code=503, detail="Pesticide calculator not available")
    
    try:
        pests = calculator.get_pests_for_pesticide(pesticide_id, crop)
        return {"pesticide_id": pesticide_id, "crop_filter": crop, "pests": pests}
    except Exception as e:
        logger.error(f"Error getting pests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/pesticide/calculate")
async def calculate_pesticide_spray(request: PesticideCalculateRequest):
    """
    Calculate pesticide spray requirements
    
    - **pesticide_id**: ID of the pesticide
    - **crop**: Target crop
    - **pest**: Target pest
    - **area**: Field area
    - **area_unit**: 'hectare' or 'acre'
    - **pump_capacity**: Spray pump capacity in liters (default 16L)
    """
    calculator = get_pesticide_calculator()
    
    if not calculator:
        raise HTTPException(
            status_code=503,
            detail="Pesticide calculator not available. Please ensure formulations.json exists."
        )
    
    try:
        result = calculator.calculate_spray(
            pesticide_id=request.pesticide_id,
            crop=request.crop,
            pest=request.pest,
            area=request.area,
            area_unit=request.area_unit,
            pump_capacity=request.pump_capacity,
            custom_dosage=request.custom_dosage,
            custom_water=request.custom_water
        )
        
        # Store calculation in database
        calc_record = {
            "calculation_id": str(uuid.uuid4()),
            **result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.pesticide_calculations.insert_one(calc_record)
        
        return {
            "success": True,
            "calculation_id": calc_record["calculation_id"],
            **result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Pesticide calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/pesticide/history")
async def get_pesticide_history(limit: int = 20):
    """
    Get recent pesticide calculations
    """
    calculations = await db.pesticide_calculations.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {"calculations": calculations, "count": len(calculations)}


# =====================================
# VOICE ASSISTANT ROUTES
# =====================================

# Initialize voice assistant components (lazy loaded)
_agri_brain = None
_voice_processor = None

def get_agri_brain():
    """Get or create AgriBrain instance"""
    global _agri_brain
    if _agri_brain is None:
        try:
            from agri_brain import agri_brain
            _agri_brain = agri_brain
        except ImportError as e:
            logger.warning(f"AgriBrain not available: {e}")
    return _agri_brain

def get_voice_processor():
    """Get or create VoiceProcessor instance"""
    global _voice_processor
    if _voice_processor is None:
        try:
            from voice_processor import get_voice_engine
            _voice_processor = get_voice_engine()
        except ImportError as e:
            logger.warning(f"VoiceProcessor not available: {e}")
    return _voice_processor


class ChatMessage(BaseModel):
    message: str
    language: str = "en"
    farmer_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    language: str
    timestamp: str


@api_router.post("/voice/chat")
async def chat_with_assistant(chat: ChatMessage):
    """
    Text-based chat with Kisan.JI AI assistant
    Uses Gemini API for responses
    """
    brain = get_agri_brain()
    
    if not brain:
        # Fallback to simple responses
        return {
            "response": "Voice assistant is loading. Please try again in a moment.",
            "language": chat.language,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    try:
        response = brain.ask_bot(chat.message, chat.language)
        
        # Store in database
        if chat.farmer_id:
            await db.voice_queries.insert_one({
                "query_id": str(uuid.uuid4()),
                "farmer_id": chat.farmer_id,
                "query_text": chat.message,
                "language": chat.language,
                "response": response,
                "query_type": "text",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "response": response,
            "language": chat.language,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "response": "I'm having trouble responding right now. Please try again.",
            "language": chat.language,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@api_router.post("/voice/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    farmer_id: Optional[str] = Form(None)
):
    """
    Transcribe audio file using Whisper
    Returns transcribed text and detected language
    """
    processor = get_voice_processor()
    
    if not processor:
        raise HTTPException(
            status_code=503, 
            detail="Voice processing is not available. Required: openai-whisper"
        )
    
    # Save uploaded file
    file_id = uuid.uuid4().hex[:8]
    file_extension = audio.filename.split('.')[-1] if '.' in audio.filename else 'wav'
    audio_path = UPLOAD_DIR / f"audio_{file_id}.{file_extension}"
    
    try:
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        
        # Transcribe
        result = processor.transcribe(str(audio_path))
        
        if result.get('success'):
            return {
                "text": result['text'],
                "language": result['language'],
                "language_name": result.get('language_name', result['language']),
                "success": True
            }
        else:
            raise HTTPException(status_code=400, detail="Transcription failed")
            
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if audio_path.exists():
            audio_path.unlink()


@api_router.post("/voice/ask")
async def voice_query(
    audio: UploadFile = File(...),
    farmer_id: Optional[str] = Form(None),
    generate_audio: bool = Form(False)
):
    """
    Complete voice query: Transcribe -> AI Response -> (Optional) TTS
    """
    processor = get_voice_processor()
    brain = get_agri_brain()
    
    if not processor:
        raise HTTPException(
            status_code=503, 
            detail="Voice processing is not available"
        )
    
    # Save uploaded file
    file_id = uuid.uuid4().hex[:8]
    file_extension = audio.filename.split('.')[-1] if '.' in audio.filename else 'wav'
    audio_path = UPLOAD_DIR / f"audio_{file_id}.{file_extension}"
    
    try:
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        
        # Step 1: Transcribe
        transcription = processor.transcribe(str(audio_path))
        
        if not transcription.get('success'):
            return {
                "success": False,
                "error": "Could not transcribe audio",
                "transcription": "",
                "response": "Sorry, I couldn't understand the audio."
            }
        
        # Step 2: Get AI response
        response_text = ""
        if brain and transcription['text']:
            response_text = brain.ask_bot(
                transcription['text'],
                transcription['language']
            )
        else:
            response_text = "I'm not available right now. Please try again."
        
        # Step 3: Store in database
        query_id = str(uuid.uuid4())
        await db.voice_queries.insert_one({
            "query_id": query_id,
            "farmer_id": farmer_id,
            "query_text": transcription['text'],
            "language": transcription['language'],
            "response": response_text,
            "query_type": "voice",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        result = {
            "success": True,
            "query_id": query_id,
            "transcription": transcription['text'],
            "language": transcription['language'],
            "language_name": transcription.get('language_name', ''),
            "response": response_text,
            "audio_response": None
        }
        
        # Step 4: Generate audio response (optional)
        if generate_audio and response_text:
            try:
                from universal_tts import get_tts_engine
                tts = get_tts_engine()
                
                if tts:
                    output_path = OUTPUT_DIR / f"response_{file_id}.wav"
                    audio_file = tts.generate_audio(
                        text=response_text,
                        language=transcription['language'],
                        output_path=str(output_path)
                    )
                    if audio_file:
                        result['audio_response'] = f"/api/voice/audio/{file_id}"
            except Exception as e:
                logger.warning(f"TTS generation failed: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Voice query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup input file
        if audio_path.exists():
            audio_path.unlink()


@api_router.get("/voice/audio/{file_id}")
async def get_audio_response(file_id: str):
    """
    Retrieve generated audio response
    """
    audio_path = OUTPUT_DIR / f"response_{file_id}.wav"
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=f"response_{file_id}.wav"
    )


@api_router.get("/voice/history")
async def get_voice_history(farmer_id: Optional[str] = None, limit: int = 20):
    """
    Get voice query history for a farmer
    """
    query = {}
    if farmer_id:
        query["farmer_id"] = farmer_id
    
    queries = await db.voice_queries.find(
        query, 
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {"queries": queries, "count": len(queries)}


# =====================================
# TRANSLATION SERVICE ROUTES
# =====================================

@api_router.get("/translate")
async def translate_text(
    text: str = Query(..., description="Text to translate"),
    target_lang: str = Query("hi", description="Target language code"),
    source_lang: str = Query("en", description="Source language code")
):
    """Translate text to the target language"""
    try:
        translator = get_translation_service()
        translated = translator.translate(text, target_lang, source_lang)
        return {
            "original": text,
            "translated": translated,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {
            "original": text,
            "translated": text,
            "error": str(e)
        }


@api_router.post("/translate/batch")
async def translate_batch(
    texts: List[str],
    target_lang: str = Query("hi", description="Target language code"),
    source_lang: str = Query("en", description="Source language code")
):
    """Translate multiple texts at once"""
    try:
        translator = get_translation_service()
        translations = translator.translate_batch(texts, target_lang, source_lang)
        return {
            "translations": translations,
            "target_lang": target_lang
        }
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        return {
            "translations": {text: text for text in texts},
            "error": str(e)
        }


@api_router.get("/translate/ui/{language}")
async def get_ui_translations(language: str):
    """Get all UI translations for a specific language"""
    try:
        translator = get_translation_service()
        translations = translator.get_ui_translations(language)
        return {
            "language": language,
            "translations": translations,
            "count": len(translations)
        }
    except Exception as e:
        logger.error(f"UI translation error: {e}")
        return {
            "language": language,
            "translations": {},
            "error": str(e)
        }


@api_router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    translator = get_translation_service()
    languages = translator.get_supported_languages()
    return {
        "languages": languages,
        "count": len(languages)
    }


# =====================================
# FARMER ALERT NETWORK ROUTES (GNN + RL)
# =====================================

@api_router.post("/farmer/register")
async def register_farmer(registration: FarmerRegistration):
    """Register a new farmer in the alert network"""
    try:
        service = get_alert_service()
        result = service.register_farmer(registration)
        return result
    except Exception as e:
        logger.error(f"Farmer registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/farmer/location")
async def update_farmer_location(update: FarmerLocationUpdate):
    """Update farmer's location (from GPS)"""
    try:
        location_service = get_location_service()
        result = location_service.update_location(update)
        
        # Also update in farmer network if registered
        network = get_farmer_network()
        network.update_farmer_location(update.farmer_id, update.latitude, update.longitude)
        
        return result
    except Exception as e:
        logger.error(f"Location update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/location/{farmer_id}")
async def get_farmer_location(farmer_id: str):
    """Get farmer's stored location"""
    try:
        location_service = get_location_service()
        location = location_service.get_location(farmer_id)
        
        if location:
            return {"success": True, "farmer_id": farmer_id, "location": location}
        else:
            return {"success": False, "message": "Location not found"}
    except Exception as e:
        logger.error(f"Get location error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/farmer/report-disease")
async def report_disease(report: DiseaseReport):
    """
    Report a disease/pest detection
    This triggers the GNN to find similar farmers and send alerts
    """
    try:
        service = get_alert_service()
        result = service.report_disease(report)
        
        return {
            "success": True,
            "report": result
        }
    except Exception as e:
        logger.error(f"Disease report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/similar/{farmer_id}")
async def get_similar_farmers(
    farmer_id: str,
    top_k: int = Query(10, description="Number of similar farmers to return"),
    min_similarity: float = Query(0.4, description="Minimum similarity threshold")
):
    """Get farmers similar to the given farmer (based on GNN similarity)"""
    try:
        network = get_farmer_network()
        similar = network.find_similar_farmers(farmer_id, top_k, min_similarity)
        
        return {
            "farmer_id": farmer_id,
            "similar_farmers": [
                {"farmer_id": f[0], "similarity": f[1], "distance_km": f[2]}
                for f in similar
            ],
            "count": len(similar)
        }
    except Exception as e:
        logger.error(f"Similar farmers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/alerts/{farmer_id}")
async def get_farmer_alerts(
    farmer_id: str,
    include_read: bool = Query(False, description="Include read alerts")
):
    """Get alerts for a farmer"""
    try:
        network = get_farmer_network()
        alerts = network.get_alerts_for_farmer(farmer_id, include_read)
        
        return {
            "farmer_id": farmer_id,
            "alerts": alerts,
            "count": len(alerts),
            "unread": sum(1 for a in alerts if not a.get("read", False))
        }
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/farmer/alerts/{farmer_id}/read/{alert_id}")
async def mark_alert_read(farmer_id: str, alert_id: str):
    """Mark an alert as read"""
    try:
        network = get_farmer_network()
        success = network.mark_alert_read(alert_id, farmer_id)
        
        return {"success": success, "alert_id": alert_id}
    except Exception as e:
        logger.error(f"Mark alert read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/notifications/{farmer_id}")
async def get_farmer_notifications(
    farmer_id: str,
    unread_only: bool = Query(False, description="Only unread notifications"),
    limit: int = Query(50, description="Maximum notifications to return")
):
    """Get notifications for a farmer"""
    try:
        notification_service = get_notification_service()
        notifications = notification_service.get_notifications(farmer_id, unread_only, limit)
        
        return {
            "farmer_id": farmer_id,
            "notifications": notifications,
            "count": len(notifications),
            "unread_count": notification_service.get_unread_count(farmer_id)
        }
    except Exception as e:
        logger.error(f"Get notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/farmer/notifications/{farmer_id}/read/{notification_id}")
async def mark_notification_read(farmer_id: str, notification_id: str):
    """Mark a notification as read"""
    try:
        notification_service = get_notification_service()
        success = notification_service.mark_as_read(farmer_id, notification_id)
        
        return {"success": success, "notification_id": notification_id}
    except Exception as e:
        logger.error(f"Mark notification read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/farmer/notifications/{farmer_id}/read-all")
async def mark_all_notifications_read(farmer_id: str):
    """Mark all notifications as read"""
    try:
        notification_service = get_notification_service()
        count = notification_service.mark_all_read(farmer_id)
        
        return {"success": True, "marked_count": count}
    except Exception as e:
        logger.error(f"Mark all read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/farmer/notification-preferences")
async def set_notification_preferences(prefs: NotificationPreferences):
    """Set notification preferences"""
    try:
        notification_service = get_notification_service()
        result = notification_service.set_preferences(prefs)
        
        return result
    except Exception as e:
        logger.error(f"Set preferences error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/notification-preferences/{farmer_id}")
async def get_notification_preferences(farmer_id: str):
    """Get notification preferences"""
    try:
        notification_service = get_notification_service()
        prefs = notification_service.get_preferences(farmer_id)
        
        return {"farmer_id": farmer_id, "preferences": prefs}
    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/dashboard/{farmer_id}")
async def get_farmer_dashboard(farmer_id: str):
    """Get complete dashboard data for a farmer"""
    try:
        service = get_alert_service()
        dashboard = service.get_farmer_dashboard(farmer_id)
        
        return dashboard
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/network-stats")
async def get_network_statistics():
    """Get statistics about the farmer alert network"""
    try:
        network = get_farmer_network()
        stats = network.get_network_stats()
        
        return stats
    except Exception as e:
        logger.error(f"Network stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/farmer/nearby")
async def get_nearby_farmers(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, description="Search radius in km")
):
    """Get farmers nearby a location"""
    try:
        location_service = get_location_service()
        nearby = location_service.get_nearby_farmers(lat, lon, radius_km)
        
        return {
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "farmers": nearby,
            "count": len(nearby)
        }
    except Exception as e:
        logger.error(f"Nearby farmers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import timedelta for price history
from datetime import timedelta

# Include the router in the main app
app.include_router(api_router)

# CORS - Allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()