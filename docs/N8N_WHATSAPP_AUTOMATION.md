# n8n Automation & WhatsApp Integration

**Author: Rajat Pundir (@Rajatpundir7)**  
**Role: Full Stack Developer - Automation & Integration**  
**Status: 50% Complete**

---

## Overview

This module implements workflow automation using n8n and WhatsApp Business API integration to make KisanJi accessible without app installation.

---

## n8n Workflow Automation

### Implemented Workflows

#### 1. Disease Detection Workflow
```
Trigger (Webhook) → Image Processing → Vision Engine → Disease Result → Notification
```
- Receives crop images via webhook
- Processes through ONNX models
- Returns diagnosis with treatment recommendations

#### 2. Weather Alert Automation
```
Scheduler (Every 6 hours) → Weather API → Risk Analysis → Farmer Notifications
```
- Automated weather data fetching
- Frost/rain/heatwave detection
- Push notifications to affected farmers

#### 3. Market Price Updates
```
Scheduler (Daily 8 AM) → eNAM API → Price Comparison → Alert Generation
```
- Daily mandi price fetching
- Price trend analysis
- Sell/Hold recommendations

#### 4. GNN Alert Propagation
```
Disease Report → Graph Analysis → Similar Farmer Detection → Bulk Alerts
```
- Automated alert network using Graph Neural Networks
- Community-wide disease outbreak notifications

---

## WhatsApp Business API Integration (50% Complete)

### Architecture

```
Farmer WhatsApp → Twilio/Meta API → n8n Webhook → KisanJi Backend → Response
```

### Completed Features ✅

1. **Text Query Handling**
   - Farmers send queries in Hindi/English
   - Gemini AI processes and responds
   - Response translated to farmer's language

2. **Webhook Setup**
   - Twilio webhook configuration
   - Message parsing and routing
   - Response formatting for WhatsApp

3. **Voice Message Support**
   - Audio message download
   - Whisper transcription
   - Text response generation

### In Progress 🔄

4. **Image-based Disease Detection**
   - Image download from WhatsApp
   - Vision engine processing
   - Result with treatment audio

5. **Location-based Services**
   - Mandi prices based on location
   - Weather alerts for farmer's village
   - Nearby service provider suggestions

---

## n8n Workflow Files

```
n8n_workflows/
├── disease_detection.json       # Disease detection workflow
├── weather_alerts.json          # Weather monitoring workflow
├── market_prices.json           # Mandi price updates
├── whatsapp_webhook.json        # WhatsApp message handler
└── gnn_alerts.json              # GNN-based alert propagation
```

---

## Environment Variables

```env
# n8n Configuration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/
N8N_API_KEY=your_n8n_api_key

# WhatsApp Business API
WHATSAPP_BUSINESS_ID=your_business_id
WHATSAPP_API_TOKEN=your_api_token
WHATSAPP_PHONE_NUMBER=+91XXXXXXXXXX

# Twilio (Alternative)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## API Endpoints for n8n

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/disease` | POST | Disease detection webhook |
| `/webhook/weather` | GET | Weather data fetch |
| `/webhook/whatsapp` | POST | WhatsApp message handler |
| `/webhook/alert` | POST | Manual alert trigger |

---

## Usage Example

### WhatsApp Message Flow

1. **Farmer sends**: "मेरी गेहूं की फसल में पीले धब्बे हैं"
2. **System detects**: Hindi language, wheat crop issue
3. **AI Response**: Disease identification + treatment in Hindi
4. **Audio**: Voice response generated and sent

### Image Detection Flow

1. **Farmer sends**: Crop leaf photo
2. **System processes**: Vision engine analysis
3. **Response**: Disease name, confidence %, treatment steps
4. **Follow-up**: Nearby pesticide shop locations

---

## Roadmap

- [x] n8n basic workflow setup
- [x] WhatsApp webhook integration
- [x] Text query handling
- [x] Voice message transcription
- [ ] Image disease detection via WhatsApp
- [ ] Location-based recommendations
- [ ] Automated follow-up messages
- [ ] Multi-language audio responses

---

## Contact

For integration queries: rajatpundir07@gmail.com
