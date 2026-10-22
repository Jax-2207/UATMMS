"""
UATMMS XGBoost Prediction Models
Gradient-boosted models for traffic prediction.
"""

from typing import Optional, Tuple, Dict, List
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from backend.app.core.logging import logger


class TravelTimePredictor:
    """XGBoost model for travel time prediction."""

    def __init__(self, model_name: str = "travel_time_predictor"):
        self.model_name = model_name
        self.model: Optional[xgb.XGBRegressor] = None
        self.feature_columns: List[str] = []
        self.is_trained = False

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build feature matrix from raw dataset.

        Features include:
        - Recent history: lagged speed, queue, occupancy
        - Context: time of day, day of week, signal phase
        - Upstream state: flow, incident severity
        """
        df = df.copy()

        # Time features
        df['hour_of_day'] = (df['timestamp_s'] % 86400) / 3600
        df['day_of_week'] = ((df['timestamp_s'] // 86400) + 3) % 7  # 0=Monday
        df['is_peak_hour'] = ((df['hour_of_day'] >= 7) & (df['hour_of_day'] <= 10) |
                              (df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 19)).astype(int)

        # Current conditions
        df['speed_normalized'] = df['mean_speed_ms'] / 20.0  # Normalize to ~1.0 at 20 m/s
        df['occupancy_sq'] = df['occupancy_pct'] ** 2  # Quadratic term for non-linearity
        df['queue_normalized'] = df['queue_length'] / 20.0  # Normalize

        # Signal phase features
        df['is_green'] = (df['signal_phase'] % 2).astype(int)  # Simplified: even=red, odd=green
        df['phase_progress'] = df['signal_time_in_phase_s'] / 60.0  # Normalize to 0-1 (assuming ~60s max)

        # Incident features
        df['has_incident'] = (df['incident_severity'] > 0).astype(int)
        df['incident_severity_norm'] = df['incident_severity'] / 5.0

        # Upstream state
        df['flow_normalized'] = df['upstream_flow_veh_h'] / 2000.0  # Normalize to ~1.0 at 2000 veh/h

        # Select features for model
        self.feature_columns = [
            'mean_speed_ms', 'vehicle_count', 'queue_length', 'occupancy_pct',
            'upstream_flow_veh_h', 'signal_phase', 'signal_time_in_phase_s',
            'incident_severity', 'hour_of_day', 'day_of_week', 'is_peak_hour',
            'speed_normalized', 'occupancy_sq', 'queue_normalized',
            'is_green', 'phase_progress', 'has_incident', 'incident_severity_norm',
            'flow_normalized'
        ]

        return df

    def train(
        self,
        dataset_rows: List[Dict],
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[float, float]:
        """
        Train XGBoost model for travel time prediction.

        Args:
            dataset_rows: List of TrafficSnapshot dictionaries
            test_size: Fraction for test set
            random_state: Random seed for reproducibility

        Returns:
            (mae, rmse) on test set
        """
        # Convert to DataFrame
        df = pd.DataFrame(dataset_rows)

        # Build features
        df = self.build_features(df)

        # Extract target and features
        X = df[self.feature_columns]
        y = df['travel_time_5min_s']

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Train XGBoost
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            objective='reg:squarederror',
            verbosity=0
        )

        self.model.fit(X_train, y_train, verbose=False)
        self.is_trained = True

        # Evaluate
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        logger.info(
            f"[TravelTimePredictor] Trained on {len(X_train)} samples. "
            f"Test MAE={mae:.2f}s, RMSE={rmse:.2f}s"
        )

        return mae, rmse

    def predict(self, edge_data: Dict) -> Tuple[float, float]:
        """
        Predict travel time for an edge.

        Args:
            edge_data: Dictionary with edge attributes

        Returns:
            (predicted_travel_time_s, confidence)
        """
        if not self.is_trained or self.model is None:
            return 20.0, 0.0  # Fallback

        try:
            # Build feature vector
            feature_vector = {}
            for col in self.feature_columns:
                if col in edge_data:
                    feature_vector[col] = edge_data[col]
                else:
                    feature_vector[col] = 0.0

            df = pd.DataFrame([feature_vector])
            prediction = self.model.predict(df)[0]

            # Confidence based on prediction magnitude (placeholder logic)
            confidence = min(1.0, 0.7 + 0.3 * (1.0 / (1.0 + abs(prediction - 20.0) / 20.0)))

            return float(prediction), confidence

        except Exception as e:
            logger.error(f"[TravelTimePredictor] Prediction failed: {e}")
            return 20.0, 0.0

    def save(self, path: Path):
        """Save trained model to file."""
        if self.model is None:
            logger.warning("[TravelTimePredictor] No model to save")
            return

        try:
            with open(path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_columns': self.feature_columns
                }, f)
            logger.info(f"[TravelTimePredictor] Model saved to {path}")
        except Exception as e:
            logger.error(f"[TravelTimePredictor] Save failed: {e}")

    def load(self, path: Path):
        """Load trained model from file."""
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_columns = data['feature_columns']
                self.is_trained = True
            logger.info(f"[TravelTimePredictor] Model loaded from {path}")
        except Exception as e:
            logger.error(f"[TravelTimePredictor] Load failed: {e}")


class CongestionClassifier:
    """XGBoost model for congestion level classification."""

    def __init__(self, model_name: str = "congestion_classifier"):
        self.model_name = model_name
        self.model: Optional[xgb.XGBClassifier] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.feature_columns: List[str] = []
        self.is_trained = False

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build features for congestion classification."""
        df = df.copy()

        # Time features
        df['hour_of_day'] = (df['timestamp_s'] % 86400) / 3600
        df['is_peak_hour'] = ((df['hour_of_day'] >= 7) & (df['hour_of_day'] <= 10) |
                              (df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 19)).astype(int)

        # Congestion indicators
        df['speed_category'] = pd.cut(df['mean_speed_ms'], bins=[0, 5, 10, 15, 100], labels=[0, 1, 2, 3])
        df['queue_category'] = pd.cut(df['queue_length'], bins=[0, 5, 10, 20, 1000], labels=[0, 1, 2, 3])

        self.feature_columns = [
            'mean_speed_ms', 'vehicle_count', 'queue_length', 'occupancy_pct',
            'upstream_flow_veh_h', 'signal_phase', 'hour_of_day', 'is_peak_hour',
            'speed_category', 'queue_category'
        ]

        # Convert categorical features to numeric
        df['speed_category'] = df['speed_category'].astype(int)
        df['queue_category'] = df['queue_category'].astype(int)

        return df

    def train(
        self,
        dataset_rows: List[Dict],
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        Train XGBoost classifier for congestion level.

        Args:
            dataset_rows: List of TrafficSnapshot dictionaries
            test_size: Fraction for test set
            random_state: Random seed

        Returns:
            Dictionary with classification metrics
        """
        df = pd.DataFrame(dataset_rows)
        df = self.build_features(df)

        # Encode target
        X = df[self.feature_columns]
        y = df['congestion_level']

        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state
        )

        # Train classifier
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=random_state,
            objective='multi:softprob',
            num_class=len(np.unique(y_encoded)),
            verbosity=0
        )

        self.model.fit(X_train, y_train, verbose=False)
        self.is_trained = True

        # Evaluate
        from sklearn.metrics import f1_score, precision_score, recall_score
        y_pred = self.model.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='weighted')
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)

        logger.info(
            f"[CongestionClassifier] Trained on {len(X_train)} samples. "
            f"F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}"
        )

        return {
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'test_samples': len(X_test)
        }

    def predict(self, edge_data: Dict) -> Tuple[str, float]:
        """
        Predict congestion level.

        Args:
            edge_data: Dictionary with edge attributes

        Returns:
            (predicted_level, confidence)
        """
        if not self.is_trained or self.model is None:
            return 'free_flow', 0.0

        try:
            feature_vector = {col: edge_data.get(col, 0.0) for col in self.feature_columns}
            df = pd.DataFrame([feature_vector])
            pred_idx = self.model.predict(df)[0]
            pred_label = self.label_encoder.inverse_transform([pred_idx])[0]
            confidence = 0.7  # Placeholder

            return pred_label, confidence

        except Exception as e:
            logger.error(f"[CongestionClassifier] Prediction failed: {e}")
            return 'free_flow', 0.0


# Global model instances
travel_time_predictor = TravelTimePredictor()
congestion_classifier = CongestionClassifier()
