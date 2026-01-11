# 🌾 Kisan.JI – Smart Agriculture Platform

**Live Demo:** [https://kisanji-frontend.vercel.app](https://kisanji-frontend.vercel.app)
**Explainer Video:** [https://youtu.be/ETIP463LaVk?si=M5DlUlwCZ6KcZCZz](https://youtu.be/ETIP463LaVk?si=M5DlUlwCZ6KcZCZz)

**Team Name:** Kedari
**Event:** Hack The Winter
**University:** Graphic Era Hill University, Dehradun

---

## 🚜 Overview

**Kisan.JI** is an AI-powered, mobile-first **“Village Nervous System”** built to empower smallholder Indian farmers. It bridges modern agricultural science with grassroots farming by delivering real-time insights on crops, pests, diseases, weather, markets, and government schemes.

This repository contains a **fully functional prototype** with:

* ⚙️ Python (FastAPI) backend
* 🎨 HTML/CSS/JS + React frontend
* 🧠 Optimized ONNX-based deep learning models for fast inference

---

## 🧠 Key Features

### 🤖 AI-Powered Assistant

* **Gemini AI Integration** – Smart chatbot for farming queries
* **Voice Assistant** – Multilingual support (Hindi, Marathi, Tamil, Telugu, etc.)
* **Text-to-Speech** – Audio responses in regional languages

### 🌱 Crop Management

* **Disease Detection** – ONNX Runtime-based plant disease classification

  * Models: `corn_mobile_v2.onnx`, `sugarcane_mobile_v2.onnx`, `wheat_mobile_v2.onnx`, `rice_mobile_v2.onnx`, `cotton_mobile_v2.onnx`
  * Workflow: *Image → ONNX Inference → Disease & Severity*

* **Pest Detection** – YOLOv8-powered pest identification

* **Crop Recommendation Engine**

  * ML Model: Random Forest (`crop_recommender.pkl`)
  * Inputs:

    * Nitrogen (N)
    * Phosphorus (P)
    * Potassium (K)
    * Soil pH
    * Rainfall
    * Water Source (Rain / Tubewell / Borewell)
  * Output: Best-suited high-yield crop for the season

---

### 📊 Market Intelligence

* **Live Mandi Prices** – Real-time prices via eNAM API
* **Weather Forecasts** – OpenWeatherMap integration
* **Price Trends** – Historical price analysis

---

### 🛠️ Farm Tools

* **Fertilizer Calculator** – NPK-based recommendations
* **Pesticide Calculator** – Safe dosage computation
* **Spray Scheduling** – Weather-aware spray planning

---

### 🚨 Smart Alerts

* **GNN-Based Alert Network** – Graph Neural Network for farmer-to-farmer alert propagation
* **Weather Alerts** – Frost, rain & extreme weather warnings
* **Disease Outbreak Alerts** – Community-level notifications

---

### 🏛️ Government Schemes

* **PM-KISAN** – Direct benefit information
* **PMFBY** – Crop insurance details
* **Subsidies** – State-wise subsidy information

---

## 📚 Disease Encyclopedia

Beyond detection, Kisan.JI also acts as a learning platform:

* **Categories:** Fungicides, Bacterial Diseases, Insect Pests
* **Crops Covered:** Apple, Gram, Sugarcane, Wheat, Rice, Cotton & 20+ others
* **Usage:** Manual lookup with categorized image datasets

---

## 🧬 System Architecture & Flow

* **Architecture Diagrams:** `architecture.jpeg`, `arch.jpeg`
* **Flowcharts:** `flow.jpeg`, `flowchart.jpeg`

---

## 🗂️ Database Schema (Backend)

* `users` – Role, Language, Voice Enabled
* `farmer_profile` – Land Size, Soil Type, Irrigation
* `disease_results` – Image ID, Confidence, Severity
* `market_prices` – Mandi Name, Price per Quintal
* `schemes` & `scheme_notifications` – Government benefits

---

## 🚀 Planned Improvements (Round 2)

### 1️⃣ Ganga Flood & Water Alerts

* **Goal:** Climate-resilience for farmers
* **Plan:** Real-time river-level monitoring with early evacuation alerts

### 2️⃣ Autonomous WhatsApp AI Agent

* **Goal:** Zero-installation access
* **Plan:** WhatsApp Business API integration for image-based disease diagnosis + voice advice

### 3️⃣ Blockchain Supply Chain

* **Goal:** Transparent farmer–buyer transactions
* **Plan:** Blockchain ledger for traceability and fair payments

---

## ⚙️ Quick Start

### 🔧 Prerequisites

* Node.js 18+
* Python 3.11+
* MongoDB Atlas account
* Google Gemini API Key
* OpenWeatherMap API Key

---

### 🖥️ Local Development

#### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/kisanji.git
cd kisanji
```

#### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python server.py
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

#### Access

* **Frontend:** [http://localhost:3000](http://localhost:3000)
* **Backend API:** [http://localhost:8000/api](http://localhost:8000/api)
* **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☁️ Deployment

### Backend (Render)

* Root Directory: `backend`
* Build Command: `pip install -r requirements.txt`
* Start Command:

```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**

* `MONGO_URL`
* `DB_NAME=echoharvest_db`
* `GEMINI_API_KEY`
* `WEATHER_API_KEY`

---

### Frontend (Vercel)

* Root Directory: `frontend`
* Build Command: `npm run build`
* Output Directory: `build`

**Environment Variable:**

```env
REACT_APP_API_URL=https://your-backend-url/api
```

---

## 📁 Project Structure

```
kisanji/
├── backend/
│   ├── server.py
│   ├── agri_brain.py
│   ├── vision_engine.py
│   ├── alert_service.py
│   ├── crop_recommender.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

---

## 🤝 Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is developed as part of a **Hackathon Prototype** and is intended for educational and demonstration purposes.

---

🌾 *Built with technology, for the roots of India.*
