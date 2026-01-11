#  Kisan.JI - Smart Agriculture Platform   (deployed on vercel live link ---->>> https://kisanji-frontend.vercel.app )

### Explainatory video link---->  https://youtu.be/ETIP463LaVk?si=M5DlUlwCZ6KcZCZz

Team Name: Kedari
Event: Hack The Winter.
University: Graphic Era Hill University, Dehradun

(Kisan.JI) is an AI-powered, mobile-first "village nervous system" designed to empower smallholder farmers. Addressing the critical issues of crop loss and market exploitation, our solution acts as a bridge between advanced agricultural science and the rural farmer.Current Status: This is a fully functional prototype featuring a Python backend, HTML/CSS/JS frontend, and optimized ONNX-based deep learning models for fast, lightweight inference.

  
  **AI-Powered Agricultural Assistant for Indian Farmers**
  


---

### Application Flow & Architecture ###
##  System Architecture
<p align="center">
  <img src="architecture.jpeg" alt="EchoHarvest System Architecture" width="100%">
</p>

##  Application Flowchart
<h2 align="center"> Application Flowchart</h2>
<p align="center">
  <img src="flow.jpeg" alt="Application Flowchart" width="100%">
</p>

    
##  Features---

###  AI-Powered Assistant
- **Gemini AI Integration** - Smart chatbot for farming queries
- **Voice Assistant** - Multilingual voice support (Hindi, Marathi, Tamil, Telugu, etc.)
- **Text-to-Speech** - Audio responses in regional languages

###  Crop Management
- **Disease Detection** - ONNX model-based plant disease identification(plant_doctor.pt, corn_mobile_v2.onnx, sugarcane_mobile_v2.onnx,  wheat_mobile_v2.onnx, rice_mobile_v2.onnx, cotton_mobile_v2.onnx)
- Workflow: Image Input → ONNX Runtime Inference → Disease
- **Pest Detection** - YOLOv8-powered pest identification
- **Crop Recommendation** - Powered by a trained Random Forest model (crop_recommender.pkl).
•	Inputs: Nitrogen (N), Phosphorus (P), Potassium (K), pH Level, Rainfall, and Water Source (Tubewell/Borewell vs. Rain).
•	Logic: Correlates soil nutrients with IMD weather data to suggest the highest-yield crop for the specific season.

###  Market Intelligence
- **Live Mandi Prices** - Real-time market prices from eNAM API
- **Weather Forecasts** - OpenWeatherMap integration with farming alerts
- **Price Trends** - Historical price analysis

###  Farm Tools
- **Fertilizer Calculator** - NPK-based fertilizer recommendations
- **Pesticide Calculator** - Safe dosage calculations
- **Spray Scheduling** - Weather-aware spray timing

###  Smart Alerts
- **GNN-Based Network** - Graph Neural Network for farmer alert propagation
- **Weather Alerts** - Frost, rain, and extreme weather warnings
- **Disease Outbreak Alerts** - Community-wide disease notifications

###  Government Schemes
- **PM-KISAN** - Direct benefit information
- **Crop Insurance** - PMFBY scheme details
- **Subsidies** - State-wise subsidy information

### Database Schema (Backend) 
•	users (Role, Language, Voice_Enabled)
•	farmer_profile (Land Size, Soil Type, Irrigation)
•	disease_results (Image ID, Confidence, Severity)
•	market_prices (Mandi Name, Price/Quintal)
•	schemes & scheme_notifications (Govt Subsidies)

### Disease Encyclopedia 
Beyond detection, the app serves as an educational library. We have categorized thousands of images into structured datasets for manual lookup:
•	Categories: Fungicides, Bacterial Effects, Insecticides.
•	Coverage: Apple, Gram, Sugarcane, Wheat, Rice, Cotton, and 20+ other major Indian crops.


## Planned Improvements (Round 2)
### 1. Ganga Alerts (Flood & Water Safety)
•	Objective: To directly address climate uncertainty.
•	Plan: Integration of real-time river level monitoring for farmers in the Ganges basin to provide early evacuation warnings.

 #### 2. Autonomous WhatsApp Agent (Business API)
•	Objective: To remove the barrier of app installation.
•	Plan: Porting the vision_engine and chatbot.py to a WhatsApp number. Farmers will send a photo to a contact, and our server will reply with the diagnosis and audio advice.

 ### 3. Blockchain Supply Chain
•	Objective: To validate the "Company Buyer Listing" feature.
•	Plan: A transparent ledger to record transactions between farmers and corporate buyers, ensuring fair payments and traceability.




##  Quick Start

### Prerequisites
- Node.js 18+ & npm
- Python 3.11+
- MongoDB Atlas account
- Google Gemini API key
- OpenWeatherMap API key

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/kisanji.git
cd kisanji
```

2. **Setup Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python server.py
```

3. **Setup Frontend**
```bash
cd frontend
npm install
npm start
```

4. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs

---

##  Deployment

### Backend (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Set the following:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `MONGO_URL`: Your MongoDB Atlas connection string
   - `DB_NAME`: `echoharvest_db`
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `WEATHER_API_KEY`: Your OpenWeatherMap API key

### Frontend (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository;
3. Set the following:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
4. Add environment variable:
   - `REACT_APP_API_URL`: Your Render backend URL + `/api`
     (e.g., `https://kisanji-backend.onrender.com/api`)

---

##  Project Structure

```
kisanji/
├── backend/
│   ├── server.py           # FastAPI main server
│   ├── agri_brain.py       # Gemini AI integration
│   ├── vision_engine.py    # Disease detection
│   ├── alert_service.py    # GNN alert network
│   ├── crop_recommender.py # ML crop recommendations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service
│   │   └── contexts/       # React contexts
│   ├── public/
│   │   └── images/         # Background images
│   └── package.json
└── README.md
```

---

##  Environment Variables

### Backend (.env)
```env
MONGO_URL=mongodb+srv://...
DB_NAME=echoharvest_db
GEMINI_API_KEY=your_key
WEATHER_API_KEY=your_key
```

### Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000/api
```


