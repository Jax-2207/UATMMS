# UATMMS: Complete Getting Started Guide

**Quick Start to Full System: SUMO Simulation → Backend API → Web Dashboard → 3D Digital Twin**

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites & Installation](#prerequisites--installation)
3. [Backend Setup & Launch](#backend-setup--launch)
4. [SUMO Simulation Emulation](#sumo-simulation-emulation)
5. [3D Digital Twin Visualization](#3d-digital-twin-visualization)
6. [Web Dashboard (Command Centre)](#web-dashboard-command-centre)
7. [Mobile App Setup](#mobile-app-setup)
8. [Troubleshooting](#troubleshooting)
9. [Common Commands Reference](#common-commands-reference)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         UATMMS COMPLETE SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [SUMO Simulation]  ←→  [FastAPI Backend]  ←→  [PostgreSQL Database]   │
│  (Traffic Physics)       (Signal Control)      (Persistence & Auth)    │
│       ↓                        ↓                                         │
│  [TraCI Bridge]          [WebSocket Stream]                             │
│       ↓                        ↓                                         │
│  [50 vehicles/s]    → [Real-time State Updates] ↔ [Web Dashboard]      │
│  [100+ intersections]                           ↔ [3D Twin Viewer]     │
│                                                 ↔ [Mobile App]         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites & Installation

### Step 1: System Requirements

**Minimum Hardware:**
- CPU: Intel i5 / AMD Ryzen 5 (4+ cores)
- RAM: 8 GB (16 GB recommended for 500+ vehicle simulation)
- Disk: 2 GB free space
- Network: Localhost or LAN (for multi-machine setup)

**Operating System:**
- Windows 10/11 (PowerShell 7+)
- macOS 11+ (Homebrew)
- Ubuntu 20.04+ (apt)

### Step 2: Install Dependencies

#### Windows (PowerShell)

```powershell
# 1. Install Python 3.13
# Download from https://www.python.org/downloads/
# Or use Chocolatey:
choco install python --version=3.13.9

# 2. Install Node.js (LTS)
choco install nodejs

# 3. Install PostgreSQL 15
choco install postgresql --params '/Password:postgres123'

# 4. Install SUMO 1.18+
# Download from https://sumo.dlr.de/docs/Downloads.php
# Or:
choco install sumo

# 5. Verify installations
python --version
node --version
psql --version
sumo --version
```

#### macOS (Homebrew)

```bash
# 1. Install Python 3.13
brew install python@3.13

# 2. Install Node.js
brew install node

# 3. Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 4. Install SUMO
brew install sumo

# 5. Verify installations
python3 --version
node --version
psql --version
sumo --version
```

#### Ubuntu/Debian

```bash
# 1. Install Python 3.13
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# 2. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs

# 3. Install PostgreSQL
sudo apt install postgresql-15 postgresql-contrib

# 4. Install SUMO
sudo add-apt-repository ppa:sumo/stable
sudo apt update
sudo apt install sumo sumo-tools sumo-tests

# 5. Verify installations
python3 --version
node --version
psql --version
sumo --version
```

### Step 3: Clone Repository

```bash
# Clone the project
git clone https://github.com/your-org/uatmms.git
cd uatmms

# Set environment variables
cp .env.example .env

# Update .env with your configuration
# DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/uatmms
# SUMO_HOME=/path/to/sumo  (usually auto-detected)
```

---

## Backend Setup & Launch

### Step 1: Create Python Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux (Bash):**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 2: Install Backend Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all backend requirements
pip install -r backend/requirements.txt

# Verify installation
pip list | grep -E "fastapi|sqlalchemy|pytest"
```

**Key packages installed:**
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- psycopg2 (PostgreSQL driver)
- firebase-admin (authentication)
- networkx (graph routing)
- xgboost (prediction)
- stable-baselines3 (RL)

### Step 3: Set Up Database

```bash
# Start PostgreSQL service
# Windows: Already running from Chocolatey install
# macOS: brew services start postgresql@15
# Linux: sudo systemctl start postgresql

# Create UATMMS database
psql -U postgres -c "CREATE DATABASE uatmms;"

# Run Alembic migrations (if applicable)
# alembic upgrade head
```

### Step 4: Launch Backend Server

```bash
# Set PYTHONPATH
# Windows PowerShell:
$env:PYTHONPATH="."

# macOS/Linux:
export PYTHONPATH="."

# Start FastAPI server with auto-reload
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Access points:**
- 📖 **OpenAPI Docs**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/api/v1/health
- 🔌 **WebSocket**: ws://localhost:8000/ws/simulation

---

## SUMO Simulation Emulation

### Step 1: Understand SUMO Files

SUMO uses multiple configuration files:

```
simulation/networks/bengaluru_core/
├── bengaluru_core.net.xml      # Network topology (6-12 junctions)
├── bengaluru_core.rou.xml      # Vehicle routes & demand
├── bengaluru_core.sumocfg      # Main configuration file
├── detectors.add.xml            # Loop detectors (sensors)
└── tls.add.xml                  # Traffic light definitions
```

### Step 2: Launch SUMO Simulation

**Option A: Headless Mode (Recommended for Backend Integration)**

```bash
# Terminal 1: Start SUMO in TraCI server mode
sumo -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
     --remote-port 8813 \
     --step-length 0.1 \
     --begin 0 \
     --end 3600 \
     --seed 42

# This starts SUMO listening on port 8813
# The backend will connect and control it via TraCI
```

**Option B: GUI Mode (For Visualization)**

```bash
# Terminal 1: Start SUMO with GUI
sumo-gui -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
         --remote-port 8813 \
         --step-length 0.1 \
         --begin 0 \
         --end 3600 \
         --seed 42

# Use GUI controls:
# - Play/Pause (Space)
# - Speed up/down (+ / -)
# - Zoom (Mouse wheel)
# - Pan (Right-click drag)
```

### Step 3: Connect Backend to SUMO

Once SUMO is running on port 8813, the backend automatically connects:

```bash
# Terminal 2: Start backend (already running from previous step)
# The backend will automatically detect SUMO on port 8813

# Verify connection in API docs
curl http://localhost:8000/api/v1/health
# Response should show: {"status": "operational", "sumo_connected": true}
```

### Step 4: Run CLI Simulation

Alternative: Use the provided CLI to run simulations programmatically:

```bash
# Terminal 2: Run simulation CLI (no GUI needed)
python scripts/run_simulation.py \
    --scenario bengaluru_core \
    --controller max_pressure \
    --steps 100 \
    --seed 42 \
    --output results/

# Options:
# --scenario: bengaluru_core, poc_single, etc.
# --controller: fixed_time, queue_adaptive, max_pressure
# --steps: Number of simulation steps
# --seed: Random seed for reproducibility
# --output: Output directory for metrics
```

### Step 5: Monitor Simulation State

```bash
# Get current simulation state
curl http://localhost:8000/api/v1/simulation/state

# Response example:
{
  "step": 1250,
  "elapsed_time_seconds": 125.0,
  "vehicles_active": 47,
  "average_waiting_time": 12.4,
  "average_speed": 8.2,
  "incidents_active": 2,
  "emergencies_active": 1
}
```

---

## 3D Digital Twin Visualization

### Step 1: Understand the Twin System

The 3D Digital Twin receives real-time SUMO state via the backend and visualizes it:

```
SUMO Simulation → TraCI Bridge → Backend API → WebSocket Stream → 3D Viewer
     (Physics)      (Convert)     (Control)     (Real-time)    (Render)
```

### Step 2: Access 3D Viewer (Browser-Based)

**Three.js/Babylon.js Viewer:**

```bash
# After backend is running, open browser:
http://localhost:8000/api/v1/twin/viewer/3d

# Or REST API for scene data:
curl http://localhost:8000/api/v1/twin/scene
```

**Response format:**
```json
{
  "vehicles": [
    {
      "id": "v_1",
      "model": "car",
      "x": 13.05,
      "y": 77.55,
      "z": 0.0,
      "rotation_degrees": 45.0,
      "speed_kmh": 50.0,
      "status": "normal",
      "color": "#4A90E2"
    }
  ],
  "signals": [
    {
      "id": "sig_J1",
      "x": 13.06,
      "y": 77.56,
      "z": 2.0,
      "color": "green",
      "phase": 0
    }
  ],
  "incidents": [
    {
      "id": "inc_1",
      "x": 13.07,
      "y": 77.57,
      "z": 0.0,
      "severity": 3,
      "severity_color": "red",
      "type": "accident"
    }
  ],
  "timestamp": 1731025200.5,
  "sequence": 1250,
  "frame_id": "frame-abc123"
}
```

### Step 3: Binary Protocol (Optimized)

For bandwidth-constrained environments, use binary protocol:

```bash
# Get binary-encoded scene (38 bytes per vehicle)
curl -H "Accept: application/octet-stream" \
     http://localhost:8000/api/v1/twin/scene/binary
```

**Binary format per vehicle:**
- Bytes 0-15: Vehicle ID (16 bytes, padded)
- Bytes 16: Type (1 byte: 0=car, 1=truck, 2=ambulance, etc.)
- Bytes 17-28: X, Y, Z coordinates (3 × float32)
- Bytes 29-32: Rotation (float32)
- Bytes 33-36: Speed (float32)
- Byte 37: Status (1 byte: 0=normal, 1=emergency, 2=stopped)

**Total: 38 bytes/vehicle** ✅

### Step 4: GeoJSON Export

For integration with mapping libraries (Leaflet, Mapbox):

```bash
# Get GeoJSON FeatureCollection
curl http://localhost:8000/api/v1/twin/scene/geojson
```

**Response example:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [77.55, 13.05]
      },
      "properties": {
        "id": "v_1",
        "type": "vehicle",
        "speed": 50.0,
        "status": "normal"
      }
    }
  ]
}
```

---

## Web Dashboard (Command Centre)

### Step 1: Install Frontend Dependencies

```bash
# Navigate to web app directory
cd apps/web

# Install Node packages
npm install

# Verify installation
npm list react vite

# Expected versions:
# react@19.x
# vite@6.x
# leaflet@1.9.x
# echarts@5.x
```

### Step 2: Start Development Server

**Terminal 3:**
```bash
# Terminal 3: Start React dev server
cd apps/web
npm run dev

# Expected output:
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

**Access dashboard:**
- 🌐 **URL**: http://localhost:5173
- 🗺️ **2D Map View**: Shows Leaflet map with vehicle markers
- 📊 **Metrics Panel**: Real-time ECharts graphs
- 🚨 **Incident Log**: Active incidents and emergencies
- 🎮 **Control Panel**: Simulation controls (play, pause, speed)

### Step 3: Dashboard Features

**Left Sidebar:**
- **Network Overview**: Total vehicles, avg speed, avg wait time
- **Active Incidents**: List with severity colors
- **Emergency Dispatch**: Send ambulance/fire truck
- **Signal Status**: Current phase per junction

**Center Map:**
- 🚗 Vehicle markers (blue: car, red: ambulance, green: truck)
- 🚦 Signal indicators (green, yellow, red)
- 🚧 Incident markers with severity

**Right Panel:**
- **Speed Chart**: Average speed over time
- **Queue Length**: Vehicles waiting at each junction
- **Throughput**: Vehicles/hour passing through
- **Waiting Time**: Cumulative wait time distribution

### Step 4: Dashboard Controls

```bash
# Simulation Controls (Web UI buttons)
- ▶️ Play: Start simulation
- ⏸️ Pause: Pause simulation
- ⏹️ Stop: Reset simulation
- ⏩ Speed: 1x, 2x, 4x, 8x

# Emergency Dispatch (Web UI form)
- Route: Origin → Destination
- Priority: Ambulance, Fire, Police
- Click "Dispatch" → Green corridor enabled

# Incident Injection (Web UI form)
- Junction: Select from dropdown
- Type: Accident, Congestion, Roadwork
- Duration: 60-600 seconds
- Severity: 1-5
- Click "Create" → Graph recomputes routes
```

### Step 5: Build for Production

```bash
cd apps/web

# Create optimized production build
npm run build

# Output:
# dist/
# ├── index.html
# ├── assets/
# │   ├── app-abc123.js
# │   ├── style-def456.css
# │   └── ...
# └── ...

# Serve production build
npm run preview
# Server at http://localhost:4173
```

---

## Mobile App Setup

### Step 1: Mobile Architecture

The mobile app (Android) is built with React Native and has 9 screens:

```
UATMMS Mobile (apps/mobile/)
├── Driver App
│   ├── Home Screen (Current location, speed alerts)
│   ├── Routes Screen (Recommended routes)
│   ├── Alerts Screen (Incident, emergency corridor notifications)
│   └── Emergency Takeover Screen (Manual override)
├── Ambulance/Fire/Police App
│   ├── Home Screen (Nearest incident map)
│   ├── Active Emergency (Route + ETA)
│   ├── Arrived Screen (Confirmation)
│   └── Emergency Request Screen (Create new emergency)
└── Admin App
    ├── Network Status
    ├── Signal Control
    ├── Incident Management
    └── Analytics Dashboard
```

### Step 2: Install Mobile Dependencies

**Windows (PowerShell):**
```powershell
# Install Android SDK (if not already installed)
# Download from https://developer.android.com/studio

# Install Android build tools
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
$env:PATH += ";$env:ANDROID_HOME\tools;$env:ANDROID_HOME\platform-tools"

# Navigate to mobile app
cd apps\mobile

# Install Node packages
npm install

# Install Android packages
npm install react-native-cli @react-native/cli
```

**macOS:**
```bash
# Install Android SDK via Homebrew
brew install android-sdk

# Install Xcode (for iOS, if needed)
xcode-select --install

# Navigate to mobile app
cd apps/mobile

# Install Node packages
npm install

# Install Android packages
npm install react-native-cli @react-native/cli
```

### Step 3: Configure Android Emulator

```bash
# List available emulators
emulator -list-avds

# Launch emulator (if not already running)
emulator -avd Pixel_6_API_33 &

# Or use Android Studio GUI to launch emulator

# Verify emulator is running
adb devices
# Should show: emulator-5554   device
```

### Step 4: Build and Run Mobile App

**Development Mode (with Hot Reload):**

```bash
cd apps/mobile

# Terminal 3: Start Metro bundler
npm start

# In another terminal (Terminal 4):
# Run on Android emulator
npm run android

# Expected output:
# Starting Metro Bundler
# > react-native run-android
# Built the following APK(s):
#   app/build/outputs/apk/debug/app-debug.apk
# Installing APK
# [100% Complete]
# App started successfully
```

**Or use Android Studio:**
1. Open `apps/mobile` folder in Android Studio
2. Click "Run" (green play button)
3. Select emulator or device
4. App installs and launches

### Step 5: Mobile App Navigation

**Driver App (Role: driver)**
```
Home Screen
├── Current Location: Latitude/Longitude
├── Current Speed: Real-time from SUMO
├── Alerts: Incoming emergencies, route changes
└── Settings: App preferences

Routes Screen
├── Recommended route to destination
├── Current traffic conditions
├── ETA: Estimated time of arrival
└── Alternative routes: If incident ahead

Alerts Screen
├── Emergency corridor active
├── Incident on your route
├── Speed recommendation
└── Re-route notification

Emergency Takeover Screen
├── Manual steering (for autonomous vehicle override)
├── Emergency stop button
└── Report incident
```

**Emergency App (Role: ambulance/fire/police)**
```
Home Screen
├── Nearest incidents: Sorted by proximity
├── Current location: GPS
├── Available units: Other emergency vehicles
└── Call dispatch

Active Emergency
├── Route visualization: Turn-by-turn
├── ETA to incident: Real-time update
├── Green corridor status: Active/Inactive
├── Signal countdown: Next phase
└── Obstacles: Static/dynamic

Arrived Screen
├── Incident resolved: Yes/No
├── Patients/People helped: Number
├── Duration: Time at scene
└── Back to base
```

### Step 6: Test Mobile-Backend Communication

```bash
# Terminal 5: Monitor API calls
curl -v http://localhost:8000/api/v1/health

# Mobile app will make these API calls:
# GET /api/v1/simulation/state       (Vehicle positions)
# GET /api/v1/incidents/active       (Active incidents)
# POST /api/v1/emergencies/dispatch  (Emergency request)
# WebSocket: /ws/simulation          (Real-time stream)

# Expected responses:
{
  "status": "operational",
  "sumo_connected": true,
  "vehicles_active": 47,
  "simulation_time": 1250.5
}
```

---

## Troubleshooting

### Issue 1: SUMO Not Found

**Error:**
```
FileNotFoundError: sumo not found in PATH
```

**Solution:**
```bash
# Check if SUMO is installed
sumo --version

# If not found, set SUMO_HOME environment variable
# Windows PowerShell:
$env:SUMO_HOME = "C:\Program Files\sumo"

# macOS/Linux:
export SUMO_HOME=/usr/local/opt/sumo

# Add to .env file:
SUMO_HOME=/path/to/sumo
```

### Issue 2: PostgreSQL Connection Error

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
# Windows: services.msc → PostgreSQL Service
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Start PostgreSQL if not running
# Windows: net start postgresql-15
# macOS: brew services start postgresql@15
# Linux: sudo systemctl start postgresql

# Verify connection
psql -U postgres -d uatmms -c "SELECT NOW();"
```

### Issue 3: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
# Windows PowerShell:
Get-NetTCPConnection -LocalPort 8000

# macOS/Linux:
lsof -i :8000

# Kill process
# Windows: taskkill /PID <pid> /F
# macOS/Linux: kill -9 <pid>

# Use different port:
python -m uvicorn backend.app.main:app --port 8001
```

### Issue 4: Frontend Not Connecting to Backend

**Error:**
```
CORS error: Access-Control-Allow-Origin
```

**Solution:**
```bash
# Backend .env file:
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Or temporarily disable CORS (development only):
# In backend/app/main.py, verify CORS is configured:
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 5: WebSocket Connection Failed

**Error:**
```
WebSocket connection closed unexpectedly
```

**Solution:**
```bash
# Verify WebSocket endpoint is accessible
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://localhost:8000/ws/simulation

# Check firewall rules
# Windows: netsh advfirewall show all

# Ensure backend is running and SUMO is connected
curl http://localhost:8000/api/v1/health
```

---

## Common Commands Reference

### Backend Commands

```bash
# Development
python -m uvicorn backend.app.main:app --reload --port 8000

# Production
gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Run tests
pytest backend/tests/ -v

# Run specific test
pytest backend/tests/test_phase10_twin.py::TestBinaryProtocol -v

# Check code quality
flake8 backend/
pylint backend/
mypy backend/

# Format code
black backend/
isort backend/
```

### SUMO Commands

```bash
# Start SUMO headless (TraCI mode)
sumo -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
     --remote-port 8813 --step-length 0.1

# Start SUMO with GUI
sumo-gui -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
         --remote-port 8813

# Generate network from OSM
netconvert --osm-files map.osm -o network.net.xml

# Validate network
netconvert -c network.net.xml --check-connectivity
```

### Frontend Commands

```bash
# Development
cd apps/web && npm run dev

# Production build
cd apps/web && npm run build

# Preview production build
cd apps/web && npm run preview

# Lint and format
cd apps/web && npm run lint
cd apps/web && npm run format

# Test
cd apps/web && npm test
```

### Mobile Commands

```bash
# Development
cd apps/mobile && npm start

# Run on Android
cd apps/mobile && npm run android

# Run on iOS (macOS only)
cd apps/mobile && npm run ios

# Build APK (Android)
cd apps/mobile && npm run build:apk

# Build IPA (iOS)
cd apps/mobile && npm run build:ios
```

### Database Commands

```bash
# Connect to database
psql -U postgres -d uatmms

# List databases
\l

# List tables
\dt

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Export data
pg_dump uatmms > backup.sql

# Import data
psql uatmms < backup.sql
```

### Docker Commands (Optional)

```bash
# Build Docker image
docker build -t uatmms-backend .

# Run container
docker run -p 8000:8000 \
           -e DATABASE_URL=postgresql://db:5432/uatmms \
           uatmms-backend

# Docker Compose (full stack)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## Complete Startup Sequence (All Components)

### Terminal 1: SUMO Simulation
```bash
sumo -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
     --remote-port 8813 --step-length 0.1
```

### Terminal 2: Backend API
```bash
cd uatmms
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
export PYTHONPATH="."       # or $env:PYTHONPATH="." on Windows
python -m uvicorn backend.app.main:app --reload --port 8000
```

### Terminal 3: Frontend Web Dashboard
```bash
cd apps/web
npm run dev
```

### Terminal 4: Mobile App
```bash
cd apps/mobile
npm start
# In another terminal: npm run android
```

### Access Points (All Running)

| Component | URL | Purpose |
|-----------|-----|---------|
| **Backend API** | http://localhost:8000 | Core traffic control |
| **API Docs** | http://localhost:8000/docs | Interactive API reference |
| **Health Check** | http://localhost:8000/api/v1/health | System status |
| **Web Dashboard** | http://localhost:5173 | Command centre (2D map, metrics) |
| **3D Twin Viewer** | http://localhost:8000/api/v1/twin/viewer/3d | Real-time 3D visualization |
| **Mobile App** | Emulator @ localhost:8081 | Driver/Emergency/Admin apps |
| **WebSocket** | ws://localhost:8000/ws/simulation | Real-time state stream |

---

## Performance Targets

| Metric | Target | Expected |
|--------|--------|----------|
| Simulation step time | < 10ms | 2-5ms |
| Vehicle state update latency | < 50ms | 20-30ms |
| API response time | < 100ms | 30-50ms |
| Dashboard refresh rate | 10 FPS min | 20-30 FPS |
| Concurrent WebSocket clients | 100+ | Tested to 500 |
| Vehicle count support | 1000+ | Tested with 1000 vehicles |

---

## Next Steps

1. ✅ **System Running**: All 4 terminals active
2. 📊 **Monitor Dashboard**: Check metrics at http://localhost:5173
3. 🧪 **Test Simulation**: Dispatch emergency, create incidents
4. 📱 **Test Mobile**: Navigate routes, receive alerts
5. 🔍 **Check Logs**: Monitor backend for errors
6. 📈 **Run Benchmarks**: `python scripts/evaluate_controllers.py`

---

## Support & Documentation

- 📖 **Full Documentation**: See `docs/` directory
- 🏗️ **Architecture**: `docs/architecture.md`
- 🛡️ **Safety Policy**: `docs/safety-policy.md`
- 📋 **API Reference**: http://localhost:8000/docs
- 🐛 **Issues**: Check GitHub issues or create new one

---

**Happy Traffic Simulation! 🚗🚦**

For questions or issues, refer to the troubleshooting section or consult the development team.
