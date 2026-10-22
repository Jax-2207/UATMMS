"""
UATMMS Prediction Inference Interface
Serves traffic predictions using trained models with fallback to baselines.
"""

from typing import Dict, Optional, Tuple
from backend.app.prediction.model import (
    travel_time_predictor, congestion_classifier
)
from backend.app.prediction.baselines import (
    baseline_ensemble
)
from backend.app.core.logging import logger


class PredictionEngine:
    """
    Unified interface for traffic predictions.
    Routes requests to trained models or baselines with intelligent fallback.
    """

    def __init__(self):
        self.use_xgboost = False  # Set to True once model is trained
        self.fallback_to_baseline = True

    def predict_travel_time(
        self,
        edge_id: str,
        current_condition: Dict,
        horizon_s: int = 300
    ) -> Tuple[float, float, str]:
        """
        Predict travel time for an edge.

        Args:
            edge_id: Edge to predict for
            current_condition: Current state dictionary with:
                - mean_speed_ms: current speed
                - travel_time_5min_s: observed travel time
                - queue_length: current queue
                - vehicle_count: vehicles on edge
                - occupancy_pct: edge occupancy
                - upstream_flow_veh_h: incoming flow
                - signal_phase: current phase
                - signal_time_in_phase_s: time in phase
                - incident_severity: current incidents
                - timestamp_s: current simulation time
            horizon_s: Prediction horizon in seconds

        Returns:
            (predicted_travel_time_s, confidence, model_used)
        """
        # Try XGBoost if trained
        if self.use_xgboost and travel_time_predictor.is_trained:
            try:
                pred, conf = travel_time_predictor.predict(current_condition)
                if conf > 0.5:  # Sufficient confidence
                    logger.debug(f"[PredictionEngine] XGBoost prediction for {edge_id}: {pred:.1f}s (conf={conf:.2f})")
                    return pred, conf, "xgboost"
            except Exception as e:
                logger.warning(f"[PredictionEngine] XGBoost prediction failed: {e}")

        # Fallback to baseline ensemble
        if self.fallback_to_baseline:
            try:
                pred, conf = baseline_ensemble.predict_travel_time(
                    edge_id,
                    current_condition.get('travel_time_5min_s', 20.0),
                    current_condition.get('timestamp_s', 0.0),
                    horizon_s
                )
                logger.debug(f"[PredictionEngine] Baseline prediction for {edge_id}: {pred:.1f}s (conf={conf:.2f})")
                return pred, conf, "baseline"
            except Exception as e:
                logger.error(f"[PredictionEngine] Baseline prediction failed: {e}")

        # Final fallback
        return 20.0, 0.5, "fallback"

    def predict_queue_length(
        self,
        edge_id: str,
        current_condition: Dict,
        horizon_s: int = 300
    ) -> Tuple[int, float, str]:
        """
        Predict queue length.

        Returns:
            (predicted_queue_length, confidence, model_used)
        """
        # Currently only baseline available for queue prediction
        try:
            pred, conf = baseline_ensemble.historical.predict_queue_length(
                edge_id,
                current_condition.get('timestamp_s', 0.0),
                horizon_s
            )
            return pred, conf, "baseline"
        except Exception as e:
            logger.error(f"[PredictionEngine] Queue prediction failed: {e}")
            return 5, 0.5, "fallback"

    def predict_speed(
        self,
        edge_id: str,
        current_condition: Dict,
        horizon_s: int = 300
    ) -> Tuple[float, float, str]:
        """
        Predict average speed on edge.

        Returns:
            (predicted_speed_m/s, confidence, model_used)
        """
        try:
            pred, conf = baseline_ensemble.historical.predict_speed(
                edge_id,
                current_condition.get('timestamp_s', 0.0),
                horizon_s
            )
            return pred, conf, "baseline"
        except Exception as e:
            logger.error(f"[PredictionEngine] Speed prediction failed: {e}")
            return 15.0, 0.5, "fallback"

    def predict_congestion_level(
        self,
        edge_id: str,
        current_condition: Dict,
        horizon_s: int = 300
    ) -> Tuple[str, float, str]:
        """
        Predict congestion level (categorical).

        Args:
            edge_id: Edge to predict for
            current_condition: Current state dictionary
            horizon_s: Prediction horizon in seconds

        Returns:
            (predicted_level, confidence, model_used)
            where predicted_level ∈ {free_flow, moderate, congested, gridlock}
        """
        # Try XGBoost if trained
        if self.use_xgboost and congestion_classifier.is_trained:
            try:
                pred, conf = congestion_classifier.predict(current_condition)
                if conf > 0.5:
                    logger.debug(f"[PredictionEngine] XGBoost congestion for {edge_id}: {pred} (conf={conf:.2f})")
                    return pred, conf, "xgboost"
            except Exception as e:
                logger.warning(f"[PredictionEngine] XGBoost congestion failed: {e}")

        # Fallback to baseline
        if self.fallback_to_baseline:
            try:
                pred, conf = baseline_ensemble.predict_congestion_level(
                    edge_id,
                    current_condition.get('congestion_level', 'free_flow'),
                    current_condition.get('timestamp_s', 0.0),
                    horizon_s
                )
                logger.debug(f"[PredictionEngine] Baseline congestion for {edge_id}: {pred} (conf={conf:.2f})")
                return pred, conf, "baseline"
            except Exception as e:
                logger.error(f"[PredictionEngine] Baseline congestion failed: {e}")

        # Final fallback
        return 'free_flow', 0.5, "fallback"

    def enable_xgboost(self):
        """Activate XGBoost models for predictions."""
        if travel_time_predictor.is_trained or congestion_classifier.is_trained:
            self.use_xgboost = True
            logger.info("[PredictionEngine] XGBoost models activated")
        else:
            logger.warning("[PredictionEngine] XGBoost models not trained yet")

    def get_model_status(self) -> Dict:
        """Get status of available models."""
        return {
            "xgboost_travel_time": travel_time_predictor.is_trained,
            "xgboost_congestion": congestion_classifier.is_trained,
            "baseline_ensemble": baseline_ensemble.historical.historical_data is not None,
            "currently_using_xgboost": self.use_xgboost,
            "fallback_enabled": self.fallback_to_baseline
        }


# Global instance
prediction_engine = PredictionEngine()
