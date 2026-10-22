"""
Unit tests for UATMMS RL Evaluation (Phase 7)
Tests: Model promotion, benchmark suite, baseline comparison
"""

import pytest
import numpy as np
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from rl.evaluation.promotion import PromotionCriteria, BaselineComparison
from rl.evaluation.benchmark import BenchmarkSuite, BenchmarkMetrics
from backend.app.core.logging import logger


class TestPromotionCriteriaInitialization:
    """Test promotion criteria setup."""

    def test_criteria_creation(self):
        """Test promotion criteria is created."""
        criteria = PromotionCriteria()
        assert criteria is not None
        assert criteria.min_reward_improvement == 0.10
        assert criteria.max_safety_violations_per_episode == 5

    def test_criteria_thresholds(self):
        """Test promotion criteria thresholds are set."""
        criteria = PromotionCriteria()
        
        assert criteria.min_absolute_reward == -5.0
        assert criteria.max_violation_rate == 0.01
        assert criteria.max_reward_std_dev == 2.0
        assert criteria.min_evaluation_episodes == 20


class TestBaselineComparison:
    """Test baseline strategy implementations."""

    def test_fixed_time_baseline(self):
        """Test fixed-time baseline strategy."""
        baseline = BaselineComparison.get_baseline("fixed_time")
        
        obs = np.array([0.1, 0.2, 0.3, 0.4,  # queues
                       0.2, 0.3, 0.4, 0.5,  # waiting times
                       0.5, 0.6, 0.7, 0.8,  # speeds
                       0.25, 0.3, 0.0, 0.75])  # phase, time, incident, capacity
        
        action = baseline.compute_action(obs)
        assert action in [0, 1, 2]

    def test_actuated_baseline(self):
        """Test actuated baseline strategy."""
        baseline = BaselineComparison.get_baseline("actuated")
        
        obs = np.array([0.1, 0.2, 0.8, 0.4,  # queues (high on E)
                       0.2, 0.3, 0.4, 0.5,
                       0.5, 0.6, 0.7, 0.8,
                       0.25, 0.3, 0.0, 0.75])
        
        action = baseline.compute_action(obs)
        assert action in [0, 1, 2]

    def test_max_pressure_baseline(self):
        """Test max pressure baseline strategy."""
        baseline = BaselineComparison.get_baseline("max_pressure")
        
        obs = np.array([0.1, 0.2, 0.3, 0.4,
                       0.2, 0.3, 0.4, 0.5,
                       0.5, 0.6, 0.7, 0.8,
                       0.25, 0.3, 0.0, 0.75])
        
        action = baseline.compute_action(obs)
        assert action in [0, 1, 2]

    def test_unknown_baseline_defaults_to_hold(self):
        """Test unknown baseline defaults to hold."""
        baseline = BaselineComparison.get_baseline("unknown_strategy")
        
        obs = np.zeros(16)
        action = baseline.compute_action(obs)
        
        assert action == 0  # Hold action


class TestPromotionEvaluation:
    """Test model promotion evaluation."""

    @patch('rl.evaluation.promotion.PPO.load')
    def test_evaluate_model_passed(self, mock_load):
        """Test evaluation passes when criteria met."""
        with tempfile.TemporaryDirectory() as tmpdir:
            criteria = PromotionCriteria()
            
            # Create mock model
            mock_model = MagicMock()
            mock_load.return_value = mock_model
            
            # Create mock environment
            mock_env = MagicMock()
            obs = np.ones(16) * 0.5
            mock_env.reset.return_value = (obs, {})
            mock_env.step.return_value = (obs, 5.0, False, False, {"safety_violation": False, "episode_info": {}})
            
            # Mock predict to return good actions
            mock_model.predict.return_value = (0, None)
            
            model_path = os.path.join(tmpdir, "model.zip")
            Path(model_path).touch()
            
            passed, report = criteria.evaluate_model(
                model_path=model_path,
                env=mock_env,
                n_episodes=5
            )
            
            assert "passed" in report
            assert "criteria_results" in report
            assert "statistics" in report

    @patch('rl.evaluation.promotion.PPO.load')
    def test_evaluate_model_with_violations(self, mock_load):
        """Test evaluation flags safety violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            criteria = PromotionCriteria()
            
            mock_model = MagicMock()
            mock_load.return_value = mock_model
            
            mock_env = MagicMock()
            obs = np.ones(16) * 0.5
            
            # Simulate violations
            mock_env.reset.return_value = (obs, {})
            mock_env.step.return_value = (obs, 0.0, False, False, {
                "safety_violation": True,
                "episode_info": {"safety_violations": 3}
            })
            
            mock_model.predict.return_value = (0, None)
            
            model_path = os.path.join(tmpdir, "model.zip")
            Path(model_path).touch()
            
            passed, report = criteria.evaluate_model(
                model_path=model_path,
                env=mock_env,
                n_episodes=5
            )
            
            assert "failures" in report

    def test_evaluate_model_missing_file(self):
        """Test evaluation fails for missing model file."""
        criteria = PromotionCriteria()
        
        mock_env = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            passed, report = criteria.evaluate_model(
                model_path=os.path.join(tmpdir, "nonexistent.zip"),
                env=mock_env,
                n_episodes=5
            )
            
            assert passed is False
            assert "error" in report


class TestBaselineComparison:
    """Test baseline comparison functionality."""

    @patch('rl.evaluation.promotion.PPO.load')
    def test_compare_with_baselines(self, mock_load):
        """Test comparing model with baselines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            criteria = PromotionCriteria()
            
            mock_model = MagicMock()
            mock_load.return_value = mock_model
            
            mock_env = MagicMock()
            obs = np.ones(16) * 0.5
            mock_env.reset.return_value = (obs, {})
            mock_env.step.return_value = (obs, 1.0, False, False, {})
            
            mock_model.predict.return_value = (0, None)
            
            model_path = os.path.join(tmpdir, "model.zip")
            Path(model_path).touch()
            
            comparison = criteria.compare_with_baselines(
                model_path=model_path,
                env=mock_env,
                n_episodes=2
            )
            
            assert "model" in comparison
            assert "baselines" in comparison
            assert "best_strategy" in comparison
            assert "fixed_time" in comparison["baselines"]
            assert "actuated" in comparison["baselines"]
            assert "max_pressure" in comparison["baselines"]

    def test_save_report(self):
        """Test saving promotion report to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            criteria = PromotionCriteria()
            
            report = {
                "timestamp": "2026-10-22T00:00:00",
                "passed": True,
                "criteria_results": {}
            }
            
            output_path = os.path.join(tmpdir, "report.json")
            saved_path = criteria.save_report(report, output_path)
            
            assert os.path.exists(saved_path)
            
            with open(saved_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded["passed"] is True


class TestBenchmarkMetrics:
    """Test benchmark metrics dataclass."""

    def test_metrics_creation(self):
        """Test creating benchmark metrics."""
        metrics = BenchmarkMetrics(
            avg_waiting_time=15.0,
            total_vehicles_served=100,
            throughput=120.0,
            avg_queue_length=5.0,
            queue_variance=2.0,
            safety_violations=0,
            violation_rate=0.0,
            emergency_response_time=5.0,
            cumulative_reward=50.0,
            episode_length=3600,
            phase_switches_per_hour=30.0,
            action_consistency=0.7,
            level_of_service="B",
            overall_performance_score=85.0
        )
        
        assert metrics.avg_waiting_time == 15.0
        assert metrics.level_of_service == "B"
        assert metrics.overall_performance_score == 85.0

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = BenchmarkMetrics(
            avg_waiting_time=15.0,
            total_vehicles_served=100,
            throughput=120.0,
            avg_queue_length=5.0,
            queue_variance=2.0,
            safety_violations=0,
            violation_rate=0.0,
            emergency_response_time=5.0,
            cumulative_reward=50.0,
            episode_length=3600,
            phase_switches_per_hour=30.0,
            action_consistency=0.7,
            level_of_service="B",
            overall_performance_score=85.0
        )
        
        d = metrics.to_dict()
        
        assert isinstance(d, dict)
        assert d["avg_waiting_time"] == 15.0
        assert d["level_of_service"] == "B"


class TestBenchmarkSuite:
    """Test benchmark evaluation suite."""

    def test_suite_creation(self):
        """Test benchmark suite is created."""
        suite = BenchmarkSuite()
        assert suite is not None
        assert suite.score_weights is not None

    def test_get_level_of_service(self):
        """Test level of service calculation."""
        suite = BenchmarkSuite()
        
        assert suite._get_level_of_service(5.0) == "A"
        assert suite._get_level_of_service(15.0) == "B"
        assert suite._get_level_of_service(30.0) == "C"
        assert suite._get_level_of_service(50.0) == "D"
        assert suite._get_level_of_service(75.0) == "E"
        assert suite._get_level_of_service(100.0) == "F"

    def test_compute_performance_score(self):
        """Test performance score calculation."""
        suite = BenchmarkSuite()
        
        score = suite._compute_performance_score(
            avg_waiting=10.0,
            throughput=80.0,
            safety_violations=0,
            action_consistency=0.8,
            cumulative_reward=50.0
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_compute_los_distribution(self):
        """Test LOS distribution calculation."""
        suite = BenchmarkSuite()
        
        metrics_list = [
            BenchmarkMetrics(
                avg_waiting_time=5.0, total_vehicles_served=100,
                throughput=120.0, avg_queue_length=5.0, queue_variance=2.0,
                safety_violations=0, violation_rate=0.0, emergency_response_time=5.0,
                cumulative_reward=50.0, episode_length=3600, phase_switches_per_hour=30.0,
                action_consistency=0.7, level_of_service="A", overall_performance_score=85.0
            ),
            BenchmarkMetrics(
                avg_waiting_time=25.0, total_vehicles_served=100,
                throughput=120.0, avg_queue_length=5.0, queue_variance=2.0,
                safety_violations=0, violation_rate=0.0, emergency_response_time=5.0,
                cumulative_reward=50.0, episode_length=3600, phase_switches_per_hour=30.0,
                action_consistency=0.7, level_of_service="C", overall_performance_score=75.0
            )
        ]
        
        distribution = suite._compute_los_distribution(metrics_list)
        
        assert distribution["A"] == 1
        assert distribution["C"] == 1
        assert distribution["B"] == 0

    @patch('gymnasium.Env')
    def test_evaluate_policy(self, mock_env_class):
        """Test policy evaluation."""
        suite = BenchmarkSuite()
        
        mock_env = MagicMock()
        obs = np.ones(16) * 0.5
        mock_env.reset.return_value = (obs, {})
        mock_env.step.return_value = (obs, 1.0, False, False, {"safety_violation": False, "episode_info": {}})
        
        def policy_fn(obs):
            return 0  # Always hold
        
        metrics_list = suite.evaluate_policy(
            env=mock_env,
            policy_fn=policy_fn,
            n_episodes=2,
            deterministic=True
        )
        
        assert len(metrics_list) > 0
        for metrics in metrics_list:
            assert isinstance(metrics, BenchmarkMetrics)

    def test_aggregate_metrics(self):
        """Test metrics aggregation."""
        suite = BenchmarkSuite()
        
        metrics_list = [
            BenchmarkMetrics(
                avg_waiting_time=10.0, total_vehicles_served=100,
                throughput=120.0, avg_queue_length=5.0, queue_variance=2.0,
                safety_violations=0, violation_rate=0.0, emergency_response_time=5.0,
                cumulative_reward=50.0, episode_length=3600, phase_switches_per_hour=30.0,
                action_consistency=0.7, level_of_service="B", overall_performance_score=80.0
            ),
            BenchmarkMetrics(
                avg_waiting_time=15.0, total_vehicles_served=110,
                throughput=130.0, avg_queue_length=6.0, queue_variance=2.5,
                safety_violations=1, violation_rate=0.0003, emergency_response_time=6.0,
                cumulative_reward=55.0, episode_length=3600, phase_switches_per_hour=32.0,
                action_consistency=0.75, level_of_service="B", overall_performance_score=82.0
            )
        ]
        
        aggregated = suite.aggregate_metrics(metrics_list)
        
        assert "n_episodes" in aggregated
        assert aggregated["n_episodes"] == 2
        assert "traffic_efficiency" in aggregated
        assert "safety" in aggregated
        assert "rl_metrics" in aggregated
        assert "performance" in aggregated

    @patch('gymnasium.Env')
    def test_compare_policies(self, mock_env_class):
        """Test comparing multiple policies."""
        suite = BenchmarkSuite()
        
        mock_env = MagicMock()
        obs = np.ones(16) * 0.5
        mock_env.reset.return_value = (obs, {})
        mock_env.step.return_value = (obs, 1.0, False, False, {"safety_violation": False, "episode_info": {}})
        
        policies = {
            "policy_a": lambda obs: 0,
            "policy_b": lambda obs: 1
        }
        
        with patch.object(suite, 'evaluate_policy'):
            with patch.object(suite, 'aggregate_metrics', return_value={"performance": {"overall_score_mean": 80.0}}):
                comparison = suite.compare_policies(
                    policies=policies,
                    env=mock_env,
                    n_episodes=2
                )
        
        assert "policies" in comparison
        assert "ranking" in comparison
        assert "best_policy" in comparison


# Pytest fixtures
@pytest.fixture
def promotion_criteria():
    """Provide promotion criteria instance."""
    return PromotionCriteria()


@pytest.fixture
def benchmark_suite():
    """Provide benchmark suite instance."""
    return BenchmarkSuite()

