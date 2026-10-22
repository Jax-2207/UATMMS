# Phase 7: Reinforcement Learning - Decision Flow

**Phase:** 7 of 8  
**Purpose:** Document architectural decisions and their rationales

---

## High-Level Decision Tree

```
┌─ PHASE 7: Adaptive Traffic Signal Control via RL
│
├─ D1: Framework Selection
│  ├─ [✓] Gymnasium + Stable-Baselines3 PPO
│  ├─ [✗] Custom RL implementation
│  └─ [✗] Ray RLlib
│
├─ D2: Safety Enforcement Model
│  ├─ [✓] External SafetyWrapper (hard constraints)
│  ├─ [✗] Soft penalties in reward (learnable)
│  └─ [✗] No safety enforcement (risky)
│
├─ D3: Training Scope
│  ├─ [✓] Single junction first (J1)
│  ├─ [✗] Multi-junction from start (complex)
│  └─ [✗] No training, use baselines (no learning)
│
├─ D4: Reward Structure
│  ├─ [✓] Multi-objective with weighted sum
│  ├─ [✗] Single-objective (incomplete)
│  └─ [✗] Hierarchical rewards (overly complex)
│
├─ D5: Action Space
│  ├─ [✓] 4 discrete actions (hold, next, extend, emergency)
│  ├─ [✗] Continuous phase duration (hard to validate)
│  └─ [✗] 8+ actions per phase (too granular)
│
├─ D6: Evaluation Strategy
│  ├─ [✓] Baseline comparison + promotion criteria
│  ├─ [✗] No comparison (unclear if improvement)
│  └─ [✗] Complex metric aggregation (hard to interpret)
│
└─ D7: Deployment Path
   ├─ [✓] Offline training → checkpoint → promote → deploy
   ├─ [✗] Online learning (risky)
   └─ [✗] Sim-to-real transfer (future phase)
```

---

## Decision D1: Framework Selection

**Question:** Which RL framework to use for traffic signal control?

### Options Evaluated

#### Option A: Gymnasium + Stable-Baselines3 PPO ✅ CHOSEN
**Pros:**
- Industry-standard for research & production
- Rich ecosystem of algorithms (PPO, DQN, A2C, etc.)
- Active maintenance and community
- Excellent documentation
- Compatible with TensorFlow/PyTorch backends

**Cons:**
- Generic framework (requires custom SUMO integration)
- Heavier than minimal implementation

**Effort:** Medium (1 week for integration)

---

#### Option B: Custom RL Implementation ❌ REJECTED
**Pros:**
- Minimal dependencies
- Fully customizable
- Educational value

**Cons:**
- High maintenance burden
- Reinventing the wheel
- Bug-prone (gradient computation, buffer management)
- Difficult to scale to more complex algorithms later

**Effort:** High (4-6 weeks)

---

#### Option C: Ray RLlib ❌ REJECTED
**Pros:**
- Distributed training out-of-box
- Excellent for multi-agent RL
- Scales to large networks

**Cons:**
- Overkill for single junction
- Complex setup and configuration
- Higher computational overhead
- Steeper learning curve

**Effort:** Very High (2-3 weeks just for setup)

---

### Decision Rationale
**Chosen: Gymnasium + Stable-Baselines3**

Traffic signal control is a well-studied domain with published PPO results. Using industry-standard tools ensures:
1. Code quality and reliability
2. Easy maintenance and extension
3. Reproducibility with published papers
4. Faster development cycle

---

## Decision D2: Safety Enforcement Model

**Question:** How should we enforce safety constraints during RL learning?

### Options Evaluated

#### Option A: External SafetyWrapper (Hard Constraints) ✅ CHOSEN
**Architecture:**
```
RL Agent → Action → SafetyWrapper → Validate → Safe Action → Env
                         ↓
                  SafetyValidator
                  (hard constraints)
```

**Pros:**
- Guarantees safety is enforced
- Agent cannot learn to violate constraints
- Clear separation of concerns
- Enables offline safety validation

**Cons:**
- Action space exploration limited
- May reduce learning efficiency slightly

**Implementation:**
```python
class SafetyWrapper:
    def step(self, action):
        is_valid, rewritten_action, reason = self._validate_action(action)
        if not is_valid:
            reward -= 100.0  # Penalty
            action = rewritten_action  # Execute safe alternative
        return env.step(action)
```

---

#### Option B: Soft Penalties in Reward ❌ REJECTED
**Architecture:**
```
RL Agent → Action → Env → Reward (with penalty for violations)
```

**Pros:**
- Agent learns which constraints matter most
- Flexible trade-off between objectives

**Cons:**
- **Unacceptable Risk:** Agent can learn to violate constraints
- Violates principle of "safety as hard boundary"
- Difficult to guarantee safety in deployment

**Example Problem:**
```
Scenario: If waiting_time penalty < safety_violation penalty, 
          agent might learn: violate safety to reduce waiting time
```

---

#### Option C: No Safety Enforcement ❌ REJECTED
**Obvious risks:** Unsafe policies, infrastructure damage, unsafe emergency response

---

### Decision Rationale
**Chosen: External SafetyWrapper**

In critical systems (traffic control), safety must be non-negotiable. Hard constraints enforce safety through the architecture itself, not through learning incentives. This follows "Safety-Critical System" design principles:

1. **Fail-safe by design** - Invalid actions are impossible
2. **Defense in depth** - Multiple validation layers
3. **Predictable behavior** - Agent cannot surprise us with unsafe actions

---

## Decision D3: Training Scope

**Question:** Should we train on single or multiple junctions?

### Options Evaluated

#### Option A: Single Junction First (J1) ✅ CHOSEN
**Approach:**
1. Train on J1 until convergence
2. Evaluate and promote
3. Fine-tune on J2, J3, etc. (multi-junction training in Phase 7+)

**Pros:**
- Faster convergence
- Clearer reward signal (actions directly affect observable junction)
- Easier debugging
- Simpler validation

**Cons:**
- Multiple training runs for multiple junctions
- Doesn't learn network-wide coordination

**Training Time:** ~10 hours for J1 (1M timesteps)

---

#### Option B: Multi-Junction from Start ❌ REJECTED
**Approach:** Train MAPPO agent coordinating all junctions simultaneously

**Pros:**
- Network-wide optimal policies
- Learned coordination
- Single training run

**Cons:**
- Much larger state/action space
- Reward signal noisy (hard to attribute actions)
- **Much longer convergence** (~50+ hours)
- Difficult debugging
- Higher computational cost
- May not be better than separate controllers + cooperation

**Training Time:** ~50+ hours for network

---

### Decision Rationale
**Chosen: Single Junction First**

Progressive complexity is standard in RL:
1. Master simple problem first (single junction)
2. Validate performance improvement
3. Extend to harder problem (multi-junction coordination)

This approach:
- De-risks development (prove PPO works for single junction first)
- Enables faster iteration and debugging
- Provides solid foundation for network-wide extension
- Aligns with Phase 7 scope (proof of concept)

---

## Decision D4: Reward Structure

**Question:** How to formulate rewards for competing traffic objectives?

### Options Evaluated

#### Option A: Multi-Objective Weighted Sum ✅ CHOSEN
**Formula:**
```
Reward = w_wait*norm(waiting) + w_queue*norm(queue) + w_tp*norm(throughput)
         + w_em*norm(emergency) + w_safety*violations
```

**Weights:**
- Waiting time: -1.0 (primary)
- Queue length: -0.5 (secondary)
- Throughput: 0.01 (bonus)
- Emergency delay: -10.0 (critical)
- Safety violations: -100.0 (non-negotiable)

**Pros:**
- Interpretable (each component clear)
- Tunable (adjust weights per deployment)
- Aligns with traffic engineering standards
- Enables multi-objective Pareto analysis

**Cons:**
- Manual weight tuning required
- Multiple objectives can conflict

---

#### Option B: Single-Objective (Waiting Time Only) ❌ REJECTED
**Formula:**
```
Reward = -avg_waiting_time / 30
```

**Pros:**
- Simple
- Clear objective

**Cons:**
- **Incomplete:** Ignores queue stability, throughput
- Agent might trade long queues for slightly lower waiting
- Doesn't reflect real-world traffic engineering goals

---

#### Option C: Hierarchical Rewards ❌ REJECTED
**Approach:**
```
if violations > 0:
    reward = -violations * 100
elif queue_length > 15:
    reward = -(queue_length / 20)
else:
    reward = -(waiting_time / 30)
```

**Pros:**
- Hard constraints on safety & queue
- Simpler learning (fewer objectives simultaneously)

**Cons:**
- Discontinuous reward landscape (hard to learn)
- Abrupt policy changes at thresholds
- Difficult to fine-tune boundaries

---

### Decision Rationale
**Chosen: Multi-Objective Weighted Sum**

Traffic engineering inherently involves balancing multiple objectives. A weighted sum:
1. Matches how traffic engineers think about the problem
2. Enables principled trade-off decisions
3. Allows deployment-specific tuning via weights
4. Proven approach in transportation RL literature

---

## Decision D5: Action Space

**Question:** What actions should the RL agent be able to take?

### Options Evaluated

#### Option A: 4 Discrete Actions ✅ CHOSEN
| Action | Effect | Constraints |
|--------|--------|-------------|
| 0 (Hold) | Stay in current phase | None |
| 1 (Next) | Advance to next phase | After min_green (10s) |
| 2 (Extend) | Add 5s to green phase | Until max_green (90s) |
| 3 (Emergency) | Reserved for emergency | Handled by emergency manager |

**Pros:**
- Matches real signal controller capabilities
- Easy to validate against safety constraints
- Discrete = clear decision points
- Proven in traffic signal control literature

**Cons:**
- Coarse granularity (5s extend steps)
- Cannot tune exact phase duration

**Validation:** Simple state machine
```python
if action == 0:  # Hold - always valid
    valid = True
elif action == 1:  # Next - check min_green
    valid = (time_in_phase >= min_green)
elif action == 2:  # Extend - check max_green
    valid = (time_in_phase < max_green)
```

---

#### Option B: Continuous Phase Duration ❌ REJECTED
**Approach:** Agent outputs desired phase duration (10-90 seconds)

**Pros:**
- Maximum flexibility
- Fine-grained control

**Cons:**
- **Difficult to validate** (continuous output vs discrete safety constraints)
- High variance (agent must learn exact timing)
- Sample inefficiency
- Harder to explain to traffic engineers

---

#### Option C: 8+ Actions Per Phase ❌ REJECTED
**Approach:** One action per phase (8 phases) + meta-actions (extend, etc.)

**Pros:**
- More expressive
- Parallel decision-making

**Cons:**
- Large action space (harder to learn)
- High sample complexity
- Difficult to validate combinations
- Unnecessary for traffic signal control

---

### Decision Rationale
**Chosen: 4 Discrete Actions**

Discrete actions map cleanly to real signal controllers and are proven in traffic RL literature. They're:
1. Simple to validate
2. Sample-efficient to learn
3. Practical to deploy (match controller capabilities)
4. Interpretable to traffic engineers

---

## Decision D6: Evaluation Strategy

**Question:** How to evaluate if trained model is ready for production?

### Options Evaluated

#### Option A: Baseline Comparison + Promotion Criteria ✅ CHOSEN
**Process:**
1. Train model on junction
2. Evaluate on 20 episodes
3. Compare against 3 baselines (Fixed, Actuated, Max Pressure)
4. Check promotion criteria (reward, safety, consistency)
5. If passed: promote to production checkpoints

**Promotion Criteria:**
- Min reward: -5.0 per step
- Max violations: 5 per episode
- Reward consistency: std_dev ≤ 2.0
- Outperforms ≥ 1 baseline

**Pros:**
- Quantifiable go/no-go decision
- Baseline comparison provides context
- Objective criteria (no opinion-based decisions)
- Reproducible evaluation

**Cons:**
- Evaluation takes ~2 hours (20 episodes × 1 hour each)
- Doesn't guarantee real-world performance

---

#### Option B: No Comparison ❌ REJECTED
**Approach:** Just check if model converges

**Pros:**
- Fast (minutes)

**Cons:**
- **No way to know if improvement over baselines**
- Misses opportunities for better algorithms
- Unclear deployment value

---

#### Option C: Complex Metric Aggregation ❌ REJECTED
**Approach:** Multi-dimensional Pareto frontiers, weighted summation of 10+ metrics

**Pros:**
- Comprehensive

**Cons:**
- Difficult to interpret
- Hard to set thresholds
- Overkill for single metric (waiting time)
- Added complexity without commensurate benefit

---

### Decision Rationale
**Chosen: Baseline Comparison + Promotion Criteria**

In production ML systems, clear quantitative criteria are essential:
1. Baselines provide context (is improvement meaningful?)
2. Objective thresholds avoid subjective go/no-go calls
3. Reproducible evaluation across model versions
4. Aligns with MLOps best practices

---

## Decision D7: Deployment Path

**Question:** How to move from training to production deployment?

### Options Evaluated

#### Option A: Offline Training → Checkpoint → Promote → Deploy ✅ CHOSEN
**Pipeline:**
```
1. Train model offline (simulator) → save checkpoint
2. Evaluate on benchmark suite
3. Compare against baselines
4. If criteria met: promote to prod/checkpoints/J1_prod_v1.zip
5. Deploy to production controller
6. Monitor performance
7. If performance degrades: roll back to previous version
```

**Pros:**
- Safe (offline validation before deployment)
- Reproducible (checkpoints versioned)
- Rollback capability
- Clear audit trail

**Cons:**
- Sim-to-real gap (simulator != real world)
- Offline evaluation may not predict real performance

**Timeline:** 1-2 hours (training + evaluation)

---

#### Option B: Online Learning ❌ REJECTED
**Approach:** Deploy initial model, continue learning from real traffic data

**Pros:**
- Adapts to real traffic patterns
- Continuous improvement

**Cons:**
- **Too risky** for safety-critical system
- Potential for safety violations in production
- Difficult to debug issues
- Regulatory concerns

---

#### Option C: Sim-to-Real Transfer ❌ REJECTED (For Phase 7)
**Approach:** Train simulation-to-reality domain adaptation

**Pros:**
- Bridges sim-to-real gap
- Better real-world performance

**Cons:**
- Adds complexity (2-3 weeks development)
- Requires real-world test site
- Out of scope for Phase 7 (proof of concept)

**Note:** Planned for Phase 7+ multi-junction extension

---

### Decision Rationale
**Chosen: Offline → Checkpoint → Promote → Deploy**

Matches standard DevOps/MLOps practices:
1. Train offline (controlled environment)
2. Validate thoroughly (benchmark suite)
3. Version control (git checkpoints)
4. Promote through stages (dev → prod)
5. Monitor and rollback (versioned deployments)

This approach minimizes risk while maintaining ability to iterate quickly.

---

## Decision Summary Table

| # | Decision | Chosen | Rationale | Risk Level |
|---|----------|--------|-----------|-----------|
| D1 | Framework | Gymnasium + SB3 | Industry standard | Low |
| D2 | Safety | External wrapper | Hard constraints | Low |
| D3 | Scope | Single junction | Progressive complexity | Low |
| D4 | Reward | Multi-objective | Realistic objectives | Low |
| D5 | Actions | 4 discrete | Real controller mapping | Low |
| D6 | Eval | Baseline + criteria | Quantifiable go/no-go | Low |
| D7 | Deploy | Offline pipeline | Safe progression | Low |

**Overall Risk Assessment:** LOW - Conservative decisions prioritizing safety and reproducibility

---

## Key Principles Underlying Decisions

1. **Safety First:** Constraints are hard boundaries, not soft penalties
2. **Progressive Complexity:** Single junction before multi-junction
3. **Quantitative Evaluation:** Objective criteria over opinion
4. **Production-Ready:** Decisions align with MLOps best practices
5. **Simplicity:** Prefer interpretability over maximum expressiveness

---

## Future Decision Points (Phase 7+)

- **D8:** Multi-junction coordination strategy (MAPPO vs separate agents)
- **D9:** Real-world validation approach (test site, domain adaptation)
- **D10:** Online learning vs offline training in production
- **D11:** Policy generalization across different intersections

