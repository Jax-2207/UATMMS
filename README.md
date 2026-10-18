# UATMMS: Universal Automatic Traffic Management and Manipulation System

> **AI-assisted, network-level traffic management system built on microscopic simulation, dynamic graph routing, safety-validated signal controllers, and emergency green corridors.**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6+-646CFF.svg)](https://vitejs.dev/)
[![SUMO](https://img.shields.io/badge/SUMO-1.20+-orange.svg)](https://sumo.dlr.de/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

---

## 1. Project Overview & Core Philosophy

UATMMS coordinates multi-intersection urban traffic networks through a continuous closed loop:

$$\text{Observe} \longrightarrow \text{Predict} \longrightarrow \text{Optimize} \longrightarrow \text{Validate} \longrightarrow \text{Control} \longrightarrow \text{Monitor}$$

### Non-Negotiable Core Principles
1. **Simulation as Single Source of Truth**: Eclipse SUMO owns physical vehicle movements, speeds, queues, and signal states. 2D/3D dashboards are subscribers, never inventing vehicle positions.
2. **Safety as a Hard Gate**: A deterministic **Safety Validator** verifies all signal adjustments against physical minimum/maximum greens, pedestrian clearance intervals, and non-conflicting phase matrices before commands are executed.
3. **Network-Level Coordinated Control**: Traffic is optimized globally across intersections (via Max-Pressure and PPO Reinforcement Learning) rather than treating individual junctions in isolation.
4. **Emergency Green Corridors**: Prioritized dynamic routing and scheduled signal preemption for emergency vehicles (ambulances, fire engines) with cross-traffic conflict handling.

---

## 2. Repository Layout

```
MegaProject/
├── apps/
│   └── web/                   # React + TypeScript + Vite Command Centre
├── backend/
│   ├── app/
│   │   ├── api/               # REST routes (health, simulation, emergencies, incidents)
│   │   ├── auth/              # Firebase token verification & server-side RBAC
│   │   ├── core/              # Config, logging, error hierarchy
│   │   ├── db/                # SQLAlchemy models & sessions
│   │   ├── emergency/         # Corridor scheduler & dispatch
│   │   ├── evaluation/        # Metrics collection & benchmarks
│   │   ├── incidents/         # Road closures, obstacle injection, hazard models
│   │   ├── network/           # Graph topology & SUMO ID mapping
│   │   ├── prediction/        # XGBoost congestion forecast models
│   │   ├── routing/           # Dijkstra & A* dynamic cost routing
│   │   ├── safety/            # Deterministic Safety Validator & fallbacks
│   │   ├── schemas/           # Pydantic v2 schemas
│   │   ├── simulation/        # SUMO TraCI lifecycle & state manager
│   │   └── main.py            # FastAPI entry point & WebSockets
│   ├── tests/                 # Pytest test suite
│   └── requirements.txt       # Backend dependencies
├── docs/
│   ├── architecture.md        # Architecture Decision Records (ADRs)
│   ├── coding-conventions.md  # Python, TS, and Git development standards
│   ├── experiment-protocol.md # Benchmark protocol, metrics & fair comparison rules
│   └── safety-policy.md       # Safety constraints, clearance times & fallbacks
├── rl/
│   ├── env/                   # Gymnasium TraCI wrapper
│   ├── training/              # PPO training routines
│   ├── checkpoints/           # Trained policy checkpoints
│   └── evaluations/           # Policy comparison benchmark logs
├── scripts/
│   ├── run_simulation.py      # Simulation runner CLI
│   └── evaluate_controllers.py # Controller benchmarking harness
├── simulation/
│   ├── configs/               # Run configurations
│   ├── networks/              # SUMO .net.xml and OSM networks
│   └── scenarios/             # Traffic demand & incident definitions
├── visualization/
│   └── unity-or-godot/        # 3D digital twin scene & bridge
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md
```

---

## 3. Getting Started

### Prerequisites
* **Python**: 3.11+ (Python 3.13 recommended)
* **Node.js**: v18+ or v22+
* **SUMO**: Eclipse SUMO 1.18+ (download from [sumo.dlr.de](https://sumo.dlr.de/docs/Downloads.php))

### 1. Clone & Configure Environment
```bash
git clone <repo-url>
cd MegaProject

# Copy environment configuration
cp .env.example .env
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Run unit tests to verify setup
$env:PYTHONPATH="."
pytest backend/tests -v
```

### 3. Launch Backend API Server
```bash
# Starts FastAPI server with hot-reload on http://127.0.0.1:8000
python -m uvicorn backend.app.main:app --reload --port 8000
```
* **Interactive OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **System Health Endpoint**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
* **WebSocket Simulation Stream**: `ws://127.0.0.1:8000/ws/simulation`

### 4. Run Headless Simulation CLI
```bash
$env:PYTHONPATH="."
python scripts/run_simulation.py --scenario default_6junctions --steps 50
```

### 5. Launch Frontend Command Centre
```bash
cd apps/web
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 4. Safety Validation Guarantee

All signal adjustments must be approved by `backend.app.safety.validator.SafetyValidator`. If an algorithm attempts an unsafe action (e.g., flipping a green light too quickly or conflicting phases), it is rejected and logged:

```json
{
  "junction_id": "J1_MG_Road",
  "approved": false,
  "reason": "Minimum green violation: junction J1_MG_Road has been in phase 0 for 4.0s (required: 10.0s).",
  "is_emergency": false
}
```

---

## 5. Development Roadmap Status
- [x] **Phase 0: Project Setup & Repository Skeleton** (Current)
- [ ] **Phase 1: SUMO Proof of Concept (TraCI Python Adapter)**
- [ ] **Phase 2: Multi-Intersection Network & OSM Import**
- [ ] **Phase 3: Dynamic Graph Routing (Dijkstra/A*)**
- [ ] **Phase 4: Baseline Signal Controllers (Fixed-Time, Adaptive, Max-Pressure)**
- [ ] **Phase 5: Emergency Green Corridors & Incident Injection**
- [ ] **Phase 6: Traffic Prediction (XGBoost)**
- [ ] **Phase 7: Reinforcement Learning (PPO in Gymnasium)**
- [ ] **Phase 8: PostgreSQL Persistence & Firebase RBAC**
- [ ] **Phase 9: Command Centre Dashboard (2D Map + ECharts + Logs)**
- [ ] **Phase 10: 3D Digital Twin Integration**
- [ ] **Phase 11: System Hardening, Benchmarking & Demo**
