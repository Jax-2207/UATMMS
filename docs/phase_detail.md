# UATMMS: Comprehensive Phase Implementation Guide

> **Universal Automatic Traffic Management and Manipulation System**  
> *Engineering Implementation Roadmap derived from `UATMMS_Complete_Project_Blueprint.pdf`*

---

## Executive Architecture & Core Loop

UATMMS coordinates multi-intersection urban traffic networks through a continuous closed loop:

$$\text{Observe} \longrightarrow \text{Predict} \longrightarrow \text{Optimize} \longrightarrow \text{Validate} \longrightarrow \text{Control} \longrightarrow \text{Monitor}$$

```
+---------------------------------------------------------------------------------------------------+
|                                      UATMMS MODULAR SYSTEM                                        |
+---------------------------------------------------------------------------------------------------+
|  [2D Map & Command Centre] <==== (REST & WebSockets) ====> [FastAPI Monolith Backend]             |
|                                                                     |                             |
|       +-------------------------------------------------------------+                             |
|       |                                                                                           |
|       v                                                                                           |
|  [Network Graph Model]  ===>  [Signal Controllers]  ===>  [Safety Validator]  ===> [TraCI Bridge] |
|   (NetworkX Dijkstra/A*)       (Fixed/Adaptive/Pressure)   (Hard Invariant Gate)   (SUMO Physics) |
+---------------------------------------------------------------------------------------------------+
```

---

## 12-Phase Master Implementation Roadmap

| Phase | Title | Key Objective | Status |
| :--- | :--- | :--- | :---: |
| **Phase 0** | **Project Setup & Skeleton** | Repository conventions, modular backend, Safety Validator, Web/Mobile UI skeletons, CI & tests | **COMPLETED** |
| **Phase 1** | **SUMO Proof of Concept** | TraCI Python adapter, live simulation stepping, vehicle/signal state polling | **COMPLETED** |
| **Phase 2** | **Multi-Intersection Network** | 6–12 junction OSM/SUMO network (.net.xml), edge ID mapping, realistic Indian traffic demand | **COMPLETED** |
| **Phase 3** | **Dynamic Graph Routing** | NetworkX directed graph, time-dependent dynamic edge costs ($C_e(t)$), Dijkstra & A*, 15% hysteresis | **COMPLETED** |
| **Phase 4** | **Baseline Signal Controllers** | Fixed-Time, Queue-Adaptive, and Max-Pressure network controllers with benchmark harness | **COMPLETED** |
| **Phase 5** | **Emergency Corridors & Incidents** | Multi-junction green corridor scheduler, conflicting emergency arbitration, obstacle injection | **NEXT UP** |
| **Phase 6** | **Traffic Prediction** | Short-term congestion & queue forecasting using Historical Baselines & XGBoost | Planned |

| **Phase 7** | **Reinforcement Learning Research** | Gymnasium environment wrapper, Stable-Baselines3 PPO, action masking, safe policy lifecycle | Planned |
| **Phase 8** | **Database & Authentication** | PostgreSQL relational schema + JSONB fields, Alembic migrations, Firebase token verification & RBAC | Planned |
| **Phase 9** | **Command Centre Dashboard** | Live Leaflet 2D map, Apache ECharts telemetry, WebSockets streaming, role-based controls | Planned |
| **Phase 10** | **3D Digital Twin Integration** | SUMO-to-Unity/Godot synchronization bridge for real-time microscopic 3D visualization | Planned |
| **Phase 11** | **Hardening, Benchmarking & Demo** | Multi-seed evaluation runs ($N \ge 5$), safety regression tests, documentation & demo walkthrough | Planned |

---

## Phase Details: What and How We Solve Each Phase

---

### Phase 0: Project Setup & Repository Skeleton
* **Status**: **COMPLETED**
* **Objective**: Establish development standards, error hierarchy, testing harness, modular FastAPI backend, deterministic Safety Validator, and web/mobile UI skeletons.

#### What Was Built:
- **Modular Monolith**: FastAPI app in `backend/app/` with clean domain boundaries (`api`, `auth`, `core`, `db`, `simulation`, `safety`, `routing`, `control`, `emergency`, `incidents`, `prediction`, `evaluation`, `schemas`).
- **Deterministic Safety Validator** (`backend/app/safety/validator.py`): Enforces minimum green ($G_{\min} = 10\text{s}$), maximum green ($G_{\max} = 90\text{s}$), clearance transitions, conflict matrices, and audit logging.
- **Authoritative Simulation Manager** (`backend/app/simulation/manager.py`): Lifecycle controls (`start`, `pause`, `resume`, `reset`, `step_forward`, `get_state`).
- **Web & Mobile Applications**:
  - `apps/web`: React 19 + TypeScript + Vite Command Centre with dark-mode glassmorphic interface and WebSocket client.
  - `apps/mobile`: 9-screen Android role-based application (Driver, Ambulance, Police) matching Figma specifications.
- **Specifications & ADRs**: `docs/architecture.md`, `docs/safety-policy.md`, `docs/experiment-protocol.md`, `docs/coding-conventions.md`.
- **Harness & Tooling**: `pytest.ini`, `scripts/run_simulation.py`, `scripts/evaluate_controllers.py`.

#### Definition of Done:
- All unit tests pass: `pytest` (7 passed in 1.08s).
- Direct CLI execution works: `python scripts/run_simulation.py --steps 10` (verified).

---

### Phase 1: SUMO Proof of Concept (TraCI Adapter)
* **Status**: **COMPLETED**
* **Objective**: Establish bidirectional Python-to-SUMO TraCI communication for vehicle/signal inspection and control.

#### What Was Built:
- **TraCI Adapter Class** (`backend/app/simulation/traci_adapter.py`):
  - Manages SUMO process lifecycle (`sumo` or `sumo-gui` via `traci.start(...)` and `traci.close()`).
  - Implements connection resilience, timeouts, and graceful shutdown.
  - Extracts microscopic state: vehicle IDs, coordinates, speeds, lane IDs, waiting times, and traffic light phases.
  - Applies approved phase changes via `traci.trafficlight.setPhase()`, strictly gated behind `SafetyValidator`.
- **Minimal Test Network** (`simulation/networks/poc_single_junction/`):
  - 1 signalized 4-way intersection `.net.xml` with defined detectors and phases.
  - Vehicle demand `.rou.xml` and configuration `.sumocfg`.
- **Integration with Simulation Manager**:
  - `backend/app/simulation/manager.py` switches between live TraCI and synthetic fallback automatically.
- **Verification**: `backend/tests/test_traci_adapter.py` passing 4/4 tests.

---

### Phase 2: Multi-Intersection Urban Network & Demand Generation
* **Status**: **COMPLETED**
* **Objective**: Build a realistic 6–12 intersection connected urban network reflecting Indian city road layouts (Bangalore MG Road corridor) with repeatable traffic demand.

#### What Needs to Be Built:
- **SUMO Network Definition** (`simulation/networks/bengaluru_core/`):
  - 6 to 12 interconnected signalized junctions (e.g., MG Road, Brigade Road, Residency Road, Church Street, Commercial Street, Lavelle Road).
  - OpenStreetMap (`.osm`) geometry cleaned via `netconvert` or manually curated in `netedit`.
  - Multi-lane configurations, turn pockets, and pedestrian crosswalks.
- **Indian Vehicle Mix & Demand Profiles** (`simulation/scenarios/`):
  - Vehicle types: Passenger cars (40%), two-wheelers/motorcycles (35%), auto-rickshaws (15%), buses/trucks (8%), emergency ambulances/fire (2%).
  - Driver behavior distributions: varied `accel`, `decel`, `minGap` (closer following distance), `emergencyDecel`, and `tau` (headway).
  - Scenarios:
    1. `off_peak.rou.xml` (500 veh/hr)
    2. `standard_demand.rou.xml` (1,500 veh/hr)
    3. `peak_rush.rou.xml` (3,000 veh/hr with bottleneck junctions)
- **SUMO-to-Backend ID Mapping Table** (`backend/app/network/mapping.py`):
  - Bi-directional lookup between human-readable IDs (`J1_MG_Road`), SUMO junction IDs (`cluster_10293`), and frontend graph IDs.

#### How We Are Going to Solve It:
1. Define network geometry using SUMO `.nod.xml`, `.edg.xml`, and `.con.xml` or OpenStreetMap export filtered for urban arterials.
2. Generate synthetic demand profiles using `randomTrips.py` or `duarouter` with calibrated vehicle emission probabilities.
3. Establish reproducible seeds ($seed \in \{42, 101, 777, 888, 999\}$) in scenario configuration files.

#### Definition of Done:
- SUMO loads `bengaluru_core.sumocfg` without errors or disconnected lane warnings.
- Simulation runs for 1,000 steps with stable vehicle flow and realistic congestion bottlenecks.

---

### Phase 3: Dynamic Graph Routing (Dijkstra, A* & Hysteresis)
* **Status**: **COMPLETED**
* **Objective**: Represent the connected road network as a directed weighted graph $G=(V, E)$, compute time-dependent routes using dynamic traffic costs, and eliminate route flapping via hysteresis.

#### What Was Built:
- **Road Graph Engine** (`backend/app/routing/graph.py`):
  - Directed graph wrapping NetworkX `DiGraph` synchronized with CBD network topology.
  - Automatically indexes junctions with coordinates $(x, y)$ for Euclidean heuristics and directed road linkages.
- **Dynamic Cost Function** (`backend/app/routing/cost_model.py`):
  $$C_e(t) = \text{travel\_time}_e(t) + \alpha \cdot \text{queue\_penalty}_e(t) + \beta \cdot \text{incident\_penalty}_e(t)$$
  - Returns $\infty$ ($10^9$) on severe incidents ($\ge 5$) or total road closures.
  - Applies 70% queue penalty discount for emergency vehicles (simulating priority clearance).
- **Route Planners** (`backend/app/routing/dijkstra.py`, `backend/app/routing/astar.py`):
  - Dijkstra baseline for exact shortest travel-time path.
  - A* with Euclidean distance heuristic ($h(n) = \frac{\text{dist}(n, \text{goal})}{v_{\max}}$) for fast calculation.
- **Dynamic Router & Rerouting Hysteresis** (`backend/app/routing/router.py`):
  - Prevents route oscillation by only switching if candidate route offers $> 15\%$ travel time improvement.
- **REST Endpoints** (`backend/app/api/endpoints/routing.py`):
  - `POST /api/v1/routes/plan`: computes optimal edge and junction sequence.
  - `POST /api/v1/routes/evaluate`: evaluates dynamic reroute recommendations with hysteresis.
- **Verification**: `backend/tests/test_routing.py` (7/7 tests passed).


---

### Phase 4: Baseline Signal Controllers & Benchmarking
* **Status**: **COMPLETED**
* **Objective**: Implement and fairly compare fixed-time, queue-based adaptive, and Max-Pressure network signal controllers under identical scenarios with zero safety violations.

#### What Was Built:
- **Base Controller Interface** (`backend/app/control/base.py`):
  - Abstract base class `BaseSignalController` with mandatory, non-bypassable `SafetyValidator` verification for all phase transitions.
  - Auto-registers observed junctions and tracks decision telemetry (requested, approved, rejected).
- **Fixed-Time Controller** (`backend/app/control/fixed_time.py`):
  - Webster 6-stage cycle: NS Green (30s) $\to$ NS Yellow (3s) $\to$ All-Red (2s) $\to$ EW Green (25s) $\to$ EW Yellow (3s) $\to$ All-Red (2s). Cycle length = 65s.
- **Queue-Based Adaptive Controller** (`backend/app/control/queue_adaptive.py`):
  - Dynamic green extension up to $G_{\max} = 90\text{s}$ and gap-out clearing of empty approaches down to $G_{\min} = 10\text{s}$.
- **Decentralized Max-Pressure Controller** (`backend/app/control/max_pressure.py`):
  - Computes phase pressure $P_{\text{phase}} = \sum q_{\text{in}} - \sum q_{\text{out}}$ (Varaiya 2013) to stabilize network queue differentials.
- **Signal Control Manager** (`backend/app/control/manager.py`):
  - Coordinates controller lifecycle, runtime switching, and telemetry aggregation.
- **Safety Validator Clearance Enhancement** (`backend/app/safety/validator.py`):
  - Enforces phase-appropriate constraints: minimum green (10s), yellow clearance (3s), and all-red clearance (2s).
- **Evaluation Benchmark Harness** (`scripts/evaluate_controllers.py`):
  - Multi-seed evaluation runs (`[42, 101, 777]`) measuring $W_{\text{avg}}$, throughput $Q$ (veh/h), queue lengths, and safety violations.
  - **Results**:
    - Fixed-Time: $W_{\text{avg}} = 17.43\text{s}$, Throughput = 27,240 veh/h, Violations = 0.
    - Queue-Adaptive: $W_{\text{avg}} = 10.82\text{s}$ (**37.9% wait reduction**), Throughput = 27,840 veh/h (**+2.2%**), Violations = 0.
    - Max-Pressure: $W_{\text{avg}} = 11.65\text{s}$ (**33.2% wait reduction**), Throughput = 27,828 veh/h (**+2.2%**), Violations = 0.
- **Verification**: `backend/tests/test_controllers.py` (5/5 tests passed).


---

### Phase 5: Emergency Green Corridors & Incident Management
* **Objective**: Build the dynamic emergency preemption scheduler with cross-traffic conflict handling and incident injection mechanics.

#### What Needs to Be Built:
- **Corridor Scheduler** (`backend/app/emergency/corridor_scheduler.py`):
  - Given emergency vehicle origin, destination, and urgency:
    1. Computes optimal route via dynamic graph routing.
    2. Calculates Estimated Time of Arrival ($\text{ETA}_j$) at each upcoming junction $j$ along the route:
       $$\text{ETA}_j = t_{\text{now}} + \sum_{e \in \text{path to } j} \frac{\text{length}_e}{v_e}$$
    3. Schedules prioritized green window $[ \text{ETA}_j - t_{\text{buffer}}, \text{ETA}_j + t_{\text{clear}} ]$.
- **Conflicting Emergency Arbitration** (`backend/app/emergency/arbitration.py`):
  - Resolves overlapping or perpendicular emergency requests using explicit priority rules:
    - Life-support Ambulance (Severity 1) $>$ Fire Engine (Severity 2) $>$ Police Transfer (Severity 3).
    - When two equal-urgency emergencies conflict: coordinates non-instant transitions rather than rapid phase flipping.
- **Incident Injection & Recovery Engine** (`backend/app/incidents/manager.py`):
  - Event types: `blocked_lane`, `accident`, `animal_crossing`, `rash_driving`, `signal_failure`.
  - Injects capacity reduction or lane blockages via TraCI (`traci.lane.setDisallowed()` or stopped dummy vehicle).
  - Triggers graph edge weight update $\rightarrow$ triggers dynamic rerouting $\rightarrow$ restores capacity upon incident resolution.

#### How We Are Going to Solve It:
1. Emergency corridor commands MUST pass through `SafetyValidator`. An emergency cannot force a sub-minimum green transition ($< 10\text{s}$) or skip yellow clearance ($3\text{s}$).
2. After emergency passage, controller smoothly restores signals to normal cycle without causing gridlock on cross streets.

#### Definition of Done:
- Test: Ambulance departs from J1 to J6 during rush hour. Green corridor clears ahead of the vehicle.
- Travel time of emergency vehicle is reduced by $\ge 30\%$ compared to baseline, with 0 red lights encountered and 0 safety breaches.
- Incident test: Obstacle injected on Brigade Road updates cost graph and automatically redirects subsequent vehicles.

---

### Phase 6: Traffic Prediction Engine (Historical Baselines & XGBoost)
* **Objective**: Forecast near-future congestion, queue lengths, and travel times across network edges for a 1–5 minute horizon.

#### What Needs to Be Built:
- **Dataset Feature Extractor** (`backend/app/prediction/dataset.py`):
  - Logs time-series snapshots of edge conditions: $[t, \text{edge\_id}, \text{speed}_{t-1}, \text{count}_{t-1}, \text{queue}_{t-1}, \text{occupancy}_{t-1}, \text{upstream\_flow}, \text{signal\_phase}]$.
- **Baseline Predictors** (`backend/app/prediction/baselines.py`):
  - Current-state persistence ($\hat{y}_{t+k} = y_t$).
  - Historical time-of-day moving averages.
- **XGBoost Forecasting Model** (`backend/app/prediction/model.py`):
  - Gradient-boosted regression trees trained to predict:
    1. Continuous travel time $\hat{T}_e(t + \Delta t)$.
    2. Queue length $\hat{L}_e(t + \Delta t)$.
    3. Categorical congestion severity (Free-Flow, Moderate, Congested, Gridlock).
- **Inference Integration**:
  - Serves predictions to routing engine so dynamic routing can avoid *upcoming* congestion rather than merely *existing* congestion.

#### How We Are Going to Solve It:
1. Generate training data across 20 simulation runs with randomized demand profiles.
2. Strict train/test separation by scenario seed to prevent data leakage.
3. Evaluate using Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE).

#### Definition of Done:
- XGBoost model trained and saved to `backend/app/prediction/checkpoints/`.
- Predictions evaluated against persistence baseline; XGBoost achieves measurable MAE reduction on held-out test scenarios.

---

### Phase 7: Reinforcement Learning Research Branch (Gymnasium + SB3 PPO)
* **Objective**: Implement a Gymnasium-compatible SUMO environment and train a Proximal Policy Optimization (PPO) agent for adaptive traffic signal control.

#### What Needs to Be Built:
- **Gymnasium Environment Wrapper** (`rl/env/sumo_traffic_env.py`):
  - Implements `gymnasium.Env` (`reset()`, `step()`, `observation_space`, `action_space`).
  - **Observation Space**: Box vector containing local queue lengths, approaching vehicle speeds, waiting times, current phase index, elapsed phase duration, and downstream free capacity.
  - **Action Space**: Discrete choice of permitted signal phases or green extension steps. Action masking prevents illegal transitions.
- **Reward Function Design** (`rl/env/reward.py`):
  $$R_t = - w_1 \sum \text{waiting\_time} - w_2 \sum \text{queue\_length} + w_3 \cdot \text{throughput} - w_4 \cdot \text{emergency\_delay}$$
- **Training Pipeline** (`rl/training/train_ppo.py`):
  - Stable-Baselines3 `PPO` with PyTorch backend.
  - Multi-layer perceptron policy network (`MlpPolicy`).
  - TensorBoard logging for policy loss, value loss, and episode reward.
- **Safe Policy Promotion & Rollback**:
  - RL policy outputs candidate actions $\rightarrow$ strictly filtered through `SafetyValidator`.
  - Checkpoints promoted only if they outperform Max-Pressure on unseen evaluation seeds.

#### How We Are Going to Solve It:
1. Start with single-intersection environment (`J1_MG_Road`) to stabilize hyperparameters (learning rate, entropy coefficient, clip range).
2. Expand to multi-intersection shared policy.
3. Fallback mechanism: if RL policy generates an invalid action, the safety validator blocks it and maintains safe deterministic timing.

#### Definition of Done:
- PPO agent trains stably for 100,000 steps without exploding loss.
- Evaluated on 5 unseen seeds against Fixed-Time and Max-Pressure; results documented in `rl/evaluations/benchmark_report.md`.

---

### Phase 8: Database Persistence & Firebase Authentication (RBAC)
* **Objective**: Implement persistent PostgreSQL storage for relational entities and audit logs, with Firebase token verification and strict server-side RBAC.

#### What Needs to Be Built:
- **PostgreSQL Database Models** (`backend/app/db/models.py` via SQLAlchemy):
  - `users`, `roles`, `user_roles`, `simulation_runs`, `incidents`, `emergency_requests`, `routes`, `signal_events`, `metric_snapshots`, `audit_events`.
  - JSONB columns for flexible data: `incident_config`, `edge_sequence`, `algorithm_hyperparameters`.
- **Alembic Migrations** (`backend/app/db/alembic/`):
  - Version-controlled schema migrations.
  - SQLite fallback for zero-dependency local development.
- **Authentication & RBAC Middleware** (`backend/app/auth/rbac.py`):
  - Firebase Admin SDK verification of client-provided Bearer ID tokens.
  - Role-Permission Matrix:
    - `admin`: system configuration, user provisioning, audit inspection.
    - `operator`: simulation control, signal inspection, plan approval.
    - `police`: incident verification, road closure confirmation.
    - `ambulance` / `fire`: emergency corridor requests.
    - `public`: read-only routes and traffic alerts.
  - All protected endpoints check permissions server-side.

#### How We Are Going to Solve It:
1. Provide mock authentication mode (`MOCK_AUTH_FOR_DEV=True`) with pre-seeded role tokens for testing.
2. When connected to real Firebase, verify JWT signatures, extract UID, and load application roles from PostgreSQL.
3. Automatically log all privileged actions (signal changes, emergency dispatch, incident reporting) into `audit_events`.

#### Definition of Done:
- Integration tests verify role enforcement: unauthorized users cannot trigger emergency corridors or force signal changes.
- Alembic migration `001_initial_schema.py` applies cleanly to both SQLite and PostgreSQL.

---

### Phase 9: Command Centre Dashboard Integration
* **Objective**: Build the full-featured, responsive Command Centre web application synchronizing live SUMO simulation state, interactive 2D map, ECharts analytics, and role workflows.

#### What Needs to Be Built:
- **Interactive 2D Map** (`apps/web/src/components/Map/`):
  - Leaflet / OpenStreetMap component rendering road edges, signalized junctions, vehicle positions, active emergency corridors, and incident markers.
- **Live Telemetry & ECharts** (`apps/web/src/components/Analytics/`):
  - Real-time charts showing vehicle throughput, average speed, waiting time, and queue length over time.
  - Controller comparison view displaying baseline vs adaptive metrics.
- **Role-Based Control Workspaces**:
  - Operator view (simulation controls, manual overrides, logs).
  - Emergency Dispatcher view (dispatch ambulance, track corridor ETA, view signal status).
  - Police view (report/verify incidents, toggle road closures).
- **WebSocket Streaming Manager**:
  - Robust client hook with auto-reconnection and sequence-number tracking to ignore out-of-order packets.

#### How We Are Going to Solve It:
1. Connect frontend React components directly to `/ws/simulation` stream.
2. Render SUMO vehicle positions on 2D map with smooth CSS/canvas interpolation.
3. Integrate Safety Validator rejection alerts into the side notification drawer.

#### Definition of Done:
- End-to-end browser walkthrough: starting simulation in web UI streams vehicle motion and updates ECharts metrics in real-time.
- Dispatching emergency in UI visualizes green corridor path on map and triggers signal transitions.

---

### Phase 10: 3D Digital Twin Integration
* **Objective**: Synchronize an interactive 3D digital twin (Unity / Godot / Three.js) with authoritative SUMO simulation state.

#### What Needs to Be Built:
- **3D Bridge Protocol** (`visualization/bridge/`):
  - Lightweight WebSocket or UDP state publisher streaming vehicle coordinates $(x, y, z)$, heading angle, velocity, vehicle model type, and traffic light colors.
- **3D Scene Environment** (`visualization/unity-or-godot/`):
  - 3D road models, signal light meshes (Green/Yellow/Red emissive materials), and vehicle 3D assets (cars, auto-rickshaws, buses, ambulances with flashing sirens).
- **Interpolation Engine**:
  - Smooth client-side dead reckoning / positional interpolation between 1.0s simulation ticks to ensure 60 FPS rendering.

#### How We Are Going to Solve It:
1. Enforce **Single Source of Truth**: 3D client is purely a viewer; it NEVER computes its own traffic physics or feeds telemetry back to the controller.
2. If 3D client lags or disconnects, backend simulation and 2D command centre continue without disruption.

#### Definition of Done:
- 3D scene mirrors SUMO vehicle movements and signal states accurately across pause, step, and reset operations.

---

### Phase 11: System Hardening, Benchmarking & Demo Script
* **Objective**: Rigorous stress testing, comprehensive safety validation, benchmark report generation, and polished demonstration scripting.

#### What Needs to Be Built:
- **Adversarial Safety Test Suite** (`backend/tests/test_adversarial_safety.py`):
  - Simultaneous conflicting emergency corridor requests.
  - Rapid controller flapping requests (sub-minimum green attempts).
  - TraCI disconnection and stale-state fail-safe activation.
  - Invalid phase requests and out-of-bounds inputs.
- **Final Controller Benchmark Report** (`docs/benchmark_report.md`):
  - Complete evaluation across Fixed-Time, Queue-Adaptive, Max-Pressure, and PPO RL.
  - Documented mean $\pm$ standard deviation across 5 evaluation seeds.
- **Demo Script & Video Walkthrough** (`docs/demo_guide.md`):
  - Step-by-step walkthrough script for live presentation:
    1. Normal rush-hour traffic baseline.
    2. Incident injection (fallen tree on arterial road) $\rightarrow$ dynamic graph rerouting.
    3. Cardiac emergency ambulance dispatch $\rightarrow$ green corridor preemption $\rightarrow$ safe recovery.
    4. Safety Validator blocking an unsafe phase switch live on dashboard.
    5. Mobile app driver alert synchronization.

#### Definition of Done:
- Zero critical safety bugs in entire test suite (`pytest` passing 100%).
- Full end-to-end demo script executed successfully without crashes.
- All documentation, ADRs, and limitation disclosures fully aligned with the Blueprint.

---

## Safety & Governance Invariants Summary

Every phase must strictly adhere to the non-negotiable rules defined in `docs/safety-policy.md`:

```
+-------------------------------------------------------------------------------+
|                      SAFETY VALIDATOR HARD INVARIANTS                         |
+-------------------------------------------------------------------------------+
| 1. Minimum Green:       Must remain green for >= 10.0s before any transition  |
| 2. Maximum Green:       Must not starve cross-streets longer than 90.0s       |
| 3. Clearance Phases:    Must transition through >= 3s Yellow and >= 2s All-Red|
| 4. Conflict Matrix:     Never green concurrently for intersecting movements   |
| 5. Deterministic Hold:  On error, timeout or disconnect, revert to safe hold  |
| 6. Audit Trail:         Every single request & verdict logged in audit_events |
+-------------------------------------------------------------------------------+
```

---

*This document is the authoritative phase reference for UATMMS engineering execution.*
