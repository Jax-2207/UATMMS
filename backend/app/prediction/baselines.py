"""
UATMMS Traffic Prediction Baselines
Simple baseline predictors for comparing ML model performance.
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import numpy as np
from backend.app.core.logging import logger


class PersistenceBaseline:
    """
    Persistence baseline: predict next value equals current value.
    Useful for short horizons where conditions don't change much.
    """

    def predict_travel_time(self, current_travel_time_s: float, horizon_s: int = 300) -> float:
        """
        Predict travel time using persistence.

        Args:
            current_travel_time_s: Current observed travel time
            horizon_s: Prediction horizon (unused in persistence)

        Returns:
            Predicted travel time (same as current)
        """
        return current_travel_time_s

    def predict_queue_length(self, current_queue: int, horizon_s: int = 300) -> int:
        """Predict queue length using persistence."""
        return current_queue

    def predict_speed(self, current_speed_ms: float, horizon_s: int = 300) -> float:
        """Predict speed using persistence."""
        return current_speed_ms

    def predict_congestion_level(self, current_level: str, horizon_s: int = 300) -> str:
        """Predict congestion level using persistence."""
        return current_level


class HistoricalBaselinePredictor:
    """
    Historical baseline: predict using time-of-day averages.
    Accounts for recurring daily patterns (morning rush, peak, evening, off-peak).
    """

    def __init__(self):
        self.time_of_day_stats: Dict[int, Dict] = defaultdict(dict)  # hour -> {edge_id: stats}
        self.historical_data: List[Dict] = []

    def train_from_dataset(self, dataset_rows: List[Dict]):
        """
        Train historical baseline from collected data.

        Args:
            dataset_rows: List of TrafficSnapshot dictionaries from dataset.load_dataset()
        """
        self.historical_data = dataset_rows

        # Aggregate by hour of day
        for row in dataset_rows:
            timestamp_s = row['timestamp_s']
            hour = int((timestamp_s % 86400) / 3600)  # Hour of day (0-23)
            edge_id = row['edge_id']

            if edge_id not in self.time_of_day_stats[hour]:
                self.time_of_day_stats[hour][edge_id] = {
                    'travel_times': [],
                    'queue_lengths': [],
                    'speeds': [],
                    'congestion_levels': defaultdict(int)
                }

            stats = self.time_of_day_stats[hour][edge_id]
            stats['travel_times'].append(row['travel_time_5min_s'])
            stats['queue_lengths'].append(row['queue_length'])
            stats['speeds'].append(row['mean_speed_ms'])
            stats['congestion_levels'][row['congestion_level']] += 1

        # Compute averages
        for hour in self.time_of_day_stats:
            for edge_id in self.time_of_day_stats[hour]:
                stats = self.time_of_day_stats[hour][edge_id]

                if stats['travel_times']:
                    stats['avg_travel_time'] = np.mean(stats['travel_times'])
                    stats['std_travel_time'] = np.std(stats['travel_times'])
                else:
                    stats['avg_travel_time'] = 0.0
                    stats['std_travel_time'] = 0.0

                if stats['queue_lengths']:
                    stats['avg_queue_length'] = int(np.mean(stats['queue_lengths']))
                else:
                    stats['avg_queue_length'] = 0

                if stats['speeds']:
                    stats['avg_speed'] = np.mean(stats['speeds'])
                else:
                    stats['avg_speed'] = 15.0

                # Most common congestion level
                if stats['congestion_levels']:
                    stats['most_common_congestion'] = max(
                        stats['congestion_levels'].items(),
                        key=lambda x: x[1]
                    )[0]
                else:
                    stats['most_common_congestion'] = 'free_flow'

        logger.info(f"[HistoricalBaseline] Trained on {len(dataset_rows)} records")

    def predict_travel_time(
        self,
        edge_id: str,
        current_sim_time_s: float,
        horizon_s: int = 300
    ) -> Tuple[float, float]:
        """
        Predict travel time using historical time-of-day average.

        Args:
            edge_id: Edge to predict for
            current_sim_time_s: Current simulation time
            horizon_s: Prediction horizon

        Returns:
            (predicted_travel_time, confidence)
        """
        # Extract hour of day
        hour = int((current_sim_time_s % 86400) / 3600)

        if hour in self.time_of_day_stats and edge_id in self.time_of_day_stats[hour]:
            stats = self.time_of_day_stats[hour][edge_id]
            prediction = stats['avg_travel_time']
            # Confidence based on std deviation (lower std = higher confidence)
            confidence = 1.0 / (1.0 + stats['std_travel_time'] / max(prediction, 1.0))
            return prediction, confidence
        else:
            # Fallback: assume 20 seconds average
            return 20.0, 0.5

    def predict_queue_length(
        self,
        edge_id: str,
        current_sim_time_s: float,
        horizon_s: int = 300
    ) -> Tuple[int, float]:
        """Predict queue length using historical average."""
        hour = int((current_sim_time_s % 86400) / 3600)

        if hour in self.time_of_day_stats and edge_id in self.time_of_day_stats[hour]:
            stats = self.time_of_day_stats[hour][edge_id]
            return stats['avg_queue_length'], 0.7
        else:
            return 5, 0.5

    def predict_speed(
        self,
        edge_id: str,
        current_sim_time_s: float,
        horizon_s: int = 300
    ) -> Tuple[float, float]:
        """Predict speed using historical average."""
        hour = int((current_sim_time_s % 86400) / 3600)

        if hour in self.time_of_day_stats and edge_id in self.time_of_day_stats[hour]:
            stats = self.time_of_day_stats[hour][edge_id]
            return stats['avg_speed'], 0.7
        else:
            return 15.0, 0.5

    def predict_congestion_level(
        self,
        edge_id: str,
        current_sim_time_s: float,
        horizon_s: int = 300
    ) -> Tuple[str, float]:
        """Predict congestion level using historical mode."""
        hour = int((current_sim_time_s % 86400) / 3600)

        if hour in self.time_of_day_stats and edge_id in self.time_of_day_stats[hour]:
            stats = self.time_of_day_stats[hour][edge_id]
            return stats['most_common_congestion'], 0.6
        else:
            return 'free_flow', 0.5


class BaselineEnsemble:
    """
    Ensemble of baseline predictors.
    Combines persistence and historical baselines for robust prediction.
    """

    def __init__(self):
        self.persistence = PersistenceBaseline()
        self.historical = HistoricalBaselinePredictor()

    def train(self, dataset_rows: List[Dict]):
        """Train historical baseline."""
        self.historical.train_from_dataset(dataset_rows)

    def predict_travel_time(
        self,
        edge_id: str,
        current_travel_time_s: float,
        current_sim_time_s: float,
        horizon_s: int = 300
    ) -> Tuple[float, float]:
        """
        Predict travel time using ensemble (average of baselines).

        Args:
            edge_id: Edge to predict for
            current_travel_time_s: Current observed travel time
            current_sim_time_s: Current simulation time
            horizon_s: Prediction horizon

        Returns:
            (predicted_travel_time, confidence)
        """
        persistence_pred = self.persistence.predict_travel_time(current_travel_time_s, horizon_s)
        historical_pred, historical_conf = self.historical.predict_travel_time(
            edge_id, current_sim_time_s, horizon_s
        )

        # For short horizon (<60s), weight persistence higher
        if horizon_s < 60:
            weight_persistence = 0.7
        else:
            weight_persistence = 0.5

        weight_historical = 1.0 - weight_persistence

        prediction = (weight_persistence * persistence_pred +
                     weight_historical * historical_pred)
        confidence = weight_historical * historical_conf + weight_persistence * 0.8

        return prediction, confidence

    def predict_congestion_level(
        self,
        edge_id: str,
        current_level: str,
        current_sim_time_s: float,
        horizon_s: int = 300
    ) -> Tuple[str, float]:
        """
        Predict congestion level using ensemble.

        For categorical predictions, use majority vote.
        """
        persistence_pred = self.persistence.predict_congestion_level(current_level, horizon_s)
        historical_pred, historical_conf = self.historical.predict_congestion_level(
            edge_id, current_sim_time_s, horizon_s
        )

        # Use historical for longer horizons, persistence for short
        if horizon_s < 60:
            return persistence_pred, 0.7
        else:
            return historical_pred, historical_conf


# Global instances
persistence_baseline = PersistenceBaseline()
historical_baseline = HistoricalBaselinePredictor()
baseline_ensemble = BaselineEnsemble()
