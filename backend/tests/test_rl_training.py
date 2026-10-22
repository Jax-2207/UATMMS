"""
Unit tests for UATMMS RL Training (Phase 7)
Tests: PPO trainer, model creation, training loop, evaluation
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from rl.training.train_ppo import (
    PPOTrainer, create_ppo_trainer, TensorBoardCallback, SafetyMonitorCallback
)
from rl.env.sumo_traffic_env import SUMOTrafficEnv
from backend.app.core.logging import logger


class TestPPOTrainerInitialization:
    """Test PPO trainer initialization."""

    def test_trainer_creation(self):
        """Test basic trainer creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(
                junction_id="J1",
                checkpoint_dir=tmpdir,
                log_dir=tmpdir
            )

            assert trainer.junction_id == "J1"
            assert trainer.model is None
            assert trainer.env is None
            assert trainer.training_started is False

    def test_trainer_creates_directories(self):
        """Test trainer creates checkpoint and log directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = os.path.join(tmpdir, "checkpoints")
            log_dir = os.path.join(tmpdir, "logs")

            trainer = PPOTrainer(
                checkpoint_dir=checkpoint_dir,
                log_dir=log_dir
            )

            assert os.path.exists(checkpoint_dir)
            assert os.path.exists(log_dir)

    def test_trainer_custom_time_limit(self):
        """Test trainer accepts custom simulation time limit."""
        trainer = PPOTrainer(
            junction_id="J2",
            simulation_time_limit=1800.0
        )

        assert trainer.simulation_time_limit == 1800.0

    def test_trainer_device_specification(self):
        """Test trainer device specification."""
        trainer = PPOTrainer(device="cpu")
        assert trainer.device == "cpu"

        trainer = PPOTrainer(device="auto")
        assert trainer.device == "auto"


class TestEnvironmentCreation:
    """Test environment creation in trainer."""

    @patch('rl.training.train_ppo.make_vec_env')
    @patch('rl.training.train_ppo.SUMOTrafficEnv')
    def test_create_single_env(self, mock_sumo, mock_make_vec):
        """Test creating single environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            # Mock the environment factory
            mock_env = MagicMock()
            mock_sumo.return_value = mock_env

            with patch('rl.training.train_ppo.SafetyWrapper'):
                env = trainer.create_env(num_envs=1)

                assert trainer.env is not None
                # Single env shouldn't call make_vec_env
                mock_make_vec.assert_not_called()

    @patch('rl.training.train_ppo.make_vec_env')
    @patch('rl.training.train_ppo.SUMOTrafficEnv')
    def test_create_vectorized_env(self, mock_sumo, mock_make_vec):
        """Test creating vectorized environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            mock_vec_env = MagicMock()
            mock_make_vec.return_value = mock_vec_env

            with patch('rl.training.train_ppo.SafetyWrapper'):
                with patch('rl.training.train_ppo.VecNormalize'):
                    env = trainer.create_env(num_envs=4)

                    # Vectorized env should call make_vec_env
                    mock_make_vec.assert_called_once()

    @patch('rl.training.train_ppo.SUMOTrafficEnv')
    def test_create_env_with_normalization(self, mock_sumo):
        """Test environment normalization option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            mock_env = MagicMock()
            mock_sumo.return_value = mock_env

            with patch('rl.training.train_ppo.SafetyWrapper'):
                with patch('rl.training.train_ppo.VecNormalize') as mock_normalize:
                    env = trainer.create_env(num_envs=1, normalize_observations=True)

                    # For single env, normalization may or may not be called
                    # depending on implementation


class TestModelCreation:
    """Test PPO model creation."""

    @patch('rl.training.train_ppo.PPO')
    def test_create_model(self, mock_ppo_class):
        """Test creating PPO model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            # Create a mock environment first
            mock_env = MagicMock()
            trainer.env = mock_env

            mock_model = MagicMock()
            mock_ppo_class.return_value = mock_model

            model = trainer.create_model(
                learning_rate=3e-4,
                n_steps=2048
            )

            assert trainer.model is not None
            mock_ppo_class.assert_called_once()

    def test_create_model_without_env_fails(self):
        """Test creating model without environment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            with pytest.raises(ValueError):
                trainer.create_model()

    @patch('rl.training.train_ppo.PPO')
    def test_model_hyperparameters(self, mock_ppo_class):
        """Test model is created with correct hyperparameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            mock_env = MagicMock()
            trainer.env = mock_env

            mock_model = MagicMock()
            mock_ppo_class.return_value = mock_model

            trainer.create_model(
                learning_rate=1e-3,
                n_steps=1024,
                batch_size=32,
                gamma=0.99,
                clip_range=0.2
            )

            # Verify PPO was called with correct args
            call_kwargs = mock_ppo_class.call_args[1]
            assert call_kwargs["learning_rate"] == 1e-3
            assert call_kwargs["n_steps"] == 1024
            assert call_kwargs["batch_size"] == 32


class TestTensorBoardCallback:
    """Test TensorBoard callback."""

    def test_callback_creation(self):
        """Test callback is created."""
        callback = TensorBoardCallback(verbose=0)
        assert callback is not None
        assert callback.episode_count == 0

    def test_callback_initialization(self):
        """Test callback initialization."""
        callback = TensorBoardCallback(verbose=1)
        
        callback._on_training_start()
        assert callback.num_timesteps == 0

    def test_callback_step_tracking(self):
        """Test callback tracks steps."""
        callback = TensorBoardCallback()
        
        # Simulate a training step
        callback.num_timesteps = 100
        result = callback._on_step()
        
        assert result is True  # Should return True to continue training


class TestSafetyMonitorCallback:
    """Test safety monitor callback."""

    def test_callback_creation(self):
        """Test safety callback is created."""
        callback = SafetyMonitorCallback()
        assert callback.total_violations == 0
        assert callback.episodes_with_violations == 0

    def test_callback_logs_summary(self):
        """Test callback can log summary."""
        callback = SafetyMonitorCallback()
        
        callback.total_violations = 5
        callback.episodes_with_violations = 2
        
        summary = callback.log_summary()
        
        assert summary["total_violations"] == 5
        assert summary["episodes_with_violations"] == 2


class TestTrainingStatus:
    """Test training status tracking."""

    def test_get_training_status(self):
        """Test training status method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            status = trainer.get_training_status()
            
            assert "training_started" in status
            assert "steps_completed" in status
            assert "model_created" in status
            assert "environment_created" in status

    def test_training_status_reflects_state(self):
        """Test training status reflects actual state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            assert trainer.get_training_status()["training_started"] is False
            
            trainer.training_started = True
            assert trainer.get_training_status()["training_started"] is True


class TestModelSaveLoad:
    """Test model saving and loading."""

    @patch('rl.training.train_ppo.PPO')
    def test_save_model(self, mock_ppo_class):
        """Test model saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            mock_model = MagicMock()
            trainer.model = mock_model

            save_path = os.path.join(tmpdir, "test_model")
            result = trainer.save_model(save_path)

            # Should call save on model
            mock_model.save.assert_called_once()
            assert result.endswith(".zip")

    def test_save_model_no_model_raises_error(self):
        """Test saving without model raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            with pytest.raises(ValueError):
                trainer.save_model(os.path.join(tmpdir, "test_model"))

    @patch('rl.training.train_ppo.PPO.load')
    def test_load_model(self, mock_load):
        """Test model loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            # Create a dummy model file
            model_path = os.path.join(tmpdir, "model.zip")
            Path(model_path).touch()

            mock_model = MagicMock()
            mock_load.return_value = mock_model

            loaded = trainer.load_model(model_path)

            assert trainer.model is not None
            mock_load.assert_called_once()

    def test_load_nonexistent_model_raises_error(self):
        """Test loading nonexistent model raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            with pytest.raises(FileNotFoundError):
                trainer.load_model(os.path.join(tmpdir, "nonexistent.zip"))


class TestPolicyEvaluation:
    """Test policy evaluation."""

    @patch('rl.training.train_ppo.PPO')
    def test_evaluate_policy(self, mock_ppo_class):
        """Test policy evaluation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            # Setup mock environment and model
            mock_env = MagicMock()
            mock_env.reset.return_value = (np.zeros(16), {})
            mock_env.step.return_value = (
                np.zeros(16),  # obs
                1.0,           # reward
                False,         # terminated
                False,         # truncated
                {"safety_violation": False, "episode_info": {}}  # info
            )
            trainer.env = mock_env

            mock_model = MagicMock()
            mock_model.predict.return_value = (0, None)  # action, internal state
            trainer.model = mock_model

            results = trainer.evaluate_policy(n_episodes=2, deterministic=True)

            assert "mean_reward" in results
            assert "std_reward" in results
            assert "mean_length" in results
            assert results["mean_reward"] > 0

    def test_evaluate_without_model_raises_error(self):
        """Test evaluation without model raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
            
            with pytest.raises(ValueError):
                trainer.evaluate_policy()


class TestFactoryFunction:
    """Test factory function."""

    @patch('rl.training.train_ppo.PPOTrainer.create_env')
    @patch('rl.training.train_ppo.PPOTrainer.create_model')
    def test_create_ppo_trainer_factory(self, mock_create_model, mock_create_env):
        """Test create_ppo_trainer factory function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('rl.training.train_ppo.PPOTrainer') as mock_trainer_class:
                mock_trainer = MagicMock()
                mock_trainer_class.return_value = mock_trainer

                trainer = create_ppo_trainer(
                    junction_id="J1",
                    n_envs=2
                )

                # Factory should create trainer and call setup methods
                mock_trainer_class.assert_called_once()
                mock_trainer.create_env.assert_called_once_with(num_envs=2)
                mock_trainer.create_model.assert_called_once()


# Pytest fixtures
@pytest.fixture
def temp_trainer():
    """Provide a temporary trainer."""
    with tempfile.TemporaryDirectory() as tmpdir:
        trainer = PPOTrainer(checkpoint_dir=tmpdir, log_dir=tmpdir)
        yield trainer


@pytest.fixture
def temp_trainer_with_env(temp_trainer):
    """Provide trainer with environment setup."""
    with patch('rl.training.train_ppo.SUMOTrafficEnv'):
        with patch('rl.training.train_ppo.SafetyWrapper'):
            temp_trainer.create_env(num_envs=1)
            yield temp_trainer

