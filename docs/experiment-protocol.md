# UATMMS Evaluation Metrics and Experiment Protocol

## 1. Evaluation Protocol Standards
To guarantee scientifically sound, reproducible results, all traffic controllers (Fixed-time, Queue-based Adaptive, Max-Pressure, PPO Reinforcement Learning) must be evaluated under strictly identical conditions.

### Rules of Fair Comparison
1. **Identical Seeds & Demands**: Every controller is evaluated on identical random seeds across identical origin-destination demand profiles.
2. **Multi-Seed Testing**: Never report only the single best run. Run at least 5 different random seeds and report **mean $\pm$ standard deviation**.
3. **Train / Test Split**: Scenarios used for training RL models must not be used for final evaluation. Evaluation scenarios must include unseen demand spikes and unannounced incident configurations.
4. **Warm-up Period**: Every evaluation run must define a warm-up period (e.g. first 300 simulation steps) to allow traffic to populate the network before metrics are accumulated.
5. **Trade-off Reporting**: Always report both emergency performance (e.g., ambulance travel time) AND network disruption (delay incurred by regular passenger cars and public transport).

---

## 2. Core Metrics Definition

| Metric | Symbol / Unit | Calculation Formula / Description |
| :--- | :--- | :--- |
| **Average Waiting Time** | $W_{\text{avg}}$ (seconds) | Total cumulative time vehicles were stopped ($\text{speed} < 0.1 \text{ m/s}$) divided by total vehicle count. |
| **Average Travel Time** | $T_{\text{avg}}$ (seconds) | Total duration from departure to destination arrival for all completed trips. |
| **Throughput** | $Q$ (vehicles/hour) | Total number of vehicles reaching their destinations per hour of simulation time. |
| **Queue Length** | $L_{\text{queue}}$ (vehicles or meters) | Mean and maximum vehicle count lined up behind red lights across all lanes. |
| **Emergency Travel Time** | $T_{\text{emerg}}$ (seconds) | Time elapsed from emergency dispatch request to destination arrival. |
| **Red Lights Encountered** | Count | Number of times an emergency vehicle had to stop at a red light along its green corridor. Target: 0. |
| **Disruption Ratio** | Ratio | $\frac{W_{\text{avg with preemption}} - W_{\text{avg baseline}}}{W_{\text{avg baseline}}}$ to measure collateral congestion impact. |
| **Safety Violations** | Count | Number of conflicting greens, sub-minimum green transitions, or clearance breaches. **Must be 0**. |
| **Controller Latency** | $\Delta t$ (ms) | Time taken by algorithm to compute next signal decisions per step. |

---

## 3. Standard Benchmarking Scenarios
1. **Low Demand (Off-peak)**: 500 vehicles/hour across network.
2. **Medium Demand (Standard)**: 1,500 vehicles/hour.
3. **High Congestion (Peak Rush Hour)**: 3,000 vehicles/hour with bottleneck junctions.
4. **Incident & Blockage**: Peak demand with 1–2 lane closures or random obstacle injection.
5. **Single Emergency Vehicle**: Ambulance traversing cross-network during medium demand.
6. **Concurrent Conflicting Emergencies**: Two ambulances crossing perpendicular routes simultaneously.
