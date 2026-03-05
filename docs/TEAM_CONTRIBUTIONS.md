# KisanJi Team Contributions

## Team Members & Their Work

### 1. Rajat Pundir (@Rajatpundir7)
**Role: Full Stack Developer & Database Architect**

#### Key Contributions:
- **GNN-Based Network Alert System**: Implemented Graph Neural Network for efficient farmer alert propagation across village networks
- **Weather Alerts Module**: Integrated real-time warnings for frost, rain, and extreme weather conditions
- **Disease Outbreak Notifications**: Built community-wide disease alert system with image-based detection
- **Government Schemes Integration**: PM-KISAN, PMFBY Crop Insurance, State-Wise Subsidies
- **Disease Image Gallery Feature**: Interactive crop disease identification tool
- **Database Schema Design**: Designed scalable MongoDB schema with 11 interconnected tables
- **n8n Workflow Automation**: Automated disease detection, weather alerts, and market price workflows
- **WhatsApp Business API Integration (50% Complete)**: Text queries, voice messages, webhook setup

**Files Contributed:**
- `backend/farmer_alert_network.py`
- `backend/alert_service.py`
- `backend/crop_database.json`
- `AgriGraph_Optimizer/main.py`
- `docs/N8N_WHATSAPP_AUTOMATION.md`
- Database schema design

---

### 2. Saurav Beri (@sauravberi16)
**Role: Backend Developer**

#### Key Contributions:
- Backend development and core logic implementation
- Designed and implemented APIs using Python and FastAPI
- Developed agriculture-focused calculators:
  - Fertilizer recommendation system
  - Pesticide dosage calculator
- Request-response flow handling and validation
- Modular code organization for scalability

**Files Contributed:**
- `backend/advanced_fertilizer_calculator.py`
- `backend/pesticide_calculator.py`
- `backend/fertilizer_database.json`
- `backend/backend.py`
- `backend/server.py`

---

### 3. Ankit Negi (@anku251)
**Role: AI/ML Engineer**

#### Key Contributions:
- **Pest Detection Models**: Implemented crop-specific disease detection
  - `corn_mobile_v2.onnx` - Corn diseases (Blight, Rust)
  - `cotton_disease_v2.onnx` - Cotton diseases (Bacterial Blight, Curl Virus)
  - `rice_mobile_v2.onnx` - Rice diseases (Blast, Tungro)
  - `wheat_mobile_v2.onnx` - Wheat diseases (Rust)
  - `sugarcane_mobile_v2.onnx` - Sugarcane detection
  - `plant_doctor.pt` - General YOLOv8 model for leaf scanning
- **Crop Recommender**: ML model analyzing soil (N, P, K, pH) and environmental conditions
- **API Integration**: Mandi API, Weather API integration
- **Voice Assistant**: Gemini API integration for AgriBrain chatbot

**Files Contributed:**
- `pest_detection.py`
- `vision_engine.py`
- `crop_engine.py`
- `crop_recommender.pkl`
- `backend/voice_assistant.py`
- `backend/agri_brain.py`
- Model files (*.onnx, *.pt)

---

### 4. Devesh Singh (@singhdevesh9net)
**Role: Full Stack Developer - Flood Alert System**

#### Key Contributions:
- **Ganga River Flood Alert System**: Real-time flood monitoring dashboard
- Live monitoring of 8 cities (Varanasi, Patna, Haridwar, Prayagraj, Kanpur, Farakka, Rishikesh, Kolkata)
- Traffic light indicators for flood warnings (red/orange/green)
- Region and severity level filtering
- Population impact and rainfall data display
- Clean, modern UI with smooth animations

**Technologies Used:**
- Django backend
- Vanilla JavaScript frontend
- Real-time data updates

**Files Contributed:**
- Flood Alert Dashboard components
- Real-time monitoring logic
- UI/UX design for alert system

---

## Project Architecture

```
kisanji/
├── backend/           # FastAPI backend (Saurav, Rajat)
├── frontend/          # React frontend (Team)
├── AgriGraph_Optimizer/  # GNN optimization (Rajat)
├── pest_detection.py  # AI models (Ankit)
├── vision_engine.py   # Computer vision (Ankit)
└── docs/              # Documentation (Team)
```

## Contact

For queries about specific features, contact the respective team member.
