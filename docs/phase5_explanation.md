# Phase 5: Emergency Green Corridors & Incident Management

**Status:** ✅ IMPLEMENTED & TESTED

## Overview

Phase 5 implements the emergency preemption system for UATMMS, enabling safe, coordinated green corridors for emergency vehicles (ambulances, fire trucks, police) while handling traffic incidents and obstacles.

### Key Components

1. **Emergency Corridor Scheduler** — Calculates green-time windows at each junction
2. **Emergency Arbitration Engine** — Resolves conflicts between overlapping corridors
3. **Incident Manager** — Tracks incidents, updates edge costs, triggers rerouting
4. **Safety Validator Extension** — Enforces hard constraints on emergency preemption
5. **REST API Endpoints** — Exposes emergency and incident workflows

---

## Architecture

### Emergency Request Lifecycle

```
Request Submitted
    ↓
Route Planning (Dynamic Graph)
    ↓
Corridor Scheduling (ETA Calculation)
    ↓
Conflict Arbitration (Priority Rules)
    ↓
Safety Validation (Hard Constraints)
    ↓
Corridor Activation (Signal Control)
    ↓
Completion & Metrics
```

### Component Responsibilities

#### Corridor Scheduler (`backend/app/emergency/corridor_scheduler.py`)

**Purpose:** Compute green-time windows for emergency vehicle passage

**Key Functions:**
- `schedule_corridor()` — Plans route and calculates timing windows
- `_estimate_travel_time()` — Uses dynamic cost model to predict route duration
- `_generate_corridor_windows()` — Creates green window specification for each junction

**Algorithm:**
1. Get route from origin to destination using dynamic routing
2. Calculate estimated arrival time (ETA) at each junction
3. Create green window: `[ETA - buffer, ETA + clearance]`
4. Ensure minimum window duration (15s default)
5. Priority assigned based on severity level

**Example Output:**
```python
EmergencyCorridorPlan(
    request_id="EMG001",
    vehicle_id="AMB001",
    route_edges=["edge_1", "edge_2", "edge_3"],
    corridor_windows=[
        CorridorWindow(
            junction_id="J1",
            green_window_start_s=10.0,
            green_window_end_s=25.0,
            estimated_arrival_s=15.0,
            priority=1  # CRITICAL
        ),
        # ... more windows
    ],
    total_estimated_travel_time_s=45.0
)
```

#### Emergency Arbitration (`backend/app/emergency/arbitration.py`)

**Purpose:** Resolve conflicts when multiple emergencies request overlapping corridors

**Conflict Detection:**
- Identifies shared junctions between corridor plans
- Detects time overlaps at common junctions

**Resolution Strategy:**
1. **By Severity:** CRITICAL (1) > HIGH (2) > MEDIUM (3)
2. **By FIFO:** For equal severity, earliest request wins
3. **By Staggering:** Lower-priority corridors delayed by ~15s intervals

**Example Conflict Resolution:**
```
Request 1: Ambulance (CRITICAL) at J1, 10-25s  ← Keeps original time
Request 2: Police (MEDIUM) at J1, 10-25s       ← Staggered to 25-40s
```

#### Incident Manager (`backend/app/incidents/manager.py`)

**Purpose:** Track incidents, update traffic costs, trigger rerouting

**Lifecycle:**
```
DETECTED → UNVERIFIED (if low confidence)
   ↓
VERIFIED / ACTIVE (capacity reduced, cost increased)
   ↓
RECOVERY (being cleared)
   ↓
RESOLVED (back to normal)
```

**Actions on Incident Activation:**
1. Update edge cost in dynamic cost model (infinite cost for closures)
2. Mark edge with incident severity flag
3. Trigger rerouting for affected vehicles
4. Log incident to audit trail

**Actions on Incident Resolution:**
1. Restore normal edge capacity
2. Clear incident flag
3. Allow rerouting back to normal paths

#### Safety Validator Extension (`backend/app/safety/validator.py`)

**Emergency-Specific Rules:**
- Emergency preemption cannot skip yellow/all-red transitions (safety non-negotiable)
- Minimum green still applies (only shortens max-green earlier)
- Hard gate on conflicting movements

---

## Data Models

### EmergencyRequest Schema
```python
{
    "vehicle_id": "AMB001",
    "origin_junction": "J1",
    "destination_junction": "J6",
    "vehicle_type": "ambulance",  # ambulance, fire, police
    "severity": 1,  # 1=CRITICAL, 2=HIGH, 3=MEDIUM
    "requester_id": "USER123"
}
```

### IncidentCreate Schema
```python
{
    "incident_type": "blocked_lane",  # blocked_lane, accident, animal_crossing, etc.
    "severity": 4,  # 1-5
    "location_edge_id": "edge_42",
    "capacity_reduction_pct": 50.0,  # 0-100%
    "confidence": 0.95,  # 0.0-1.0
    "source": "detector"  # detector, user_report, police
}
```

---

## API Endpoints

### Emergency Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/emergencies` | Create emergency request |
| `GET` | `/api/v1/emergencies/{request_id}` | Get emergency status |
| `PUT` | `/api/v1/emergencies/{request_id}/status` | Update progress |
| `POST` | `/api/v1/emergencies/{request_id}/complete` | Mark completed |
| `GET` | `/api/v1/emergencies/active/corridors` | Get active corridors |
| `GET` | `/api/v1/emergencies/stats` | Get statistics |

### Incident Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/incidents` | Report incident |
| `GET` | `/api/v1/incidents/{incident_id}` | Get incident details |
| `POST` | `/api/v1/incidents/{incident_id}/verify` | Verify incident |
| `PUT` | `/api/v1/incidents/{incident_id}/status` | Update status |
| `GET` | `/api/v1/incidents/active` | Get active incidents |
| `GET` | `/api/v1/incidents/history` | Get history |

---

## Testing

### Test Coverage

**Unit Tests** (37/37 passing):
- Emergency corridor scheduling and timing
- Emergency request validation and lifecycle
- Conflict detection and arbitration
- Incident creation, verification, and resolution
- Incident querying and statistics

### Key Test Scenarios

1. **Single Ambulance Corridor:**
   - Request → Route Planning → Corridor Scheduled → Activated → Completed
   - Verify 30%+ travel time reduction vs baseline

2. **Conflicting Emergencies:**
   - Two emergencies request overlapping corridors
   - Lower-priority corridor staggered in time
   - Both execute safely without signal flipping

3. **Incident + Rerouting:**
   - Obstacle injected on main road
   - Edge cost updated → routes recalculated
   - Affected vehicles automatically redirected
   - Incident cleared → routes restore

4. **Safety Violations:**
   - Attempt to preempt before minimum green elapsed
   - Attempt to skip yellow/all-red clearance
   - Safety validator rejects, maintains safe phase

---

## Success Metrics

### Quantitative Targets

- **Emergency Travel Time Reduction:** ≥30% vs. baseline (without preemption)
- **Red Signals Encountered:** 0 in optimal corridor
- **Safety Violations:** 0 across all test scenarios
- **Conflict Resolution Time:** <1s for arbitration
- **Incident Response Latency:** <2s from detection to cost update

### Qualitative Validation

- ✅ Multi-junction ambulance transit executes safely
- ✅ Overlapping emergencies arbitrated without collision
- ✅ Incident injection correctly updates routing
- ✅ Incident resolution restores normal traffic patterns
- ✅ Zero false positives in safety gate
- ✅ All audit events logged correctly

---

## Known Limitations & Future Work

### Current Limitations

1. **Route Calculation:** Uses junction IDs (not full SUMO edge IDs in tests)
2. **Junctions per Route:** Estimated based on route length (not from graph traversal)
3. **Incident Capacity Models:** Simple binary closed/reduced (not graduated)
4. **Multi-Agent Coordination:** Single arbitrator (not distributed)

### Future Enhancements

1. **Real-Time Rerouting:** Active vehicles dynamically rerouted mid-trip
2. **Machine Learning Prediction:** Predict incident duration for proactive recovery
3. **Multi-Priority Scheduling:** Support sub-categories (e.g., pediatric vs. trauma)
4. **Hardware Integration:** Real traffic signal API integration (Phase future)
5. **Camera Incident Detection:** Automated incident detection via computer vision

---

## Usage Examples

### Create Emergency Request

```bash
curl -X POST http://localhost:8000/api/v1/emergencies \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "AMB001",
    "origin_junction": "J1",
    "destination_junction": "J6",
    "vehicle_type": "ambulance",
    "severity": 1,
    "requester_id": "USER123"
  }'
```

**Response:**
```json
{
  "request_id": "EMG001",
  "vehicle_id": "AMB001",
  "status": "corridor_active",
  "corridor_plan": {
    "route_junctions": ["J1", "J2", "J3", "J4", "J5", "J6"],
    "corridor_windows": [ ... ],
    "total_estimated_travel_time_s": 45.0
  }
}
```

### Report Incident

```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "blocked_lane",
    "severity": 4,
    "location_edge_id": "edge_42",
    "capacity_reduction_pct": 50.0,
    "confidence": 0.9,
    "source": "detector"
  }'
```

---

## Integration with Other Phases

- **Phase 3 (Routing):** Uses dynamic graph and cost model for route planning
- **Phase 4 (Controllers):** Preemption takes precedence over baseline control
- **Phase 6 (Prediction):** Predictions used in rerouting recommendations
- **Phase 8 (Database):** Stores emergency and incident audit trails
- **Phase 9 (Dashboard):** Visualizes active corridors and incidents

---

**Architecture Maintainers:** UATMMS Team  
**Last Updated:** October 22, 2026  
**QA Status:** ✅ All tests passing (37/37)
