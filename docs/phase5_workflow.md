# Phase 5: Workflows & Standard Operating Procedures

## Emergency Dispatch Workflow

### Actor: Ambulance Dispatcher

**Scenario:** Cardiac patient at location A, transport to Hospital H (10 km, ~25-40 min normal traffic)

### Step 1: Create Emergency Request

```bash
curl -X POST http://localhost:8000/api/v1/emergencies \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "AMB_CARDIAC_001",
    "origin_junction": "J1_Residence",
    "destination_junction": "J15_Hospital",
    "vehicle_type": "ambulance",
    "severity": 1,  # CRITICAL
    "requester_id": "DISPATCHER_42",
    "metadata": {
      "patient": "Cardiac Case",
      "priority": "Critical",
      "hospital_code": "HOSP_001"
    }
  }'
```

**Response (Immediate):**
```json
{
  "request_id": "EMG_20261022_001",
  "vehicle_id": "AMB_CARDIAC_001",
  "status": "corridor_active",
  "corridor_plan": {
    "request_id": "EMG_20261022_001",
    "route_junctions": ["J1", "J2", "J4", "J7", "J9", "J12", "J15"],
    "corridor_windows": [
      {
        "junction_id": "J1",
        "green_window_start_s": 5.0,
        "green_window_end_s": 25.0,
        "estimated_arrival_s": 12.0,
        "priority": 1
      },
      {
        "junction_id": "J2",
        "green_window_start_s": 18.0,
        "green_window_end_s": 40.0,
        "estimated_arrival_s": 25.0,
        "priority": 1
      }
      // ... more windows
    ],
    "total_estimated_travel_time_s": 420.0  # 7 minutes instead of 25-40 min!
  },
  "created_at": "2026-10-22T20:45:00Z",
  "message": "Corridor ACTIVE. Signal preemption enabled along planned route."
}
```

### Step 2: Monitor Corridor Status

**Dispatcher Poll Interval:** Every 5 seconds

```bash
curl http://localhost:8000/api/v1/emergencies/EMG_20261022_001 \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Expected Response (Ongoing):**
```json
{
  "request_id": "EMG_20261022_001",
  "vehicle_id": "AMB_CARDIAC_001",
  "status": "corridor_active",
  "corridor_plan": { ... },
  "created_at": "2026-10-22T20:45:00Z",
  "message": "Vehicle in transit. Corridor active at J1-J4."
}
```

### Step 3: Vehicle Navigation (Mobile App)

**Driver sees on screen:**
- Green corridor path highlighted on map
- Next signal status: GREEN (preempted)
- ETA to hospital: 7m 15s
- Red signals encountered: 0

### Step 4: Completion Report (Sent by Driver/Hospital)

```bash
curl -X POST http://localhost:8000/api/v1/emergencies/EMG_20261022_001/complete \
  -H "Authorization: Bearer $DRIVER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "EMG_20261022_001",
    "vehicle_id": "AMB_CARDIAC_001",
    "actual_travel_time_s": 425.0,
    "red_signals_encountered": 0,
    "route_edges_traversed": ["edge_1", "edge_2", "edge_4", "edge_7", ...],
    "safety_violations": 0,
    "completion_status": "success",
    "notes": "Stable patient, arrived at hospital trauma bay."
  }'
```

**Response:**
```json
{
  "status": "completed",
  "request_id": "EMG_20261022_001",
  "metrics": {
    "travel_time_s": 425.0,
    "red_signals": 0,
    "safety_violations": 0
  }
}
```

### Step 5: Analytics Dashboard

**Dispatcher Review:**
- Emergency ID: EMG_20261022_001
- Vehicle: AMB_CARDIAC_001
- Duration: 7m 5s (vs. 25-40m normal) — **71% reduction** ✅
- Red signals: 0 ✅
- Safety violations: 0 ✅
- Status: Success

---

## Overlapping Emergencies Workflow

### Scenario: Two Simultaneous Emergencies

**Time 0s:**
- 🚑 Ambulance (CRITICAL) requests corridor: J1 → J10
- 🚒 Fire (HIGH) requests corridor: J1 → J12 (overlaps at J1, J2)

### Arbitration Flow

```
1. System detects conflict:
   - Shared junctions: {J1, J2}
   - Time overlap: 10-25s at J1

2. Apply priority rules:
   - Ambulance: Severity 1 (CRITICAL) — WINS
   - Fire: Severity 2 (HIGH) — SECONDARY

3. Arbitration decision:
   - Ambulance: Corridor unchanged (10-25s at J1)
   - Fire: Staggered +15s (25-40s at J1)

4. Validate through SafetyValidator:
   - Ambulance J1 green: 10-25s ✅ (safe)
   - Fire J1 green: 25-40s ✅ (no conflict)
   - Both approved

5. Return to requesters:
   - Ambulance: "Corridor approved, proceed immediately"
   - Fire: "Corridor approved, slight 15s delay applied"
```

**Result:**
- Ambulance: 7m travel time
- Fire: 8m travel time (1m delay vs. normal ~20m) — still **60% reduction** ✅

---

## Incident Management Workflow

### Scenario: Debris on Main Arterial Road

### Step 1: Incident Detection (Automated or Manual Report)

**Option A: Automated Detection (Camera/Sensor)**
```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "debris",
    "severity": 3,  # Moderate impact
    "location_edge_id": "edge_MG_Road_Segment_42",
    "capacity_reduction_pct": 30.0,
    "source": "detector",
    "confidence": 0.75  # Moderate confidence
  }'
```

**Response:**
```json
{
  "incident_id": "INC_20261022_001",
  "status": "unverified",  # Requires verification (confidence < 0.8)
  "message": "Incident reported. Awaiting police verification."
}
```

### Step 2: Police Verification

**Police Officer receives alert on mobile app:**
- Incident: "Debris on MG Road"
- Location: edge_MG_Road_Segment_42
- Confidence: 75%
- **ACTION REQUIRED:** Verify incident

```bash
curl -X POST http://localhost:8000/api/v1/incidents/INC_20261022_001/verify \
  -H "Authorization: Bearer $POLICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC_20261022_001",
    "verifier_id": "POLICE_OFFICER_99"
  }'
```

**Response:**
```json
{
  "incident_id": "INC_20261022_001",
  "status": "active",
  "message": "Incident verified and activated. Rerouting in progress."
}
```

### Step 3: System Updates Traffic Model

**Automatic Actions:**
1. ✅ Edge cost updated to $\infty$ (30% reduction = road less attractive)
2. ✅ Incident flag set on edge
3. ✅ Rerouting triggered for affected vehicles
4. ✅ Dashboard updated with incident marker

### Step 4: Traffic Reroutes Around Incident

**Example: Vehicle V1 approaching MG Road**
- Current path: "A → MG_Road_42 → B" (10 min)
- After incident: "A → Alternate_Route_C → B" (12 min, +2 min)
- **Trigger:** Incident cost update causes A* to find new shortest path

### Step 5: Incident Resolution

**Police Clear Road**
```bash
curl -X PUT http://localhost:8000/api/v1/incidents/INC_20261022_001/status \
  -H "Authorization: Bearer $POLICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC_20261022_001",
    "new_status": "resolved",
    "notes": "Debris removed, road clear."
  }'
```

**Response:**
```json
{
  "incident_id": "INC_20261022_001",
  "status": "resolved",
  "duration_s": 300.0,  # 5 minutes from start to resolution
  "message": "Incident cleared. Normal traffic resumed."
}
```

### Step 6: System Restores Normal Routes

**Automatic Actions:**
1. ✅ Edge cost restored to normal
2. ✅ Incident flag cleared
3. ✅ Subsequent vehicle routes optimize back to MG Road
4. ✅ Metrics logged to analytics

---

## Safety Violation Scenario & Recovery

### Scenario: Safety Validator Rejects Emergency Preemption

**Situation:**
- Ambulance requests green at J5 at time t=50s
- J5 is currently in Green (N-S) phase, started at t=42s
- Min green = 10s (still 2 seconds remaining)
- Safety validator rejects preemption: "Min green not elapsed"

### Actions:

**System:**
```
1. SafetyValidator.validate_phase_transition(..., is_emergency=True)
   → Returns (False, "Min green not elapsed (2s remaining)")

2. Log rejection: [SAFETY REJECTION] EMG_001 at J5: Min green violation

3. Hold current phase (N-S Green)

4. Alert dashboard: "Emergency J5 preemption blocked by safety"

5. Notify ambulance: "Slight delay at intersection. Will proceed with next green."
```

**Ambulance Experience:**
- Encounters RED light at J5 (but short wait)
- After 2s: N-S Green completes, Yellow phase begins
- After 5s total: New green available (E-W) not available for ambulance
- **Outcome:** Ambulance delayed ~5-10 seconds, but intersection safety maintained ✅

### Audit Log Entry:

```json
{
  "timestamp": "2026-10-22T20:50:35.123Z",
  "junction_id": "J5",
  "event_type": "safety_rejection",
  "request_id": "EMG_001",
  "target_phase": 1,
  "current_phase": 0,
  "phase_elapsed_s": 8.2,
  "min_required_s": 10.0,
  "reason": "Minimum green time not elapsed",
  "is_emergency": true,
  "outcome": "Preemption denied, safe phase held"
}
```

---

## Concurrent Workflow: Fire Response During Incident

### Timeline:

```
T=0s    : Debris incident on MG Road (edge_42)
T=15s   : Incident verified by police, routing updated
T=45s   : Fire alarm at location X, fire truck dispatched
T=50s   : Fire corridor request: X → Incident Site (MG Road area)

          System detects:
          - Fire needs to reach MG Road (which has debris)
          - Corridor passes through affected area

          Decision:
          - Incident still active → high edge cost
          - Fire severity (HIGH) still preempts normal traffic
          - BUT: Edge debris may delay arrival
          - Alternative routes available (bypass debris area)

T=55s   : Fire corridor activated via alternate route (bypasses debris)
T=60s   : Debris cleared by police
T=65s   : Fire arrives at scene
```

**Outcome:**
- Fire arrival: 15 minutes from dispatch (vs. 20-25 min normal) ✅
- Corridor maintained despite concurrent incident ✅
- System adapts to real-time changes ✅

---

## Operator Override Workflow (Manual Control)

### Scenario: Operator Manually Resolves Ambiguous Incident

**Dashboard Operator sees:**
- Incident reported: "Blocked lane"
- Confidence: 45% (LOW)
- Status: "Unverified" (waiting for manual confirmation)

### Option 1: Confirm as Real

```bash
curl -X POST http://localhost:8000/api/v1/incidents/INC_001/verify \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -d '{"incident_id": "INC_001", "verifier_id": "OP_123"}'
```

→ Incident activated, routes redirected

### Option 2: Dismiss as False Alarm

```bash
curl -X PUT http://localhost:8000/api/v1/incidents/INC_001/status \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -d '{"incident_id": "INC_001", "new_status": "false_alarm"}'
```

→ Incident cleared, no rerouting, normal traffic continues

---

**Phase 5 Standard Operating Procedures  
Last Updated:** October 22, 2026  
**Status:** ✅ Implemented & QA Tested
