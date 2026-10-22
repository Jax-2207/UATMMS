# UATMMS Quick Start Reference Card

**Print this page or keep it open while setting up the project!**

---

## One-Liner Quick Start

```bash
# Clone, setup, and run everything (macOS/Linux)
git clone <repo> && cd uatmms && python -m venv .venv && source .venv/bin/activate && \
pip install -r backend/requirements.txt && \
python -m uvicorn backend.app.main:app --reload &
sumo -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg --remote-port 8813 &
cd apps/web && npm install && npm run dev
```

---

## 4-Terminal Setup (Easiest Way)

| Terminal | Command | Purpose | Access |
|----------|---------|---------|--------|
| **T1: SUMO** | `sumo -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg --remote-port 8813` | Traffic physics simulation | Port 8813 |
| **T2: Backend** | `python -m uvicorn backend.app.main:app --reload --port 8000` | REST API + WebSocket | http://localhost:8000 |
| **T3: Web** | `cd apps/web && npm run dev` | Dashboard & command centre | http://localhost:5173 |
| **T4: Mobile** | `cd apps/mobile && npm start` | Android emulator app | Emulator @ 8081 |

---

## Installation (One-Time Setup)

### Prerequisites
```bash
# Verify all installed
python --version      # Python 3.13+
node --version        # Node 18+
psql --version        # PostgreSQL 15+
sumo --version        # SUMO 1.18+
```

### Backend Setup (T2 Preparation)
```bash
# 1. Clone repo
git clone <repo> && cd uatmms

# 2. Virtual environment
python -m venv .venv

# 3. Activate (pick your OS)
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

# 4. Dependencies
pip install -r backend/requirements.txt

# 5. Database
psql -U postgres -c "CREATE DATABASE uatmms;"
```

### Frontend Setup (T3 Preparation)
```bash
cd apps/web
npm install
```

### Mobile Setup (T4 Preparation)
```bash
cd apps/mobile
npm install
# Start Android emulator first (Android Studio)
```

---

## Running Each Component

### Terminal 1: SUMO Simulation

**Headless (recommended for backend integration):**
```bash
sumo -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
     --remote-port 8813 --step-length 0.1
```

**GUI (for visualization):**
```bash
sumo-gui -c simulation/networks/bengaluru_core/bengaluru_core.sumocfg \
         --remote-port 8813 --step-length 0.1
```

**Wait for:** `Loaded 50 vehicles, 12 junctions`

### Terminal 2: Backend API

**Development (with hot-reload):**
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

**Production:**
```bash
gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Wait for:** `Application startup complete`

**Verify connection:**
```bash
curl http://localhost:8000/api/v1/health
# Response: {"status": "operational", "sumo_connected": true}
```

### Terminal 3: Web Dashboard

**Development:**
```bash
cd apps/web
npm run dev
```

**Production build:**
```bash
npm run build
npm run preview
```

**Access:** http://localhost:5173

### Terminal 4: Mobile App

**Start metro bundler:**
```bash
cd apps/mobile
npm start
```

**In another terminal, run app:**
```bash
npm run android  # Android emulator
npm run ios      # iOS (macOS only)
```

**Wait for:** `Successfully compiled` message

---

## Key Endpoints & URLs

### Backend API
| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health` | GET | System health | `curl http://localhost:8000/api/v1/health` |
| `/simulation/state` | GET | Current sim state | `curl http://localhost:8000/api/v1/simulation/state` |
| `/twin/scene` | GET | 3D scene JSON | `curl http://localhost:8000/api/v1/twin/scene` |
| `/twin/scene/geojson` | GET | GeoJSON format | `curl http://localhost:8000/api/v1/twin/scene/geojson` |
| `/incidents/active` | GET | Active incidents | `curl http://localhost:8000/api/v1/incidents/active` |
| `/emergencies/dispatch` | POST | Dispatch ambulance | `curl -X POST http://localhost:8000/api/v1/emergencies/dispatch` |
| `/ws/simulation` | WS | Real-time stream | `wscat -c ws://localhost:8000/ws/simulation` |

### Web Dashboard
| Page | URL | Features |
|------|-----|----------|
| Home | http://localhost:5173 | 2D map, vehicles, signals |
| Incidents | http://localhost:5173/incidents | List active incidents |
| Metrics | http://localhost:5173/metrics | Charts & analytics |
| Emergencies | http://localhost:5173/emergencies | Dispatch controls |
| Settings | http://localhost:5173/settings | App configuration |

### 3D Digital Twin
| Format | URL | Use Case |
|--------|-----|----------|
| JSON | http://localhost:8000/api/v1/twin/scene | Web viewers (Three.js, Babylon) |
| GeoJSON | http://localhost:8000/api/v1/twin/scene/geojson | Leaflet/Mapbox mapping |
| Binary | http://localhost:8000/api/v1/twin/scene/binary | Bandwidth-optimized (UDP) |
| Cesium | http://localhost:8000/api/v1/twin/scene/cesium | Cesium.js 3D |

### Documentation
| Page | URL | Content |
|------|-----|---------|
| OpenAPI Docs | http://localhost:8000/docs | Interactive API reference |
| ReDoc | http://localhost:8000/redoc | API documentation |
| Health Check | http://localhost:8000/api/v1/health | System status |

---

## Common Commands

### Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test module
pytest backend/tests/test_phase10_twin.py -v

# Run with coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Run Phase 8-11 tests
pytest backend/tests/test_phase{8,9,10,11}*.py -v

# Quick verification (Phases 8-11 only)
pytest backend/tests/test_phase8*.py backend/tests/test_phase9*.py \
        backend/tests/test_phase10*.py backend/tests/test_phase11*.py
```

### Code Quality

```bash
# Format code
black backend/
isort backend/

# Lint
flake8 backend/
pylint backend/

# Type checking
mypy backend/

# All at once
make quality  # if Makefile exists
```

### Database Management

```bash
# Create database
psql -U postgres -c "CREATE DATABASE uatmms;"

# Connect to database
psql -U postgres -d uatmms

# Export data
pg_dump uatmms > backup.sql

# Import data
psql uatmms < backup.sql

# Reset database
psql -U postgres -c "DROP DATABASE uatmms; CREATE DATABASE uatmms;"
```

### Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env  # or use your editor

# Key variables to set
DATABASE_URL=postgresql://postgres:password@localhost:5432/uatmms
SUMO_HOME=/usr/local/bin/sumo
FIREBASE_PROJECT_ID=your_project_id
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Troubleshooting Checklist

| Issue | Check | Fix |
|-------|-------|-----|
| **SUMO not found** | `sumo --version` | Install SUMO or set `SUMO_HOME` |
| **Port in use** | `lsof -i :8000` | Kill process or use different port |
| **DB connection error** | `psql -U postgres` | Start PostgreSQL service |
| **WebSocket failed** | Backend logs | Verify CORS headers |
| **Mobile app won't start** | Android emulator running? | Start emulator from Android Studio |
| **Frontend not connecting** | Check network tab (F12) | Verify backend on port 8000 |
| **Tests failing** | `pytest backend/tests/ -v` | Install all dependencies |

---

## Performance Verification

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status": "operational", "sumo_connected": true, "vehicles": 50}

# Get current state
curl http://localhost:8000/api/v1/simulation/state

# Expected response:
# {
#   "step": 1250,
#   "elapsed_time": 125.0,
#   "vehicles_active": 50,
#   "average_waiting_time": 12.4,
#   "average_speed": 8.2
# }

# Monitor WebSocket
wscat -c ws://localhost:8000/ws/simulation
# Should see real-time state updates every 100ms
```

---

## File Locations (Quick Reference)

```
uatmms/
├── backend/
│   ├── app/main.py              ← FastAPI entry point
│   ├── requirements.txt           ← Dependencies
│   └── tests/                     ← Test suite (259 tests)
├── apps/
│   ├── web/
│   │   ├── package.json           ← Frontend dependencies
│   │   └── src/App.tsx            ← React app
│   └── mobile/
│       ├── package.json           ← Mobile dependencies
│       └── src/App.tsx            ← React Native app
├── simulation/
│   ├── networks/
│   │   └── bengaluru_core/        ← SUMO network files
│   └── scenarios/                 ← Traffic demand profiles
├── docs/
│   ├── architecture.md
│   ├── safety-policy.md
│   └── GETTING_STARTED.md         ← Full setup guide
├── .env.example                   ← Configuration template
├── GETTING_STARTED.md             ← Full guide (this file)
└── README.md                      ← Project overview
```

---

## Network Ports (All Components)

| Component | Port | Protocol | Purpose |
|-----------|------|----------|---------|
| SUMO | 8813 | TraCI | Simulation control |
| Backend API | 8000 | HTTP | REST API & WebSocket |
| Web Dashboard | 5173 | HTTP | Development server |
| Web Dashboard | 4173 | HTTP | Production server |
| PostgreSQL | 5432 | TCP | Database |
| Metro Bundler | 8081 | HTTP | React Native bundler |
| Android Emulator | 5555 | TCP | ADB (Android Debug Bridge) |

**Firewall rules needed:**
- Localhost only: ✅ Safe
- LAN access: Open ports 8000, 5173, 8813
- Production: Use reverse proxy (nginx, Caddy)

---

## Emergency Commands (When Things Go Wrong)

```bash
# Kill all Python processes
pkill -f python

# Kill all Node processes
pkill -f node

# Reset database
psql -U postgres -c "DROP DATABASE uatmms; CREATE DATABASE uatmms;"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json

# Reset git (CAREFUL!)
git reset --hard HEAD
git clean -fd
```

---

## Success Checklist

- [ ] Python 3.13+ installed
- [ ] Node 18+ installed
- [ ] PostgreSQL 15+ running
- [ ] SUMO 1.18+ installed
- [ ] Repository cloned
- [ ] Virtual environment created & activated
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database created
- [ ] `.env` configured
- [ ] All 4 terminals running (SUMO, Backend, Web, Mobile)
- [ ] Health check passes: `curl http://localhost:8000/api/v1/health`
- [ ] Dashboard loads: http://localhost:5173
- [ ] Tests pass: `pytest backend/tests/ -v`

---

## Next Steps After Startup

1. **Monitor Dashboard**: Open http://localhost:5173
2. **Dispatch Emergency**: Click emergency dispatch button
3. **Watch Green Corridor**: Observe signal changes in SUMO GUI
4. **Create Incident**: Use dashboard to inject obstacle
5. **View 3D Twin**: Go to http://localhost:8000/api/v1/twin/viewer/3d
6. **Check Metrics**: View real-time charts on dashboard
7. **Test Mobile**: Receive alerts on phone app
8. **Run Benchmarks**: `python scripts/evaluate_controllers.py`

---

## Support

📖 **Full Guide**: `GETTING_STARTED.md`  
🏗️ **Architecture**: `docs/architecture.md`  
🔐 **Security**: `docs/safety-policy.md`  
📊 **API Docs**: http://localhost:8000/docs  
🐛 **Issues**: Check GitHub or create issue

---

**Ready? Run your 4 terminals and enjoy! 🚗🚦✨**
