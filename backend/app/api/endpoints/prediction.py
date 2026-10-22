"""
UATMMS Prediction API Endpoints
REST endpoints for traffic forecasting and model management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
from pydantic import BaseModel
from backend.app.prediction.inference import prediction_engine
from backend.app.prediction.model import travel_time_predictor, congestion_classifier
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


class PredictionRequest(BaseModel):
    """Request for traffic predictions."""
    edge_id: str
    mean_speed_ms: float
    vehicle_count: int
    queue_length: int
    occupancy_pct: float
    upstream_flow_veh_h: float
    signal_phase: int
    signal_time_in_phase_s: float
    incident_severity: int
    congestion_level: str
    travel_time_5min_s: float
    timestamp_s: float
    horizon_s: int = 300  # Prediction horizon in seconds


class PredictionResponse(BaseModel):
    """Response with traffic predictions."""
    edge_id: str
    horizon_s: int
    travel_time_predicted_s: float
    travel_time_confidence: float
    queue_length_predicted: int
    queue_length_confidence: float
    speed_predicted_ms: float
    speed_confidence: float
    congestion_predicted: str
    congestion_confidence: float
    models_used: Dict[str, str]


@router.post("/forecast", response_model=PredictionResponse)
async def forecast_traffic(req: PredictionRequest) -> PredictionResponse:
    """
    Generate traffic predictions for an edge.

    Predicts travel time, queue length, speed, and congestion level
    for a specified horizon (default 5 minutes).

    Args:
        req: PredictionRequest with current edge conditions

    Returns:
        PredictionResponse with forecasted values and confidence scores

    Raises:
        HTTPException: If prediction fails
    """
    try:
        # Build current condition dictionary
        current_condition = req.dict()

        # Get predictions
        travel_time, tt_conf, tt_model = prediction_engine.predict_travel_time(
            req.edge_id, current_condition, req.horizon_s
        )
        queue, q_conf, q_model = prediction_engine.predict_queue_length(
            req.edge_id, current_condition, req.horizon_s
        )
        speed, sp_conf, sp_model = prediction_engine.predict_speed(
            req.edge_id, current_condition, req.horizon_s
        )
        congestion, cg_conf, cg_model = prediction_engine.predict_congestion_level(
            req.edge_id, current_condition, req.horizon_s
        )

        response = PredictionResponse(
            edge_id=req.edge_id,
            horizon_s=req.horizon_s,
            travel_time_predicted_s=travel_time,
            travel_time_confidence=tt_conf,
            queue_length_predicted=queue,
            queue_length_confidence=q_conf,
            speed_predicted_ms=speed,
            speed_confidence=sp_conf,
            congestion_predicted=congestion,
            congestion_confidence=cg_conf,
            models_used={
                "travel_time": tt_model,
                "queue_length": q_model,
                "speed": sp_model,
                "congestion": cg_model
            }
        )

        logger.debug(
            f"[API] Forecast for {req.edge_id}: "
            f"TT={travel_time:.1f}s, Queue={queue}, Congestion={congestion}"
        )

        return response

    except Exception as e:
        logger.error(f"[API] Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.post("/train-xgboost")
async def train_xgboost_models(
    dataset_path: str = Query(..., description="Path to training dataset CSV file")
) -> Dict:
    """
    Train XGBoost models on provided dataset.

    Args:
        dataset_path: Path to CSV file with training data

    Returns:
        Training results and model metrics

    Raises:
        HTTPException: If training fails
    """
    try:
        from pathlib import Path
        import pandas as pd

        # Load dataset
        dataset_file = Path(dataset_path)
        if not dataset_file.exists():
            raise HTTPException(status_code=400, detail=f"Dataset file not found: {dataset_path}")

        df = pd.read_csv(dataset_file)
        dataset_rows = df.to_dict('records')

        logger.info(f"[API] Training XGBoost on {len(dataset_rows)} samples from {dataset_path}")

        # Train travel time predictor
        tt_mae, tt_rmse = travel_time_predictor.train(dataset_rows)

        # Train congestion classifier
        cg_metrics = congestion_classifier.train(dataset_rows)

        # Enable XGBoost in inference engine
        prediction_engine.enable_xgboost()

        result = {
            "status": "success",
            "samples_trained": len(dataset_rows),
            "travel_time_model": {
                "mae": tt_mae,
                "rmse": tt_rmse
            },
            "congestion_model": cg_metrics,
            "models_activated": True
        }

        logger.info(f"[API] XGBoost training completed: {result}")
        return result

    except Exception as e:
        logger.error(f"[API] XGBoost training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/save-models")
async def save_models(
    output_dir: str = Query(..., description="Directory to save model files")
) -> Dict:
    """
    Save trained models to disk.

    Args:
        output_dir: Directory to save pickle files

    Returns:
        Status and saved file paths

    Raises:
        HTTPException: If save fails
    """
    try:
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save models
        tt_path = output_path / "travel_time_model.pkl"
        travel_time_predictor.save(tt_path)

        cg_path = output_path / "congestion_model.pkl"
        # Note: congestion_classifier.save not yet implemented
        logger.info(f"[API] Congestion model save not yet implemented")

        return {
            "status": "saved",
            "travel_time_model": str(tt_path),
            "output_dir": str(output_path)
        }

    except Exception as e:
        logger.error(f"[API] Model save failed: {e}")
        raise HTTPException(status_code=500, detail="Save failed")


@router.get("/models")
async def get_model_status() -> Dict:
    """
    Get status of prediction models.

    Returns available models and their training status.

    Returns:
        Dictionary with model status information
    """
    return prediction_engine.get_model_status()


@router.post("/evaluate-baseline")
async def evaluate_baseline(
    dataset_path: str = Query(..., description="Path to evaluation dataset CSV file")
) -> Dict:
    """
    Evaluate baseline predictors on a dataset.

    Computes MAE for persistence and historical baselines as comparison.

    Args:
        dataset_path: Path to evaluation dataset

    Returns:
        Baseline performance metrics

    Raises:
        HTTPException: If evaluation fails
    """
    try:
        from pathlib import Path
        import pandas as pd
        from sklearn.metrics import mean_absolute_error

        # Load dataset
        dataset_file = Path(dataset_path)
        if not dataset_file.exists():
            raise HTTPException(status_code=400, detail=f"Dataset not found: {dataset_path}")

        df = pd.read_csv(dataset_file)

        # Persistence baseline: predict same as current
        persistence_preds = df['travel_time_5min_s'].values[:-1]  # Shift by 1
        persistence_actual = df['travel_time_5min_s'].values[1:]

        persistence_mae = mean_absolute_error(persistence_actual, persistence_preds)

        logger.info(
            f"[API] Baseline evaluation on {len(df)} samples: "
            f"Persistence MAE = {persistence_mae:.2f}s"
        )

        return {
            "status": "evaluated",
            "samples": len(df),
            "persistence_baseline": {
                "mae": persistence_mae,
                "description": "Predicts next value equals current value"
            },
            "evaluation_dataset": str(dataset_file)
        }

    except Exception as e:
        logger.error(f"[API] Baseline evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Evaluation failed")
