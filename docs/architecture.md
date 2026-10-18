# UATMMS Architecture Decisions Record (ADR)

## 1. System Vision & Architecture Style
UATMMS (Universal Automatic Traffic Management and Manipulation System) is architected as an **event-driven modular monolith** in Python (FastAPI) paired with a responsive single-page web application (React + Vite + TypeScript).

```
                      +---------------------------------------+
                      | React + Vite Command Centre Dashboard |
                      |   (2D Leaflet, ECharts, 3D Canvas)    |
                      +-------------------+-------------------+
                                          | REST / WebSockets
                                          v
                      +---------------------------------------+
                      |         FastAPI Modular Monolith      |
                      |   - Auth / RBAC (Firebase / Server)   |
                      |   - Route Planner (NetworkX A*)       |
                      |   - Safety Validator (Hard Gate)      |
                      |   - Corridor Scheduler & Incidents    |
                      |   - Signal Controllers (Baselines/RL) |
                      +-------------------+-------------------+
                                          | TraCI / libsumo
                                          v
                      +---------------------------------------+
                      |         SUMO Traffic Simulator        |
                      |  - Microscopic vehicle physics        |
                      |  - Authoritative signal & road state  |
                      +---------------------------------------+
```

## 2. Key Architectural Decisions (Locked)

### ADR-01: Modular Monolith vs Microservices
* **Decision**: Implement all backend domain modules in a single FastAPI application with explicit module boundaries.
* **Rationale**: Microservices introduce distributed transaction complexity, network overhead, and container orchestration overhead (Kafka/k8s) that are unnecessary at this phase. Python modular monolith provides direct in-memory calls between TraCI state and routing/controllers.
* **Boundary Rules**:
  * `simulation`: Only module permitted to directly invoke TraCI or mutate SUMO state.
  * `safety`: Independent validation gate; controllers NEVER send raw commands directly to `simulation` without passing through `safety`.
  * `routing`: Operates on static and dynamic graph representations from `network`, without coupling to UI.

### ADR-02: Single Source of Truth
* **Decision**: SUMO is the sole source of truth for physical vehicle positions, speeds, queues, and signal states.
* **Rationale**: The 2D map (Leaflet) and 3D digital twin (Unity/Godot or Three.js) are view layers. They must interpolate or mirror state, never invent physics or send synthetic telemetry back into the traffic controller.

### ADR-03: Safety Validator as a Hard Gate
* **Decision**: Signal decisions (from adaptive algorithms, Max-Pressure, or Reinforcement Learning policies) pass through a deterministic safety validator.
* **Rationale**: AI/RL cannot be trusted with raw signal manipulation. Minimum greens, yellow intervals, pedestrian clearance, and non-conflicting green phases are enforced via hard rules, not penalty functions.

### ADR-04: Storage Architecture
* **Decision**: PostgreSQL with relational tables for structured records (users, roles, simulation runs, incidents, emergency requests, signal events) and `JSONB` columns for variable-schema payload data (graph metadata, scenario definitions, algorithm hyperparameters).
* **Local Fallback**: SQLite fallback enabled for developer convenience when PostgreSQL is not running locally.

### ADR-05: Authentication & Role-Based Access Control (RBAC)
* **Decision**: Firebase Authentication handles identity (Google Sign-In), but roles (`admin`, `operator`, `police`, `ambulance`, `fire`, `hospital`, `public`) are stored server-side and checked on every protected endpoint and WebSocket channel.
* **Rationale**: Client-supplied role claims are never trusted. Privileged operations (e.g. emergency preemption, incident lane closures) require verified permissions.

### ADR-06: Communication Protocols
* **Decision**: HTTP REST for control commands, scenario lifecycle, and queries; WebSockets (`/ws/simulation`) for streaming real-time simulation snapshots (vehicles, signal phases, active emergencies, active alerts) to web clients.
