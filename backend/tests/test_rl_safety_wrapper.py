"""
Unit tests for UATMMS RL Safety Wrapper (Phase 7)
Tests: Action validation, safety enforcement, violation detection
"""

import pytest
import numpy as np
import gymnasium as gym
from unittest.mock import Mock, patch, MagicMock

from rl.env.safety_wrapper import SafetyWrapper, wrap_with_safety
from rl.env.sumo_traffic_env import SUMOTrafficEnv
from backend.app.core.logging import logger


class TestSafetyWrapperInitialization:
    """Test safety wrapper initialization."""

    def test_wrapper_creation(self):
        """Test basic wrapper creation."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            assert wrapper is not None
            assert wrapper.env == base_env
            wrapper.close()

    def test_wrapper_preserves_spaces(self):
        """Test wrapper preserves observation and action spaces."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)

            assert wrapper.observation_space == base_env.observation_space
            assert wrapper.action_space == base_env.action_space

            wrapper.close()

    def test_wrapper_with_custom_config(self):
        """Test wrapper with custom configuration."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(
                base_env,
                action_masking=False,
                penalty_on_violation=-50.0,
                hard_reject_critical=False
            )

            assert wrapper.action_masking is False
            assert wrapper.penalty_on_violation == -50.0
            assert wrapper.hard_reject_critical is False

            wrapper.close()

    def test_wrapper_factory(self):
        """Test wrap_with_safety factory function."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = wrap_with_safety(base_env, penalty_on_violation=-75.0)

            assert isinstance(wrapper, SafetyWrapper)
            assert wrapper.penalty_on_violation == -75.0

            wrapper.close()


class TestActionValidation:
    """Test action validation logic."""

    def test_validate_invalid_action_index(self):
        """Test validation rejects invalid action indices."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            is_safe, rewritten, reason = wrapper._validate_action(-1)
            assert is_safe is False

            is_safe, rewritten, reason = wrapper._validate_action(5)
            assert is_safe is False

            wrapper.close()


class TestSafetyWrapperStep:
    """Test wrapped step method."""

    @pytest.mark.skip(reason="Requires full simulator integration")
    def test_safe_action_returns_valid_tuple(self):
        """Test safe actions return valid step tuple."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            obs, reward, terminated, truncated, info = wrapper.step(0)

            assert isinstance(obs, np.ndarray)
            assert isinstance(reward, (int, float))
            assert isinstance(terminated, bool)
            assert isinstance(truncated, bool)
            assert isinstance(info, dict)

            wrapper.close()


class TestValidActionsMethod:
    """Test get_valid_actions_mask method."""

    @pytest.mark.skip(reason="Requires full simulator integration")
    def test_mask_shape_and_type(self):
        """Test valid actions mask has correct shape and type."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            mask = wrapper.get_valid_actions_mask()

            assert isinstance(mask, np.ndarray)
            assert mask.shape == (4,)
            assert mask.dtype == bool

            wrapper.close()

    @pytest.mark.skip(reason="Requires full simulator integration")
    def test_mask_has_valid_actions(self):
        """Test mask allows at least some actions."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            mask = wrapper.get_valid_actions_mask()

            # Should allow at least 1 action
            assert np.sum(mask) >= 1

            wrapper.close()

    @pytest.mark.skip(reason="Requires full simulator integration")
    def test_mask_consistency_across_calls(self):
        """Test mask is consistent across multiple calls."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            mask1 = wrapper.get_valid_actions_mask()
            mask2 = wrapper.get_valid_actions_mask()

            assert np.array_equal(mask1, mask2)

            wrapper.close()


class TestResetBehavior:
    """Test reset behavior with safety wrapper."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_reset_clears_violation_counter(self, mock_sim_reset):
        """Test reset clears episode violation counter."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            # Artificially increment counter
            wrapper.violations_in_episode = 10

            obs, info = wrapper.reset()

            assert wrapper.violations_in_episode == 0

            wrapper.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_reset_returns_valid_tuple(self, mock_sim_reset):
        """Test reset returns valid observation and info."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)

            obs, info = wrapper.reset()

            assert isinstance(obs, np.ndarray)
            assert isinstance(info, dict)

            wrapper.close()


class TestEpisodeSummary:
    """Test episode summary method."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_episode_summary_structure(self, mock_sim_reset):
        """Test episode summary has correct structure."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            summary = wrapper.get_episode_summary()

            assert "violations_in_episode" in summary
            assert "total_violations" in summary
            assert "episode_safe" in summary

            assert isinstance(summary["violations_in_episode"], int)
            assert isinstance(summary["total_violations"], int)
            assert isinstance(summary["episode_safe"], bool)

            wrapper.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_episode_safe_when_no_violations(self, mock_sim_reset):
        """Test episode_safe is True when no violations."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            wrapper.violations_in_episode = 0
            summary = wrapper.get_episode_summary()

            assert summary["episode_safe"] is True

            wrapper.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    def test_episode_unsafe_when_violations_exist(self, mock_sim_reset):
        """Test episode_safe is False when violations exist."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env)
            wrapper.env.reset()

            wrapper.violations_in_episode = 3
            summary = wrapper.get_episode_summary()

            assert summary["episode_safe"] is False

            wrapper.close()


class TestCriticalViolationHandling:
    """Test handling of critical violations."""

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    @patch('backend.app.safety.validator.safety_validator._junctions', {})
    def test_critical_violation_terminates_episode(self, mock_sim_step, mock_sim_reset):
        """Test critical violation terminates episode when hard_reject=True."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env, hard_reject_critical=True)
            wrapper.env.reset()

            # Mock _validate_action to return critical violation
            with patch.object(wrapper, '_validate_action', 
                            return_value=(False, 0, "CRITICAL")):
                with patch.object(base_env, 'step', return_value=(
                    np.zeros(16), 0.0, False, False, {"episode_info": {}}
                )):
                    obs, reward, terminated, truncated, info = wrapper.step(5)

                    # Episode should terminate
                    assert terminated is True

            wrapper.close()

    @patch('backend.app.simulation.manager.simulation_manager.reset')
    @patch('backend.app.simulation.manager.simulation_manager.step')
    @patch('backend.app.safety.validator.safety_validator._junctions', {})
    def test_critical_violation_info(self, mock_sim_step, mock_sim_reset):
        """Test critical violation info is included in return."""
        with patch('backend.app.simulation.manager.simulation_manager'):
            base_env = SUMOTrafficEnv()
            wrapper = SafetyWrapper(base_env, hard_reject_critical=True)
            wrapper.env.reset()

            with patch.object(wrapper, '_validate_action',
                            return_value=(False, 0, "CRITICAL")):
                with patch.object(base_env, 'step', return_value=(
                    np.zeros(16), 0.0, False, False, {"episode_info": {}}
                )):
                    obs, reward, terminated, truncated, info = wrapper.step(5)

                    assert info["safety_violation"] is True
                    assert info["violation_reason"] == "CRITICAL"

            wrapper.close()


# Pytest fixtures
@pytest.fixture
def wrapped_env():
    """Provide a wrapped environment."""
    with patch('backend.app.simulation.manager.simulation_manager'):
        base_env = SUMOTrafficEnv()
        wrapped = SafetyWrapper(base_env)
        yield wrapped
        wrapped.close()


@pytest.fixture
def wrapped_env_after_reset(wrapped_env):
    """Provide wrapped environment after reset."""
    with patch('backend.app.simulation.manager.simulation_manager.reset'):
        obs, info = wrapped_env.reset()
        yield wrapped_env, obs, info

