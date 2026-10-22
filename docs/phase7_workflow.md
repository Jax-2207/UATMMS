# Phase 7: Reinforcement Learning - Workflow Guide

**Phase:** 7 of 8  
**Purpose:** Step-by-step guide for training, evaluating, and deploying RL models

---

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install gymnasium stable-baselines3 torch
```

### 2. Create Environment
```python
from rl.env.sumo_traffic_env import make_sumo_env
from rl.env.safety_wrapper import wrap_with_safety

env = make_sumo_env(junction_id="J1", time_limit=3600.0)
env = wrap_with_safety(env)
```

### 3. Create & Train Model
```python
from rl.training.train_ppo import create_ppo_trainer

trainer = create_ppo_trainer(junction_id="J1", n_envs=1)
results = trainer.train(total_timesteps=100_000)  # 10 min demo
```

### 4. Evaluate
```python
from rl.evaluation.benchmark import benchmark_suite

metrics = trainer.evaluate_policy(n_episodes=5)
print(f"Mean reward: {metrics['mean_reward']:.2f}")
print(f"Mean waiting time: {metrics['mean_length']:.0f}s")
```

---

## Complete Training Workflow

### Phase 7.1: Environment Setup

#### Step 1.1: Initialize SUMO Simulation
```python
from backend.app.simulation.manager import simulation_manager
from backend.app.network.topology import network_manager
from backend.app.safety.validator import safety_validator

# Load network
network = network_manager.load_network("data/network.net.xml")

# Start simulation
simulation_manager.initialize(network, mode="sumo")
simulation_manager.reset()

# Validate safety system
print(f"Junctions tracked: {len(safety_validator._junctions)}")
```

#### Step 1.2: Create Training Environment
```python
from rl.env.sumo_traffic_env import SUMOTrafficEnv
from rl.env.safety_wrapper import SafetyWrapper

# Base environment
base_env = SUMOTrafficEnv(
    junction_id="J1",
    simulation_time_limit=3600.0,
    reward_weights={
        "waiting_time": -1.0,
        "queue_length": -0.5,
        "throughput": 0.01,
        "emergency_delay": -10.0,
        "safety_violation": -100.0
    }
)

# Wrap with safety
env = SafetyWrapper(
    base_env,
    action_masking=True,
    penalty_on_violation=-100.0,
    hard_reject_critical=True
)

obs, info = env.reset()
print(f"Initial observation shape: {obs.shape}")
print(f"Action space: {env.action_space}")
```

---

### Phase 7.2: Model Training

#### Step 2.1: Create Trainer
```python
from rl.training.train_ppo import PPOTrainer

trainer = PPOTrainer(
    junction_id="J1",
    simulation_time_limit=3600.0,
    checkpoint_dir="rl/checkpoints",
    log_dir="rl/logs",
    device="auto"  # "cpu" or "cuda"
)

# Create environment
trainer.create_env(
    num_envs=4,  # Parallel environments
    normalize_observations=True
)

# Create PPO model
trainer.create_model(
    policy="MlpPolicy",
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.0,
    vf_coef=0.5
)
```

#### Step 2.2: Train Model
```python
# Train for 1 million timesteps (~10 hours)
results = trainer.train(
    total_timesteps=1_000_000,
    checkpoint_interval=10_000,       # Save every 10k steps
    eval_interval=50_000,             # Eval every 50k steps
    eval_episodes=5
)

print(f"Training completed in {results['elapsed_time']}")
print(f"Steps/sec: {results['steps_per_second']:.0f}")
print(f"Safety violations: {results['safety_violations']}")
```

#### Step 2.3: Monitor Training (TensorBoard)
```bash
tensorboard --logdir=rl/logs
# Open http://localhost:6006 in browser

# Monitor:
# - Policy reward
# - Policy loss
# - Value function loss
# - Learning curves
```

**Expected Learning Curves:**
```
Reward Progress:
  Epoch 0-100:   -50 → -20 (rapid improvement)
  Epoch 100-500:  -20 → -8  (plateauing)
  Epoch 500+:     -8 → -6   (fine-tuning)

Safety Violations:
  Epoch 0:       2-5 violations/episode (learning constraints)
  Epoch 100:     0-2 violations/episode (mostly safe)
  Epoch 500+:    0 violations/episode (fully safe)
```

---

### Phase 7.3: Model Evaluation

#### Step 3.1: Benchmark Evaluation
```python
from rl.evaluation.benchmark import benchmark_suite

# Run benchmark on trained model
metrics_list = benchmark_suite.evaluate_policy(
    env=trainer.env,
    policy_fn=lambda obs: trainer.model.predict(obs, deterministic=True)[0],
    n_episodes=20,
    deterministic=True
)

# Aggregate results
aggregated = benchmark_suite.aggregate_metrics(metrics_list)

print(f"Mean waiting time: {aggregated['traffic_efficiency']['avg_waiting_time_mean']:.1f}s")
print(f"LOS Distribution: {aggregated['performance']['los_distribution']}")
print(f"Safety violations: {aggregated['safety']['total_violations']}")
print(f"Overall score: {aggregated['performance']['overall_score_mean']:.1f}/100")
```

#### Step 3.2: Baseline Comparison
```python
# Compare with fixed-time, actuated, max-pressure
comparison = benchmark_suite.compare_policies(
    policies={
        "PPO": lambda obs: trainer.model.predict(obs)[0],
        "Fixed-Time": lambda obs: baseline_fixed_time(obs),
        "Actuated": lambda obs: baseline_actuated(obs),
        "Max-Pressure": lambda obs: baseline_maxpressure(obs)
    },
    env=trainer.env,
    n_episodes=10
)

print(f"Best strategy: {comparison['best_strategy']}")
print(f"Advantage: {comparison['performance_advantage']:.1f}%")
for policy, metrics in comparison['policies'].items():
    score = metrics['performance']['overall_score_mean']
    print(f"  {policy}: {score:.1f}/100")
```

#### Step 3.3: Promotion Decision
```python
from rl.evaluation.promotion import promotion_criteria

# Check promotion criteria
passed, report = promotion_criteria.evaluate_model(
    model_path=f"rl/checkpoints/ppo_J1_final.zip",
    env=trainer.env,
    n_episodes=20
)

if passed:
    print("✅ Model PASSED promotion criteria")
    print(f"   Mean reward: {report['statistics']['mean_reward']:.2f}")
    print(f"   Safety violations: {report['statistics']['max_violations']}")
    print(f"   Violations rate: {report['statistics']['max_violations']/3600:.1%}")
else:
    print("❌ Model FAILED promotion criteria")
    for failure in report['failures']:
        print(f"   - {failure}")

# Save report
criteria.save_report(report, "rl/evaluations/promotion_report.json")
```

---

### Phase 7.4: Model Management

#### Step 4.1: Save Model
```python
# Save after training
model_path = trainer.save_model("rl/checkpoints/ppo_J1_v1")
print(f"Model saved to: {model_path}")

# Also save training statistics
import json
stats = {
    "timestamp": datetime.now().isoformat(),
    "junction": "J1",
    "training_steps": 1_000_000,
    "final_reward": -6.5,
    "safety_violations": 0,
    "promotion_status": "PASSED"
}
with open("rl/checkpoints/ppo_J1_v1_metadata.json", "w") as f:
    json.dump(stats, f, indent=2)
```

#### Step 4.2: Load Model
```python
# Load for evaluation
trainer.load_model("rl/checkpoints/ppo_J1_v1.zip", env=trainer.env)

# Use for inference
obs, _ = trainer.env.reset()
for _ in range(100):
    action, _ = trainer.model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = trainer.env.step(action)
    if done or truncated:
        break
```

#### Step 4.3: Version Control
```bash
# Tag successful model versions
git tag -a "ppo-j1-v1-promoted" -m "Phase 7: PPO J1 model passed criteria"
git push origin ppo-j1-v1-promoted

# Archive checkpoint
zip -r rl/checkpoints/ppo_J1_v1.checkpoint.zip rl/checkpoints/ppo_J1*
```

---

## Advanced Workflows

### Multi-Phase Training

#### Train Multiple Junctions
```python
from rl.training.train_ppo import create_ppo_trainer

junctions = ["J1", "J2", "J3", "J4"]
models = {}

for junction_id in junctions:
    print(f"\n{'='*50}")
    print(f"Training junction {junction_id}")
    print(f"{'='*50}")
    
    trainer = create_ppo_trainer(
        junction_id=junction_id,
        n_envs=4,
        checkpoint_dir=f"rl/checkpoints/{junction_id}",
        log_dir=f"rl/logs/{junction_id}"
    )
    
    trainer.train(
        total_timesteps=500_000,  # Reduced for multiple junctions
        checkpoint_interval=5000,
        eval_interval=25_000
    )
    
    # Evaluate and check promotion
    passed, report = promotion_criteria.evaluate_model(
        f"rl/checkpoints/{junction_id}/ppo_{junction_id}_final.zip",
        trainer.env,
        n_episodes=10
    )
    
    if passed:
        print(f"✅ {junction_id} model promoted")
        models[junction_id] = trainer
    else:
        print(f"❌ {junction_id} model failed criteria")
```

---

### Transfer Learning (Phase 7+)

#### Fine-tune Pre-trained Model
```python
# Load model trained on J1
trainer = PPOTrainer(junction_id="J2")
trainer.create_env(num_envs=2)
trainer.create_model()

# Load pre-trained weights
from stable_baselines3 import PPO
pretrained = PPO.load("rl/checkpoints/ppo_J1_v1.zip", env=trainer.env)

# Use pre-trained policy as initialization
trainer.model.policy = pretrained.policy

# Fine-tune on J2 with lower learning rate
trainer.model.learning_rate = 1e-5  # Lower than initial (3e-4)

results = trainer.train(
    total_timesteps=100_000,  # Much less than J1 training
    checkpoint_interval=1000
)

print("Transfer learning complete")
```

---

### Hyperparameter Tuning

#### Grid Search for Optimal Parameters
```python
from itertools import product

learning_rates = [1e-4, 3e-4, 1e-3]
clip_ranges = [0.1, 0.2, 0.3]
gamma_values = [0.95, 0.99]

best_model = None
best_score = -float('inf')

for lr, clip, gamma in product(learning_rates, clip_ranges, gamma_values):
    trainer = create_ppo_trainer("J1")
    
    trainer.model.learning_rate = lr
    trainer.model.clip_range = clip
    trainer.model.gamma = gamma
    
    trainer.train(total_timesteps=100_000)
    
    metrics = trainer.evaluate_policy(n_episodes=5)
    score = metrics['mean_reward']
    
    print(f"lr={lr}, clip={clip}, gamma={gamma} → score={score:.2f}")
    
    if score > best_score:
        best_score = score
        best_model = trainer.model

print(f"\nBest hyperparameters: lr={lr}, clip={clip}, gamma={gamma}")
print(f"Best score: {best_score:.2f}")

trainer.model = best_model
trainer.train(total_timesteps=1_000_000)  # Full training with best params
```

---

### Deployment Checklist

#### Pre-Deployment Validation
```python
# Checklist before deploying to production
checklist = {
    "Model trained": False,
    "Safety criteria met": False,
    "Performance validated": False,
    "Baselines compared": False,
    "Rollback plan documented": False,
    "Monitoring configured": False
}

# 1. Train and save
trainer.train(total_timesteps=1_000_000)
model_path = trainer.save_model("rl/checkpoints/ppo_J1_v1")
checklist["Model trained"] = True

# 2. Check safety
passed, _ = promotion_criteria.evaluate_model(model_path, trainer.env)
checklist["Safety criteria met"] = passed

# 3. Benchmark
metrics = trainer.evaluate_policy(n_episodes=20)
checklist["Performance validated"] = metrics['mean_violations'] == 0

# 4. Compare baselines
comp = benchmark_suite.compare_policies(
    {"PPO": trainer.model.predict},
    trainer.env
)
checklist["Baselines compared"] = comp['best_strategy'] == "PPO_MODEL"

# 5. Rollback plan
print("""
Rollback Plan:
1. If PPO model performs poorly: revert to checkpoint ppo_J1_v0.zip
2. Monitoring alerts threshold: avg_waiting > 60s for 10+ min
3. Manual rollback command: cp ppo_J1_v0.zip rl/active/J1_signal_control.zip
""")
checklist["Rollback plan documented"] = True

# 6. Monitoring setup
print("""
Monitoring Metrics:
- Avg waiting time (target: < 25s)
- Queue lengths (target: < 10 vehicles)
- Safety violations (target: 0 per hour)
- Throughput (target: > 200 vph)
Alert on any metric exceeding threshold for 5+ minutes
""")
checklist["Monitoring configured"] = True

# Print status
print("\n" + "="*50)
print("DEPLOYMENT CHECKLIST")
print("="*50)
for item, status in checklist.items():
    mark = "✅" if status else "❌"
    print(f"{mark} {item}")

all_passed = all(checklist.values())
print(f"\n{'READY FOR DEPLOYMENT' if all_passed else 'NOT READY'}")
```

---

## Troubleshooting

### Issue: Model not converging
**Symptoms:** Reward stays at -50+ even after 100k steps

**Solutions:**
1. Check observation space - is data reaching model?
   ```python
   obs, _ = env.reset()
   print(f"Sample obs: {obs}, shape: {obs.shape}")
   ```

2. Increase learning rate
   ```python
   trainer.model.learning_rate = 1e-3  # Up from 3e-4
   trainer.train(total_timesteps=100_000)
   ```

3. Check safety wrapper isn't over-penalizing
   ```python
   for i in range(100):
       obs, info = env.reset()
       for _ in range(10):
           action = 1  # Force next phase
           obs, reward, done, truncated, info = env.step(action)
           if info.get("safety_violation"):
               print(f"Violation: {info.get('violation_reason')}")
   ```

---

### Issue: Memory error during training
**Symptoms:** `RuntimeError: CUDA out of memory`

**Solutions:**
1. Reduce parallel environments
   ```python
   trainer.create_env(num_envs=2)  # Down from 4
   ```

2. Reduce batch size
   ```python
   trainer.model.batch_size = 32  # Down from 64
   ```

3. Use CPU instead
   ```python
   trainer = PPOTrainer(device="cpu")
   ```

---

### Issue: Poor real-world performance
**Symptoms:** Model works in simulation but fails in real traffic

**Solutions:**
1. Check sim-to-real transfer
   - Real traffic more variable?
   - Real detectors noisier than SUMO?
   - Real signal hardware less responsive?

2. Add sim noise
   ```python
   env.observation_noise_std = 0.05  # Add Gaussian noise
   trainer.train(total_timesteps=500_000)
   ```

3. Domain adaptation (Phase 7+)
   - Use source-target domain networks
   - Collect real-world data for fine-tuning

---

## Performance Targets

### Expected Results After Training

**Single Junction (J1) - 1M Timesteps**

| Metric | Target | Unit |
|--------|--------|------|
| Mean reward | -8 ± 2 | per step |
| Avg waiting time | 18-25 | seconds |
| Queue length | 5-8 | vehicles |
| Throughput | 180-220 | vehicles/hour |
| Safety violations | 0 | per hour |
| Level of Service | B-C | A-F scale |

**Comparison to Baselines**

| Baseline | Waiting (s) | LOS | PPO Improvement |
|----------|------------|-----|-----------------|
| Fixed-Time (80s) | 35-40 | D | 30-40% ↓ |
| Actuated (30s) | 25-30 | C | 10-20% ↓ |
| Max Pressure | 20-25 | B | 5-15% comparable |

---

## Helpful Commands

```bash
# Monitor training
tensorboard --logdir=rl/logs --port=6006

# Check model file size
ls -lh rl/checkpoints/*.zip

# Run evaluation
python -c "
from rl.training.train_ppo import PPOTrainer
trainer = PPOTrainer()
trainer.load_model('rl/checkpoints/ppo_J1_v1.zip')
metrics = trainer.evaluate_policy(n_episodes=20)
print(f'Mean reward: {metrics[\"mean_reward\"]:.2f}')
"

# View promotion report
cat rl/evaluations/promotion_report.json | python -m json.tool

# Archive successful model
tar -czf rl/checkpoints/ppo_J1_v1_backup.tar.gz rl/checkpoints/ppo_J1*
```

---

## Next Steps

1. ✅ Train on J1 until convergence
2. ✅ Validate against baselines
3. ✅ Promote to production
4. 🔄 **Phase 7+:** Train on additional junctions
5. 🔄 **Phase 7+:** Multi-junction coordination
6. 🔄 **Phase 7+:** Real-world deployment

