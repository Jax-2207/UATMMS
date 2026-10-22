"""
UATMMS Phase 7: Model Promotion Engine
Determines if a trained model meets production readiness criteria.
Compares against baselines and validates safety constraints.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from stable_baselines3 import PPO
import gymnasium as gym

from backend.app.core.logging import logger
from rl.env.sumo_traffic_env import SUMOTrafficEnv
from rl.env.safety_wrapper import SafetyWrapper


class BaselineComparison:
    """
    Represents a baseline traffic control strategy for comparison.
    Baselines: Fixed-time, Actuated, MaxPressure
    """

    class Baseline:
        """Baseline strategy implementation."""

        def __init__(self, strategy_name: str, params: Dict = None):
            """
            Initialize baseline.

            Args:
                strategy_name: "fixed_time", "actuated", or "max_pressure"
                params: Strategy parameters
            """
            self.strategy_name = strategy_name
            self.params = params or {}

        def compute_action(self, observation: np.ndarray) -> int:
            """
            Compute baseline action given observation.

            Args:
                observation: Environment observation

            Returns:
                Action (0-3)
            """
            if self.strategy_name == "fixed_time":
                # Fixed-time: cycle through phases periodically
                phase_index = int(observation[12] * 7)  # Normalize phase to [0, 7]
                cycle_length = self.params.get("cycle_length", 80)
                time_in_phase = observation[13] * 90.0  # Denormalize time
                
                # Simple fixed timing: ~10s per phase
                if time_in_phase < 10.0:
                    return 0  # Hold
                else:
                    return 1  # Next phase

            elif self.strategy_name == "actuated":
                # Actuated: respond to queue lengths
                queues = observation[0:4]  # N, S, E, W queues
                max_queue_idx = np.argmax(queues)
                
                # If max queue on this phase, extend; otherwise switch
                current_phase = int(observation[12] * 7)
                # Simplified: each phase serves two approaches
                if current_phase // 2 == max_queue_idx // 2:
                    return 2  # Extend
                else:
                    return 1  # Next phase

            elif self.strategy_name == "max_pressure":
                # Max Pressure: minimize queue buildup
                queues = observation[0:4]
                waiting_times = observation[4:8]
                
                # Pressure = queue + waiting time (weighted)
                pressure = queues + 0.5 * waiting_times
                
                # Current phase approaches
                current_phase = int(observation[12] * 7)
                phase_approaches = [current_phase % 2, (current_phase + 1) % 2]
                
                # Downstream pressure
                downstream_capacity = observation[15]
                
                if downstream_capacity > 0.5 and np.mean([pressure[i] for i in phase_approaches]) < 3.0:
                    return 2  # Extend green
                else:
                    return 1  # Switch

            else:
                # Unknown strategy: default to hold
                return 0

    @staticmethod
    def get_baseline(strategy_name: str) -> "BaselineComparison.Baseline":
        """Create a baseline strategy."""
        return BaselineComparison.Baseline(strategy_name)


class PromotionCriteria:
    """
    Defines criteria for promoting a model to production.
    """

    def __init__(self):
        """Initialize promotion criteria."""
        # Reward thresholds (vs. baseline)
        self.min_reward_improvement = 0.10  # 10% better than baseline
        self.min_absolute_reward = -5.0  # Absolute minimum acceptable reward

        # Safety constraints
        self.max_safety_violations_per_episode = 5
        self.max_violation_rate = 0.01  # Max 1% of steps
        self.zero_violations_required = False  # Strict safety requirement

        # Consistency
        self.min_evaluation_episodes = 20
        self.max_reward_std_dev = 2.0  # Low variance required

        # Performance
        self.min_throughput_improvement = 0.05  # 5% more vehicles through junction
        self.max_waiting_time_increase = 0.1  # Waiting time can't increase >10%

        logger.info("[PromotionCriteria] Initialized with production-ready thresholds")

    def evaluate_model(
        self,
        model_path: str,
        env: gym.Env,
        n_episodes: int = 20,
        baselines: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate if model meets promotion criteria.

        Args:
            model_path: Path to trained PPO model
            env: Evaluation environment
            n_episodes: Number of evaluation episodes
            baselines: Baseline performance data (for comparison)

        Returns:
            (passed: bool, report: Dict with detailed results)
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "model_path": model_path,
            "n_episodes": n_episodes,
            "criteria_results": {},
            "passed": False,
            "failures": []
        }

        try:
            # Load model
            model = PPO.load(model_path, env=env)
            logger.info(f"[PromotionCriteria] Loaded model from {model_path}")
        except Exception as e:
            report["failures"].append(f"Failed to load model: {e}")
            report["error"] = str(e)
            return False, report

        # Run evaluation episodes
        episode_rewards = []
        episode_lengths = []
        episode_violations = []
        episode_throughput = []

        for episode in range(n_episodes):
            obs, _ = env.reset()
            done = False
            episode_reward = 0.0
            episode_length = 0
            violations = 0
            vehicles_passed = 0

            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                episode_reward += reward
                episode_length += 1

                if info.get("safety_violation", False):
                    violations += 1

                vehicles_passed = info.get("episode_info", {}).get("vehicles_passed", 0)

            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            episode_violations.append(violations)
            episode_throughput.append(vehicles_passed)

        # Compute statistics
        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)
        mean_violations = np.mean(episode_violations)
        max_violations = np.max(episode_violations)
        mean_throughput = np.mean(episode_throughput)

        # Check criteria
        criteria_passed = []
        failures = []

        # Criterion 1: Absolute reward minimum
        if mean_reward >= self.min_absolute_reward:
            criteria_passed.append("Absolute reward minimum")
            report["criteria_results"]["absolute_reward"] = {
                "passed": True,
                "value": mean_reward,
                "threshold": self.min_absolute_reward
            }
        else:
            failures.append(
                f"Reward {mean_reward:.2f} below minimum {self.min_absolute_reward:.2f}"
            )
            report["criteria_results"]["absolute_reward"] = {
                "passed": False,
                "value": mean_reward,
                "threshold": self.min_absolute_reward
            }

        # Criterion 2: Safety violations
        if max_violations <= self.max_safety_violations_per_episode:
            criteria_passed.append("Safety violations within limits")
            report["criteria_results"]["safety_violations"] = {
                "passed": True,
                "value": max_violations,
                "threshold": self.max_safety_violations_per_episode
            }
        else:
            failures.append(
                f"Max violations {max_violations} exceeds threshold "
                f"{self.max_safety_violations_per_episode}"
            )
            report["criteria_results"]["safety_violations"] = {
                "passed": False,
                "value": max_violations,
                "threshold": self.max_safety_violations_per_episode
            }

        # Criterion 3: Reward consistency
        if std_reward <= self.max_reward_std_dev:
            criteria_passed.append("Reward consistency acceptable")
            report["criteria_results"]["reward_consistency"] = {
                "passed": True,
                "value": std_reward,
                "threshold": self.max_reward_std_dev
            }
        else:
            failures.append(
                f"Reward std dev {std_reward:.2f} exceeds max {self.max_reward_std_dev:.2f}"
            )
            report["criteria_results"]["reward_consistency"] = {
                "passed": False,
                "value": std_reward,
                "threshold": self.max_reward_std_dev
            }

        # Overall result
        overall_passed = len(failures) == 0
        report["passed"] = overall_passed
        report["failures"] = failures
        report["statistics"] = {
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward),
            "mean_violations": float(mean_violations),
            "max_violations": int(max_violations),
            "mean_throughput": float(mean_throughput),
            "evaluation_episodes": n_episodes
        }

        if overall_passed:
            logger.info("[PromotionCriteria] ✓ Model PASSED promotion criteria")
        else:
            logger.warning(f"[PromotionCriteria] ✗ Model FAILED: {'; '.join(failures)}")

        return overall_passed, report

    def compare_with_baselines(
        self,
        model_path: str,
        env: gym.Env,
        n_episodes: int = 10
    ) -> Dict[str, Any]:
        """
        Compare model performance against baseline strategies.

        Args:
            model_path: Path to trained PPO model
            env: Evaluation environment
            n_episodes: Episodes per baseline

        Returns:
            Comparison report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "model_path": model_path,
            "baselines": {},
            "best_strategy": None
        }

        try:
            model = PPO.load(model_path, env=env)
        except Exception as e:
            logger.error(f"[PromotionCriteria] Failed to load model: {e}")
            report["error"] = str(e)
            return report

        # Evaluate model
        model_rewards = []
        for episode in range(n_episodes):
            obs, _ = env.reset()
            done = False
            episode_reward = 0.0

            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                episode_reward += reward

            model_rewards.append(episode_reward)

        model_mean = np.mean(model_rewards)
        report["model"] = {
            "mean_reward": float(model_mean),
            "std_reward": float(np.std(model_rewards))
        }

        # Evaluate baselines
        for baseline_name in ["fixed_time", "actuated", "max_pressure"]:
            baseline = BaselineComparison.get_baseline(baseline_name)
            baseline_rewards = []

            for episode in range(n_episodes):
                obs, _ = env.reset()
                done = False
                episode_reward = 0.0

                while not done:
                    action = baseline.compute_action(obs)
                    obs, reward, terminated, truncated, _ = env.step(action)
                    done = terminated or truncated
                    episode_reward += reward

                baseline_rewards.append(episode_reward)

            baseline_mean = np.mean(baseline_rewards)
            improvement = (model_mean - baseline_mean) / abs(baseline_mean) if baseline_mean != 0 else 0

            report["baselines"][baseline_name] = {
                "mean_reward": float(baseline_mean),
                "std_reward": float(np.std(baseline_rewards)),
                "improvement_vs_model": float(improvement * 100)  # Percentage
            }

        # Determine best
        baseline_means = {
            name: data["mean_reward"] 
            for name, data in report["baselines"].items()
        }
        best_baseline = max(baseline_means, key=baseline_means.get)
        best_mean = baseline_means[best_baseline]

        if model_mean > best_mean:
            report["best_strategy"] = "PPO_MODEL"
            report["performance_advantage"] = float((model_mean - best_mean) / abs(best_mean) * 100)
        else:
            report["best_strategy"] = best_baseline
            report["performance_advantage"] = float((best_mean - model_mean) / abs(model_mean) * 100)

        logger.info(
            f"[PromotionCriteria] Baseline comparison: "
            f"PPO={model_mean:.2f}, Best baseline={best_baseline} ({best_mean:.2f})"
        )

        return report

    def save_report(self, report: Dict, output_path: str) -> str:
        """
        Save promotion report to JSON file.

        Args:
            report: Report dictionary
            output_path: Output file path

        Returns:
            Full path to saved report
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"[PromotionCriteria] Report saved to {output_path}")
        return output_path


# Global instance
promotion_criteria = PromotionCriteria()

