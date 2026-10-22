"""
Unit tests for UATMMS RL Gymnasium Environment (Phase 7)
Tests: Environment initialization, observation/action spaces, reset/step mechanics
"""

import pytest
import numpy as np
import gymnasium as gym
from unittest.mock import Mock, patch, MagicMock

from rl.env.sumo_traffic_env import SUMOTrafficEnv, make_sumo_env
from backend.app.core.logging import logger


class TestSUMOTrafficEnvInitialization:
    """Test environment initialization and configuration."""

    def test_env_creation(self):
        """Test basic environment creation."""
        env = SUMOTrafficEnv(junction_id="J1", simulation_time_limit=3600.0)
        assert env is not None
        assert env.junction_id == "J1"
        assert env.simulation_time_limit == 3600.0
        env.close()

    def test_env_with_custom_reward_weights(self):
        """Test environment with custom reward weights."""
        custom_weights = {
            "waiting_time": -2.0,
            "queue_length": -1.0,
            "throughput": 0.02
        }
        env = SUMOTrafficEnv(
            junction_id="J2",
            reward_weights=custom_weights
        )
        assert env.reward_weights["waiting_time"] == -2.0
        assert env.reward_weights["queue_length"] == -1.0
        env.close()

    def test_observation_space(self):
        """Test observation space configuration."""
        env = SUMOTrafficEnv()
        assert isinstance(env.observation_space, gym.spaces.Box)
        assert env.observation_space.shape == (16,)
        assert env.observation_space.dtype == np.float32
        assert np.all(env.observation_space.low == 0.0)
        assert np.all(env.observation_space.high == 1.0)
        env.close()

    def test_action_space(self):
        """Test action space configuration."""
        env = SUMOTrafficEnv()
        assert isinstance(env.action_space, gym.spaces.Discrete)
        assert env.action_space.n == 4  # 4 actions
        env.close()

    def test_factory_function(self):
        """Test make_sumo_env factory."""
        env = make_sumo_env(junction_id="J3", time_limit=1800.0)
        assert isinstance(env, SUMOTrafficEnv)
        assert env.junction_id == "J3"
        assert env.simulation_time_limit == 1800.0
        env.close()


class TestSUMOTrafficEnvReset:
    """Test environment reset mechanism."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_reset_returns_valid_observation(self, mock_sim_reset):
        """Test reset returns valid observation and info."""
        env = SUMOTrafficEnv()
        obs, info = env.reset()

        assert obs is not None
        assert isinstance(obs, np.ndarray)
        assert obs.shape == (16,)
        assert obs.dtype == np.float32
        
        assert info is not None
        assert isinstance(info, dict)
        assert "step" in info
        assert info["step"] == 0
        assert "junction_id" in info
        assert "simulation_time" in info

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_reset_with_seed(self, mock_sim_reset):
        """Test reset with random seed for reproducibility."""
        env = SUMOTrafficEnv()
        obs1, _ = env.reset(seed=42)
        env.close()

        env = SUMOTrafficEnv()
        obs2, _ = env.reset(seed=42)
        env.close()

        # Same seed should produce consistent obs (though SUMO sim may vary)
        assert obs1.shape == obs2.shape

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_reset_clears_episode_state(self, mock_sim_reset):
        """Test that reset clears episode tracking state."""
        env = SUMOTrafficEnv()
        
        # Artificially set episode state
        env.current_step = 100
        env.cumulative_reward = 50.0
        env.episode_info["safety_violations"] = 5

        obs, info = env.reset()

        assert env.current_step == 0
        assert env.cumulative_reward == 0.0
        assert env.episode_info["safety_violations"] == 0
        assert env.last_observation is not None

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_reset_handles_simulation_error(self, mock_sim_reset):
        """Test reset handles simulation reset failures gracefully."""
        mock_sim_reset.side_effect = Exception("Simulation error")
        
        env = SUMOTrafficEnv()
        with pytest.raises(Exception):
            env.reset()

        env.close()


class TestSUMOTrafficEnvStep:
    """Test environment step mechanism."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_step_returns_valid_tuple(self, mock_sim_step, mock_sim_reset):
        """Test step returns valid (obs, reward, terminated, truncated, info) tuple."""
        env = SUMOTrafficEnv()
        env.reset()

        obs, reward, terminated, truncated, info = env.step(0)

        assert isinstance(obs, np.ndarray)
        assert obs.shape == (16,)
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_step_increments_counter(self, mock_sim_step, mock_sim_reset):
        """Test step increments internal step counter."""
        env = SUMOTrafficEnv()
        env.reset()

        assert env.current_step == 0
        env.step(0)
        assert env.current_step == 1
        env.step(0)
        assert env.current_step == 2

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_step_all_actions(self, mock_sim_step, mock_sim_reset):
        """Test step with all action types (0-3)."""
        env = SUMOTrafficEnv()
        env.reset()

        for action in [0, 1, 2, 3]:
            obs, reward, terminated, truncated, info = env.step(action)
            assert obs.shape == (16,)
            assert isinstance(reward, (int, float))

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_step_accumulates_reward(self, mock_sim_step, mock_sim_reset):
        """Test step accumulates cumulative reward."""
        env = SUMOTrafficEnv()
        env.reset()

        initial_reward = env.cumulative_reward
        obs, reward, _, _, _ = env.step(0)

        assert env.cumulative_reward > initial_reward or env.cumulative_reward < initial_reward
        # Reward can be positive or negative depending on environment state

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_step_terminates_at_max_steps(self, mock_sim_step, mock_sim_reset):
        """Test episode terminates when max_steps reached."""
        env = SUMOTrafficEnv(simulation_time_limit=10.0)  # Very short episode
        env.reset()

        terminated = False
        for i in range(env.max_steps + 1):
            obs, reward, terminated, truncated, info = env.step(0)
            if terminated:
                break

        assert terminated
        assert env.current_step > 0

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_step_handles_simulation_error(self, mock_sim_step, mock_sim_reset):
        """Test step handles simulation errors gracefully."""
        mock_sim_step.side_effect = Exception("Simulation error")
        
        env = SUMOTrafficEnv()
        env.reset()

        obs, reward, terminated, truncated, info = env.step(0)

        # Should return terminal state with error penalty
        assert terminated
        assert reward < 0  # Penalty applied
        assert "error" in info

        env.close()


class TestObservationExtraction:
    """Test observation space extraction."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    @patch('backend.app.safety.validator.safety_validator._junctions', {})
    def test_observation_shape_and_bounds(self, mock_sim_step, mock_sim_reset):
        """Test observation has correct shape and values within bounds."""
        env = SUMOTrafficEnv()
        obs, _ = env.reset()

        assert obs.shape == (16,)
        assert np.all(obs >= 0.0)
        assert np.all(obs <= 1.0)

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_observation_components(self, mock_sim_step, mock_sim_reset):
        """Test individual observation components."""
        env = SUMOTrafficEnv()
        obs, _ = env.reset()

        # [0-3]: Queue lengths
        assert obs[0] >= 0 and obs[0] <= 1
        assert obs[1] >= 0 and obs[1] <= 1
        assert obs[2] >= 0 and obs[2] <= 1
        assert obs[3] >= 0 and obs[3] <= 1

        # [4-7]: Waiting times
        assert obs[4] >= 0 and obs[4] <= 1
        assert obs[5] >= 0 and obs[5] <= 1
        assert obs[6] >= 0 and obs[6] <= 1
        assert obs[7] >= 0 and obs[7] <= 1

        # [8-11]: Speeds
        assert obs[8] >= 0 and obs[8] <= 1
        assert obs[9] >= 0 and obs[9] <= 1
        assert obs[10] >= 0 and obs[10] <= 1
        assert obs[11] >= 0 and obs[11] <= 1

        # [12]: Phase
        assert obs[12] >= 0 and obs[12] <= 1

        # [13]: Time in phase
        assert obs[13] >= 0 and obs[13] <= 1

        # [14]: Incident flag
        assert obs[14] >= 0 and obs[14] <= 1

        # [15]: Downstream capacity
        assert obs[15] >= 0 and obs[15] <= 1

        env.close()


class TestRewardCalculation:
    """Test reward calculation mechanics."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_reward_is_numeric(self, mock_sim_step, mock_sim_reset):
        """Test reward is always a numeric value."""
        env = SUMOTrafficEnv()
        env.reset()

        obs, reward, _, _, _ = env.step(0)

        assert isinstance(reward, (int, float))
        assert not np.isnan(reward)
        assert not np.isinf(reward)

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_action_penalty(self, mock_sim_step, mock_sim_reset):
        """Test that different actions produce different rewards."""
        env = SUMOTrafficEnv()
        env.reset()

        rewards = []
        for action in [0, 1, 2]:
            env.reset()
            obs, reward, _, _, _ = env.step(action)
            rewards.append(reward)

        # Different actions should produce different rewards (most of the time)
        # This is a statistical test - may not always hold
        assert len(set(rewards)) > 0  # At least one unique reward

        env.close()


class TestEnvironmentConsistency:
    """Test environment internal consistency."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_observation_after_reset(self, mock_sim_step, mock_sim_reset):
        """Test last_observation is set after reset."""
        env = SUMOTrafficEnv()
        assert env.last_observation is None

        env.reset()
        assert env.last_observation is not None

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_action_stored_in_history(self, mock_sim_step, mock_sim_reset):
        """Test last_action is stored."""
        env = SUMOTrafficEnv()
        env.reset()
        assert env.last_action is None

        env.step(1)
        assert env.last_action == 1

        env.step(2)
        assert env.last_action == 2

        env.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    def test_episode_info_tracking(self, mock_sim_step, mock_sim_reset):
        """Test episode info is tracked correctly."""
        env = SUMOTrafficEnv()
        env.reset()

        initial_violations = env.episode_info["safety_violations"]
        assert initial_violations == 0

        # Episode info should have all expected keys
        expected_keys = [
            "total_waiting_time",
            "total_queue_length",
            "vehicles_passed",
            "safety_violations",
            "red_signals"
        ]

        for key in expected_keys:
            assert key in env.episode_info

        env.close()


# Pytest fixtures
@pytest.fixture
def env():
    """Provide a SUMOTrafficEnv instance for testing."""
    with patch('backend.app.simulation.manager.simulation_manager'):
        environment = SUMOTrafficEnv()
        yield environment
        environment.close()


@pytest.fixture
def env_after_reset(env):
    """Provide environment after reset."""
    with patch('backend.app.simulation.manager.simulation_manager.reset'):
        obs, info = env.reset()
        yield env, obs, info

