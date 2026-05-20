# 🌱 AgriSync Agent — AI Farm Co-Pilot for Nigerian Farmers

> **Google Cloud Rapid Agent Hackathon — Fivetran Track Submission**
> Built with Gemini 2.0 Flash + Fivetran MCP + Google BigQuery

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange) ![Fivetran](https://img.shields.io/badge/Fivetran-MCP-purple) ![BigQuery](https://img.shields.io/badge/BigQuery-Sandbox-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Problem Statement

Nigeria is Africa's largest agricultural economy, with over **90 million smallholder farmers** who lack access to real-time data, crop intelligence, and farm management tools. Poor data visibility leads to:

- ❌ Low crop yields due to uninformed planting decisions
- ❌ No real-time soil/weather monitoring
- ❌ Disconnected data pipelines between farm sensors, weather APIs, and market data
- ❌ No AI-powered advisory tailored to Nigerian crops and conditions

---

## 💡 Solution: AgriSync Agent

AgriSync Agent is an **AI-powered Farm Co-Pilot** that combines:

- 🤖 **Gemini 2.0 Flash** — conversational AI that understands Nigerian farming context
- 🔄 **Fivetran MCP** — automated data pipelines from Google Sheets farm records to BigQuery
- 📊 **Google BigQuery** — warehouse storing farm records, sensor data, and weather summaries
- 🌐 **Streamlit** — beautiful, mobile-friendly chat interface for farmers and agronomists

Farmers can simply **chat in plain English** to get crop recommendations, yield analysis, sensor alerts, and Fivetran pipeline status — all in one place.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGRISYNC AGENT                           │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │ Google Sheets│    │   Weather    │    │  IoT Sensors     │  │
│  │ Farm Records │    │   APIs       │    │  (Soil/Moisture) │  │
│  └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘  │
│         │                  │                      │             │
│         └──────────────────┼──────────────────────┘             │
│                            │                                    │
│                    ┌───────▼────────┐                           │
│                    │  FIVETRAN MCP  │  ← Automated Pipelines    │
│                    │  REST API      │    Trigger Syncs          │
│                    │  (mcp_client)  │    Monitor Status         │
│                    └───────┬────────┘                           │
│                            │                                    │
│                    ┌───────▼────────┐                           │
│                    │ Google BigQuery │  ← farm_records          │
│                    │   Warehouse    │     sensor_readings       │
│                    │ (agrisync-agent│     weather_data          │
│                    │   dataset)     │                           │
│                    └───────┬────────┘                           │
│                            │                                    │
│              ┌─────────────▼──────────────┐                     │
│              │     GEMINI 2.0 FLASH       │                     │
│              │     AI Agent Core          │                     │
│              │                           │                     │
│              │  Tools:                   │                     │
│              │  • query_farm_data        │                     │
│              │  • get_crop_summary       │                     │
│              │  • get_weather_summary    │                     │
│              │  • get_sensor_readings    │                     │
│              │  • list_fivetran_connectors│                    │
│              │  • trigger_fivetran_sync  │                     │
│              │  • get_sync_status        │                     │
│              │  • get_farm_insights      │                     │
│              └─────────────┬──────────────┘                     │
│                            │                                    │
│                    ┌───────▼────────┐                           │
│                    │   STREAMLIT    │  ← Chat Interface         │
│                    │   Frontend     │    Green AG Theme         │
│                    │  (app.py)      │    Sidebar Dashboard      │
│                    └────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 How Fivetran MCP is Used

This project integrates **Fivetran as an MCP (Model Context Protocol) server** through a custom REST API client (`mcp_client.py`). Here's exactly how:

### 1. Tool Exposure to Gemini
Fivetran pipeline operations are exposed as **callable tools** that Gemini 2.0 Flash can invoke during conversations:

| Tool | Fivetran API Endpoint | What It Does |
|------|-----------------------|--------------|
| `list_fivetran_connectors` | `GET /v1/connectors` | Lists all farm data connectors |
| `trigger_fivetran_sync` | `POST /v1/connectors/{id}/sync` | Triggers fresh data sync |
| `get_sync_status` | `GET /v1/connectors/{id}` | Checks pipeline health |
| `list_fivetran_groups` | `GET /v1/groups` | Lists destination groups |

### 2. Real-Time Pipeline Control
When a farmer asks *"Is my farm data up to date?"*, Gemini automatically:
1. Calls `list_fivetran_connectors()` to find the Google Sheets connector
2. Calls `get_sync_status()` to check last sync time
3. Calls `trigger_fivetran_sync()` if data is stale
4. Reports back in plain English to the farmer

### 3. Data Flow
```
Google Sheets (Farm Records)
        ↓  [Fivetran Connector]
Google BigQuery → agrisync.farm_records
        ↓  [BigQuery Helper]
Gemini Tool Call → Natural Language Response
        ↓
Farmer gets actionable insight 🌾
```

---

## 📁 Project Structure

```
agrisync-agent/
│
├── app.py                 # Streamlit UI — green agricultural theme, chat interface
├── agent.py               # AgriSyncAgent class — Gemini 2.0 Flash, 8 tools, tool loop
├── mcp_client.py          # Fivetran REST API client — httpx-based MCP integration
├── bigquery_helper.py     # BigQuery client — farm data queries and demo setup
├── config.py              # Environment config — loads .env, validates credentials
│
├── .env                   # API keys and project config (not committed)
├── service-account.json   # GCP service account credentials (not committed)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud account with BigQuery enabled
- Fivetran account (free trial works)
- Google AI Studio API key (Gemini)

### 1. Clone the Repository

```bash
git clone https://github.com/Ali6nXI/agrisync-agent.git
cd agrisync-agent
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Gemini AI
GOOGLE_API_KEY=your_gemini_api_key_here

# Fivetran
FIVETRAN_API_KEY=your_fivetran_api_key
FIVETRAN_API_SECRET=your_fivetran_api_secret

# Google Cloud / BigQuery
GCP_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=agrisync
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=service-account.json

# App
APP_ENV=development
```

### 5. Add GCP Service Account

Place your `service-account.json` file in the project root directory. The service account needs the **BigQuery Admin** role.

### 6. Run the App

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

### 7. Setup Demo Data

Click **"Setup Demo Data"** in the sidebar to populate BigQuery with 8 Nigerian farm records across states including Kano, Kaduna, Ogun, and Rivers.

---

## 💬 Example Conversations

**Crop Yield Analysis:**
```
You: What crops are Nigerian farmers growing and what is the yield data?
AgriSync: Based on our farm records, farmers across 6 Nigerian states are 
growing maize, cassava, rice, and sorghum. The highest yield is from 
Kaduna state with 3.2 tonnes/hectare for maize...
```

**Pipeline Monitoring:**
```
You: Is my Fivetran data pipeline running correctly?
AgriSync: I checked your Fivetran connectors. Your Google Sheets connector 
last synced 2 hours ago and is healthy. Would you like me to trigger 
a fresh sync to get the latest farm data?
```

**Weather Advisory:**
```
You: What is the weather situation in Kano state for farming?
AgriSync: Current data shows Kano state has an average temperature of 
32°C with 45mm rainfall this week. This is suitable for sorghum 
and millet planting. I recommend...
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Model | Gemini 2.0 Flash | Conversational intelligence + tool calling |
| Data Pipelines | Fivetran MCP REST API | Farm data sync from Google Sheets → BigQuery |
| Data Warehouse | Google BigQuery (Sandbox) | Stores farm records, sensors, weather |
| Frontend | Streamlit | Chat UI with agricultural green theme |
| HTTP Client | httpx | Async Fivetran API calls |
| AI SDK | google-genai | Gemini integration with tool calling |
| Config | python-dotenv | Environment variable management |

---

## 📊 BigQuery Schema

### farm_records
| Column | Type | Description |
|--------|------|-------------|
| farm_id | STRING | Unique farm identifier |
| farmer_name | STRING | Farmer's full name |
| state | STRING | Nigerian state (Kano, Lagos, etc.) |
| crop_type | STRING | Crop being grown |
| yield_kg_per_ha | FLOAT | Yield in kg per hectare |
| season | STRING | Planting season |
| recorded_at | TIMESTAMP | Record timestamp |

### sensor_readings
| Column | Type | Description |
|--------|------|-------------|
| farm_id | STRING | Farm reference |
| sensor_type | STRING | Type (soil_moisture, temperature) |
| value | FLOAT | Sensor reading |
| unit | STRING | Unit of measurement |
| recorded_at | TIMESTAMP | Reading timestamp |

### weather_data
| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Weather date |
| state | STRING | Nigerian state |
| avg_temp_c | FLOAT | Average temperature (°C) |
| rainfall_mm | FLOAT | Rainfall in millimeters |
| humidity_pct | FLOAT | Humidity percentage |

---

## 🌍 Nigerian States Covered

The demo dataset includes farm data from:

- 🌾 **Kano** — Grains, Millet, Sorghum
- 🌽 **Kaduna** — Maize, Groundnuts
- 🍠 **Ogun** — Cassava, Yam
- 🌴 **Rivers** — Plantain, Palm Oil
- 🌿 **Benue** — Rice, Sesame
- 🥜 **Sokoto** — Cowpea, Groundnuts

---

## 🏆 Hackathon Track

**Google Cloud Rapid Agent Hackathon — Fivetran Track**

This project specifically demonstrates:

1. ✅ **Fivetran MCP Integration** — Fivetran REST API used as MCP tools callable by Gemini
2. ✅ **Agentic Data Pipeline Control** — AI can trigger, monitor, and report on Fivetran syncs
3. ✅ **Real-World Impact** — Solving food security challenges for 90M+ Nigerian farmers
4. ✅ **Full-Stack AI Agent** — End-to-end from data ingestion to conversational interface
5. ✅ **Google Cloud Native** — BigQuery + Gemini + Google Sheets all on GCP

---

## 👨‍💻 Author

**Joseph** — AgriSync Agent
- GitHub: [@Ali6nXI](https://github.com/Ali6nXI)
- Project: [agrisync-agent](https://github.com/Ali6nXI/agrisync-agent)

---

## 📄 License

MIT License — feel free to use and build upon this project.

---

*Built with ❤️ for Nigerian farmers and the Google Cloud Rapid Agent Hackathon 2025*