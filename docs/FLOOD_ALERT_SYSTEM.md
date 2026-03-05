# Ganga River Flood Alert System

**Author: Devesh Singh (@singhdevesh9net)**  
**Role: Full Stack Developer - Flood Alert System**

---

## Overview

A real-time flood monitoring dashboard for cities along the Ganga River. Built with Django and vanilla JavaScript.

## What does this do?

This app monitors water levels across 8 major cities along the Ganga River and shows you which areas are at risk. The dashboard updates in real-time and uses color-coded alerts to make it easy to see where flooding might happen.

---

## Features

### Live Monitoring
- **8 Cities Covered**: Varanasi, Patna, Haridwar, Prayagraj, Kanpur, Farakka, Rishikesh, Kolkata

### Visual Indicators
- 🔴 **Red (Danger)**: Immediate flood risk - evacuation recommended
- 🟠 **Orange (Warning)**: Elevated water levels - stay alert
- 🟢 **Green (Safe)**: Normal water levels

### Dashboard Capabilities
- Filter by region or severity level
- Shows affected population count
- Displays rainfall data in real-time
- Blinking traffic light indicators for urgency

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Backend | Django (Python) |
| Frontend | Vanilla JavaScript |
| Styling | CSS3 with animations |
| Data | Real-time water level APIs |

---

## Integration with KisanJi

The Flood Alert System complements the KisanJi platform by:

1. **Farmer Safety**: Alerting farmers in flood-prone areas before disasters strike
2. **Crop Protection**: Enabling farmers to take preventive measures for their crops
3. **Advisory System**: Integrating with weather alerts module for comprehensive risk assessment
4. **Village-Level Notifications**: Connecting with GNN-based alert network for targeted warnings

---

## API Endpoints

```
GET /api/flood/cities/          - List all monitored cities
GET /api/flood/alerts/          - Current alert status for all cities
GET /api/flood/city/{id}/       - Detailed info for specific city
GET /api/flood/history/{city}/  - Historical water level data
POST /api/flood/subscribe/      - Subscribe to flood notifications
```

---

## UI Preview

The dashboard features:
- Clean, modern design
- Smooth CSS animations
- Responsive layout for mobile devices
- Real-time data refresh every 30 seconds

---

## Repository

This module is maintained in a separate repository but integrates with the main KisanJi platform through API endpoints.

**Contact**: singhdevesh9netg@gmail.com
