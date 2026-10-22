"""
UATMMS Phase 7: Benchmark Suite
Provides comprehensive evaluation metrics for traffic signal control policies.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import gymnasium as gym

from backend.app.core.logging import logger


@dataclass
class BenchmarkMetrics:
    """Container for benchmark evaluation metrics."""
    
    # Traffic efficiency
    avg_waiting_time: float  # Average vehicle waiting time (seconds)
    total_vehicles_served: int  # Vehicles that completed their journey
    throughput: float  # Vehicles per hour through junction
    avg_queue_length: float  # Average vehicles waiting at stop line
    queue_variance: float  # Queue length standard deviation
    
    # Safety
    safety_violations: int  # Count of safety constraint violations
    violation_rate: float  # Violations per step
    emergency_response_time: float  # Average delay imposed on emergency vehicles (seconds)
    
    # RL metrics
    cumulative_reward: float  # Total reward over evaluation
    episode_length: int  # Steps in episode
    
    # Stability
    phase_switches_per_hour: float  # Number of phase changes
    action_consistency: float  # How often agent takes same action (0-1)
    
    # Derived metrics
    level_of_service: str  # A-F scale based on waiting time
    overall_performance_score: float  # Weighted score (0-100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "avg_waiting_time": self.avg_waiting_time,
            "total_vehicles_served": self.total_vehicles_served,
            "throughput": self.throughput,
            "avg_queue_length": self.avg_queue_length,
            "queue_variance": self.queue_variance,
            "safety_violations": self.safety_violations,
            "violation_rate": self.violation_rate,
            "emergency_response_time": self.emergency_response_time,
            "cumulative_reward": self.cumulative_reward,
            "episode_length": self.episode_length,
            "phase_switches_per_hour": self.phase_switches_per_hour,
            "action_consistency": self.action_consistency,
            "level_of_service": self.level_of_service,
            "overall_performance_score": self.overall_performance_score
        }


class BenchmarkSuite:
    """
    Comprehensive benchmark evaluation for RL policies.
    Evaluates against multiple metrics and provides comparative analysis.
    """

    def __init__(self):
        """Initialize benchmark suite."""
        # Performance weights for overall score (sum to 1.0)
        self.score_weights = {
            "waiting_time": 0.30,
            "throughput": 0.25,
            "safety": 0.25,
            "consistency": 0.15,
            "reward": 0.05
        }

        # Level of Service thresholds (seconds)
        self.los_thresholds = {
            "A": 10.0,
            "B": 20.0,
            "C": 35.0,
            "D": 55.0,
            "E": 80.0,
            "F": float('inf')
        }

        logger.info("[BenchmarkSuite] Initialized with performance weights")

    def evaluate_policy(
        self,
        env: gym.Env,
        policy_fn,
        n_episodes: int = 10,
        deterministic: bool = True
    ) -> List[BenchmarkMetrics]:
        """
        Evaluate a policy over multiple episodes and compute metrics.

        Args:
            env: Gymnasium environment
            policy_fn: Function that takes observation and returns action
            n_episodes: Number of evaluation episodes
            deterministic: If True, use deterministic policy

        Returns:
            List of BenchmarkMetrics for each episode
        """
        episode_metrics = []

        for episode in range(n_episodes):
            obs, _ = env.reset()
            done = False
            
            # Accumulators
            episode_reward = 0.0
            episode_length = 0
            waiting_times = []
            queue_lengths = []
            safety_violations = 0
            vehicles_served = 0
            phase_switches = 0
            action_history = []

            last_phase = None
            emergency_delays = []

            while not done:
                # Get action
                action = policy_fn(obs)
                action_history.append(action)

                # Step environment
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated

                # Accumulate metrics
                episode_reward += reward
                episode_length += 1

                # Extract metrics from observation and info
                current_phase = int(obs[12] * 7) if len(obs) > 12 else 0
                if last_phase is not None and current_phase != last_phase:
                    phase_switches += 1
                last_phase = current_phase

                waiting_times.append(obs[4:8].mean() if len(obs) > 8 else 0)
                queue_lengths.append(obs[0:4].mean() if len(obs) > 4 else 0)

                if info.get("safety_violation", False):
                    safety_violations += 1

                episode_info = info.get("episode_info", {})
                vehicles_served = episode_info.get("vehicles_passed", 0)

                if "emergency_delay" in info:
                    emergency_delays.append(info["emergency_delay"])

            # Compute metrics
            avg_waiting = np.mean(waiting_times) if waiting_times else 0.0
            avg_queue = np.mean(queue_lengths) if queue_lengths else 0.0
            queue_var = np.std(queue_lengths) if len(queue_lengths) > 1 else 0.0

            # Throughput: vehicles per hour
            # Assume episode represents 1 hour of simulation
            throughput = vehicles_served  # vehicles per hour equivalent

            # Phase switches per hour
            phase_switches_per_hour = (phase_switches / episode_length) * 3600.0

            # Action consistency: what % of steps had the same action as previous
            action_consistency = 0.0
            if len(action_history) > 1:
                matches = sum(1 for i in range(1, len(action_history)) 
                              if action_history[i] == action_history[i-1])
                action_consistency = matches / (len(action_history) - 1)

            # Safety metrics
            violation_rate = safety_violations / max(episode_length, 1)
            avg_emergency_delay = np.mean(emergency_delays) if emergency_delays else 0.0

            # Level of service
            los = self._get_level_of_service(avg_waiting)

            # Overall performance score
            overall_score = self._compute_performance_score(
                avg_waiting=avg_waiting,
                throughput=throughput,
                safety_violations=safety_violations,
                action_consistency=action_consistency,
                cumulative_reward=episode_reward
            )

            metrics = BenchmarkMetrics(
                avg_waiting_time=float(avg_waiting),
                total_vehicles_served=int(vehicles_served),
                throughput=float(throughput),
                avg_queue_length=float(avg_queue),
                queue_variance=float(queue_var),
                safety_violations=int(safety_violations),
                violation_rate=float(violation_rate),
                emergency_response_time=float(avg_emergency_delay),
                cumulative_reward=float(episode_reward),
                episode_length=episode_length,
                phase_switches_per_hour=float(phase_switches_per_hour),
                action_consistency=float(action_consistency),
                level_of_service=los,
                overall_performance_score=float(overall_score)
            )

            episode_metrics.append(metrics)

            logger.info(
                f"[BenchmarkSuite] Episode {episode+1}/{n_episodes}: "
                f"waiting={avg_waiting:.1f}s, LOS={los}, "
                f"violations={safety_violations}, score={overall_score:.1f}"
            )

        return episode_metrics

    def aggregate_metrics(
        self,
        metrics_list: List[BenchmarkMetrics]
    ) -> Dict[str, Any]:
        """
        Aggregate metrics across episodes.

        Args:
            metrics_list: List of BenchmarkMetrics from episodes

        Returns:
            Aggregated statistics
        """
        if not metrics_list:
            return {}

        aggregated = {
            "n_episodes": len(metrics_list),
            "evaluation_timestamp": datetime.now().isoformat(),
            "traffic_efficiency": {
                "avg_waiting_time_mean": np.mean([m.avg_waiting_time for m in metrics_list]),
                "avg_waiting_time_std": np.std([m.avg_waiting_time for m in metrics_list]),
                "total_vehicles_mean": np.mean([m.total_vehicles_served for m in metrics_list]),
                "throughput_mean": np.mean([m.throughput for m in metrics_list]),
                "throughput_std": np.std([m.throughput for m in metrics_list]),
                "queue_length_mean": np.mean([m.avg_queue_length for m in metrics_list]),
                "queue_length_std": np.std([m.avg_queue_length for m in metrics_list])
            },
            "safety": {
                "total_violations": sum(m.safety_violations for m in metrics_list),
                "avg_violations_per_episode": np.mean([m.safety_violations for m in metrics_list]),
                "violation_rate_mean": np.mean([m.violation_rate for m in metrics_list]),
                "emergency_response_time_mean": np.mean([m.emergency_response_time for m in metrics_list])
            },
            "rl_metrics": {
                "cumulative_reward_mean": np.mean([m.cumulative_reward for m in metrics_list]),
                "cumulative_reward_std": np.std([m.cumulative_reward for m in metrics_list]),
                "avg_episode_length": np.mean([m.episode_length for m in metrics_list])
            },
            "stability": {
                "phase_switches_per_hour_mean": np.mean([m.phase_switches_per_hour for m in metrics_list]),
                "action_consistency_mean": np.mean([m.action_consistency for m in metrics_list])
            },
            "performance": {
                "overall_score_mean": np.mean([m.overall_performance_score for m in metrics_list]),
                "overall_score_std": np.std([m.overall_performance_score for m in metrics_list]),
                "los_distribution": self._compute_los_distribution(metrics_list)
            }
        }

        return aggregated

    def compare_policies(
        self,
        policies: Dict[str, Any],
        env: gym.Env,
        n_episodes: int = 5
    ) -> Dict[str, Any]:
        """
        Compare multiple policies against each other.

        Args:
            policies: Dict of {policy_name: policy_fn}
            env: Environment for evaluation
            n_episodes: Episodes per policy

        Returns:
            Comparative analysis report
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "n_episodes_per_policy": n_episodes,
            "policies": {}
        }

        for policy_name, policy_fn in policies.items():
            logger.info(f"[BenchmarkSuite] Evaluating policy: {policy_name}")

            metrics_list = self.evaluate_policy(
                env=env,
                policy_fn=policy_fn,
                n_episodes=n_episodes,
                deterministic=True
            )

            aggregated = self.aggregate_metrics(metrics_list)
            comparison["policies"][policy_name] = aggregated

        # Rank policies
        rankings = {}
        for policy_name, agg in comparison["policies"].items():
            score = agg.get("performance", {}).get("overall_score_mean", 0)
            rankings[policy_name] = score

        comparison["ranking"] = sorted(
            rankings.items(),
            key=lambda x: x[1],
            reverse=True
        )

        best_policy = comparison["ranking"][0] if comparison["ranking"] else (None, 0)
        comparison["best_policy"] = best_policy[0]
        comparison["best_policy_score"] = float(best_policy[1])

        logger.info(
            f"[BenchmarkSuite] Comparison complete. Best: {best_policy[0]} "
            f"(score={best_policy[1]:.1f})"
        )

        return comparison

    def _get_level_of_service(self, avg_waiting_time: float) -> str:
        """
        Compute level of service (A-F) based on average waiting time.

        Args:
            avg_waiting_time: Average waiting time in seconds

        Returns:
            Level of service letter (A-F)
        """
        for level, threshold in sorted(self.los_thresholds.items(), key=lambda x: x[1]):
            if avg_waiting_time <= threshold:
                return level
        return "F"

    def _compute_performance_score(
        self,
        avg_waiting: float,
        throughput: float,
        safety_violations: int,
        action_consistency: float,
        cumulative_reward: float
    ) -> float:
        """
        Compute overall performance score (0-100).

        Args:
            avg_waiting: Average waiting time (seconds)
            throughput: Vehicles per hour
            safety_violations: Count of violations
            action_consistency: Consistency score (0-1)
            cumulative_reward: Episode cumulative reward

        Returns:
            Performance score 0-100
        """
        # Normalize each metric to 0-1
        waiting_score = max(0, 1 - (avg_waiting / 60.0))  # 60s = 0 score
        throughput_score = min(1, throughput / 100.0)  # 100 vehicles/hour = max
        safety_score = max(0, 1 - (safety_violations / 10.0))  # 10 violations = 0
        consistency_score = action_consistency  # Already 0-1
        reward_score = min(1, max(0, (cumulative_reward + 100) / 200.0))  # Normalize

        # Apply weights
        weighted_score = (
            self.score_weights["waiting_time"] * waiting_score +
            self.score_weights["throughput"] * throughput_score +
            self.score_weights["safety"] * safety_score +
            self.score_weights["consistency"] * consistency_score +
            self.score_weights["reward"] * reward_score
        )

        # Scale to 0-100
        return weighted_score * 100.0

    def _compute_los_distribution(
        self,
        metrics_list: List[BenchmarkMetrics]
    ) -> Dict[str, int]:
        """Count distribution of level of service across episodes."""
        los_dist = {level: 0 for level in "ABCDEF"}
        for metric in metrics_list:
            los_dist[metric.level_of_service] += 1
        return los_dist


# Global instance
benchmark_suite = BenchmarkSuite()

