"""
Unit tests for traffic prediction baselines.
"""

import pytest
import numpy as np
from backend.app.prediction.baselines import (
    PersistenceBaseline, HistoricalBaselinePredictor, BaselineEnsemble
)
from backend.app.prediction.dataset import TrafficSnapshot


class TestPersistenceBaseline:
    """Test persistence baseline predictor."""

    @pytest.fixture
    def baseline(self):
        return PersistenceBaseline()

    def test_travel_time_persistence(self, baseline):
        """Test that persistence returns current value."""
        current_tt = 25.5
        prediction = baseline.predict_travel_time(current_tt)
        assert prediction == current_tt

    def test_queue_persistence(self, baseline):
        """Test queue persistence."""
        current_queue = 10
        prediction = baseline.predict_queue_length(current_queue)
        assert prediction == current_queue

    def test_speed_persistence(self, baseline):
        """Test speed persistence."""
        current_speed = 12.5
        prediction = baseline.predict_speed(current_speed)
        assert prediction == current_speed

    def test_congestion_persistence(self, baseline):
        """Test congestion level persistence."""
        current_level = "congested"
        prediction = baseline.predict_congestion_level(current_level)
        assert prediction == current_level

    def test_horizon_ignored(self, baseline):
        """Test that horizon parameter doesn't affect persistence."""
        current_tt = 20.0
        pred_short = baseline.predict_travel_time(current_tt, horizon_s=60)
        pred_long = baseline.predict_travel_time(current_tt, horizon_s=600)
        assert pred_short == pred_long == current_tt


class TestHistoricalBaseline:
    """Test historical time-of-day baseline predictor."""

    @pytest.fixture
    def baseline(self):
        return HistoricalBaselinePredictor()

    @pytest.fixture
    def sample_dataset(self):
        """Create synthetic dataset with daily pattern."""
        rows = []

        # Simulate 3 days of data at different times
        for day in range(3):
            for hour in range(24):
                # Morning rush (7-10): slower
                base_tt = 15.0 if 7 <= hour <= 10 else 10.0
                # Evening rush (17-19): even slower
                base_tt = 18.0 if 17 <= hour <= 19 else base_tt

                for minute in range(0, 60, 15):
                    timestamp = day * 86400 + hour * 3600 + minute * 60

                    rows.append({
                        'timestamp_s': float(timestamp),
                        'edge_id': 'edge_1',
                        'mean_speed_ms': 15.0 - (base_tt / 10.0),
                        'vehicle_count': 20,
                        'queue_length': int(base_tt),
                        'occupancy_pct': 50.0 + hour * 2.0,
                        'upstream_flow_veh_h': 1000.0 + hour * 100,
                        'signal_phase': 0,
                        'signal_time_in_phase_s': 0.0,
                        'incident_severity': 0,
                        'congestion_level': 'moderate' if base_tt > 12 else 'free_flow',
                        'travel_time_5min_s': base_tt + np.random.normal(0, 1)
                    })

        return rows

    def test_train_and_predict(self, baseline, sample_dataset):
        """Test training and making predictions."""
        baseline.train_from_dataset(sample_dataset)

        # Make prediction for morning (should be slower)
        morning_time = 7.5 * 3600  # 7:30 AM
        tt_pred, conf = baseline.predict_travel_time('edge_1', morning_time)

        assert tt_pred > 0
        assert 0 < conf <= 1.0

    def test_hour_of_day_effect(self, baseline, sample_dataset):
        """Test that predictions vary by time of day."""
        baseline.train_from_dataset(sample_dataset)

        # Morning rush
        tt_morning, _ = baseline.predict_travel_time('edge_1', 8.0 * 3600)

        # Off-peak
        tt_midday, _ = baseline.predict_travel_time('edge_1', 14.0 * 3600)

        # Evening rush
        tt_evening, _ = baseline.predict_travel_time('edge_1', 18.0 * 3600)

        # Should see variation
        assert not (tt_morning == tt_midday == tt_evening)

    def test_queue_prediction(self, baseline, sample_dataset):
        """Test queue length prediction."""
        baseline.train_from_dataset(sample_dataset)

        queue_pred, conf = baseline.predict_queue_length('edge_1', 9.0 * 3600)

        assert queue_pred >= 0
        assert 0 < conf <= 1.0

    def test_speed_prediction(self, baseline, sample_dataset):
        """Test speed prediction."""
        baseline.train_from_dataset(sample_dataset)

        speed_pred, conf = baseline.predict_speed('edge_1', 8.0 * 3600)

        assert speed_pred > 0
        assert 0 < conf <= 1.0

    def test_congestion_prediction(self, baseline, sample_dataset):
        """Test congestion level prediction."""
        baseline.train_from_dataset(sample_dataset)

        level_pred, conf = baseline.predict_congestion_level('edge_1', 8.0 * 3600)

        assert level_pred in ['free_flow', 'moderate', 'congested', 'gridlock']
        assert 0 < conf <= 1.0


class TestBaselineEnsemble:
    """Test ensemble baseline predictor."""

    @pytest.fixture
    def ensemble(self):
        return BaselineEnsemble()

    @pytest.fixture
    def trained_ensemble(self, ensemble):
        """Create trained ensemble with sample data."""
        rows = []
        for i in range(100):
            rows.append({
                'timestamp_s': float(i * 100),
                'edge_id': 'edge_1',
                'mean_speed_ms': 12.0,
                'vehicle_count': 15,
                'queue_length': 8,
                'occupancy_pct': 40.0,
                'upstream_flow_veh_h': 1200.0,
                'signal_phase': 0,
                'signal_time_in_phase_s': 0.0,
                'incident_severity': 0,
                'congestion_level': 'moderate',
                'travel_time_5min_s': 15.0 + np.random.normal(0, 2)
            })

        ensemble.train(rows)
        return ensemble

    def test_ensemble_prediction(self, trained_ensemble):
        """Test ensemble makes predictions."""
        pred, conf = trained_ensemble.predict_travel_time(
            'edge_1',
            current_travel_time_s=15.0,
            current_sim_time_s=5000.0,
            horizon_s=300
        )

        assert pred > 0
        assert 0 < conf <= 1.0

    def test_ensemble_short_horizon_weights_persistence(self, trained_ensemble):
        """Test that short horizon favors persistence."""
        pred_short, conf_short = trained_ensemble.predict_travel_time(
            'edge_1',
            current_travel_time_s=20.0,
            current_sim_time_s=5000.0,
            horizon_s=30  # Short horizon
        )

        # Should be close to current value (20.0)
        assert abs(pred_short - 20.0) < 5.0

    def test_ensemble_long_horizon_weights_historical(self, trained_ensemble):
        """Test that long horizon may differ from persistence."""
        pred_long, conf_long = trained_ensemble.predict_travel_time(
            'edge_1',
            current_travel_time_s=20.0,
            current_sim_time_s=5000.0,
            horizon_s=600  # Long horizon
        )

        # Should be a blend of persistence and historical
        assert pred_long > 0

    def test_congestion_prediction(self, trained_ensemble):
        """Test ensemble congestion prediction."""
        level, conf = trained_ensemble.predict_congestion_level(
            'edge_1',
            current_level='moderate',
            current_sim_time_s=5000.0,
            horizon_s=300
        )

        assert level in ['free_flow', 'moderate', 'congested', 'gridlock']
        assert 0 < conf <= 1.0


class TestBaselineComparison:
    """Test comparing baseline predictions."""

    def test_persistence_vs_historical_simple(self):
        """Compare persistence and historical on simple dataset."""
        persistence = PersistenceBaseline()
        historical = HistoricalBaselinePredictor()

        # Create simple dataset
        rows = []
        for i in range(50):
            rows.append({
                'timestamp_s': float(i * 100),
                'edge_id': 'edge_1',
                'mean_speed_ms': 12.0,
                'vehicle_count': 10,
                'queue_length': 5,
                'occupancy_pct': 30.0,
                'upstream_flow_veh_h': 1000.0,
                'signal_phase': 0,
                'signal_time_in_phase_s': 0.0,
                'incident_severity': 0,
                'congestion_level': 'free_flow',
                'travel_time_5min_s': 10.0
            })

        historical.train_from_dataset(rows)

        # Test consistency
        current_tt = 10.0
        persistence_pred = persistence.predict_travel_time(current_tt)
        historical_pred, _ = historical.predict_travel_time('edge_1', 5000.0)

        assert persistence_pred == current_tt
        assert historical_pred >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
