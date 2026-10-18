# UATMMS Safety Policy & Validator Specification

## 1. Principles
Safety is a deterministic guarantee, not an optimization objective or reinforcement learning penalty. No optimization algorithm, RL agent, or emergency preemption request is allowed to bypass the **Safety Validator**.

## 2. Hard Invariants & Constraints

### 2.1 Conflicting Phase Prevention
* Green signals must **never** be concurrently displayed to conflicting vehicle movements or conflicting pedestrian crosswalks.
* Every junction maintains a validated conflict matrix. Any proposed phase configuration violating the conflict matrix is instantly rejected.

### 2.2 Minimum & Maximum Green Times
* **Minimum Green ($G_{\min}$)**: Every phase, once activated, must stay green for at least $G_{\min}$ seconds (default: 10s for major roads, 7s for minor roads). An emergency corridor preemption cannot truncate a phase before $G_{\min}$ has elapsed.
* **Maximum Green ($G_{\max}$)**: No non-emergency phase may remain green longer than $G_{\max}$ (default: 90s) to prevent starvation on cross streets.

### 2.3 Safe Clearance Transitions (Yellow & All-Red)
* Direct transitions from Green on Movement A to Green on conflicting Movement B are strictly prohibited.
* Every change of right-of-way must step through:
  1. Yellow interval ($T_{\text{yellow}} \ge 3$–$5\text{s}$ depending on speed limit).
  2. All-Red clearance interval ($T_{\text{all-red}} \ge 1$–$2\text{s}$) to allow the intersection to clear.

### 2.4 Pedestrian Interval Protection
* Dedicated pedestrian walk intervals must not be preempted without sufficient clearance time (Flashing Don't Walk / buffer time) for pedestrians already in crosswalks.

### 2.5 Emergency Corridor Overlap Arbitration
* When two or more emergency vehicles request conflicting green corridors:
  1. Priority is evaluated based on vehicle severity category (e.g. Life-saving cardiac ambulance vs non-critical transfer).
  2. The corridor scheduler solves a conflict-free arrival time window.
  3. Under unresolvable conflicts, the system maintains normal safe cycle transitions while providing prioritized green extensions, rather than creating instantaneous signal flipping.

### 2.6 Deterministic Failure Fallback
* If any controller crashes, produces unparseable actions, observes stale TraCI state, or times out ($> 500\text{ms}$):
  * The system enters **Deterministic Safe Fallback Mode**: signals revert to a pre-programmed fixed-time fail-safe cycle or yellow flash warning.
  * An alert is broadcast to the Command Centre and logged to `audit_events`.

## 3. Audit Logging
Every action submitted to the safety validator is logged:
* `timestamp`, `junction_id`, `requested_phase`, `validation_result` (ACCEPTED / REJECTED), `rejection_reason`, `effective_phase`.
