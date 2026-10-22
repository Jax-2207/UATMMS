"""
UATMMS Traffic Prediction Dataset
Extracts time-series features from simulation for model training.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import csv
import os
from pathlib import Path
from backend.app.core.logging import logger


@dataclass
class TrafficSnapshot:
    """Single time-step snapshot of traffic conditions on an edge."""
    timestamp_s: float
    edge_id: str
    mean_speed_ms: float          # meters/second
    vehicle_count: int             # vehicles on edge
    queue_length: int              # vehicles waiting at signal
    occupancy_pct: float           # percentage of edge occupied (0-100)
    upstream_flow_veh_h: float     # vehicles/hour entering edge
    signal_phase: int              # current signal phase (0-7)
    signal_time_in_phase_s: float  # time spent in current phase
    incident_severity: int         # 0=none, 1-5=severity level
    congestion_level: str          # free_flow, moderate, congested, gridlock
    travel_time_5min_s: float      # Ground truth: travel time 5min in future


class TrafficDataset:
    """
    Collects and manages time-series traffic data for model training.
    Stores snapshots in CSV format for easy loading into ML frameworks.
    """

    def __init__(self, output_dir: str = "backend/data/training_logs"):
        """
        Args:
            output_dir: Directory to store training data files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file: Optional[Path] = None
        self.csv_writer: Optional[csv.DictWriter] = None
        self.snapshots: List[TrafficSnapshot] = []
        self.run_id: Optional[str] = None

    def start_recording(self, run_id: str):
        """
        Start a new recording session.

        Args:
            run_id: Unique identifier for this simulation run
        """
        self.run_id = run_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"traffic_data_{run_id}_{timestamp}.csv"
        self.current_log_file = self.output_dir / filename

        logger.info(f"[TrafficDataset] Starting recording to {self.current_log_file}")

        # Write CSV header
        try:
            with open(self.current_log_file, 'w', newline='') as f:
                fieldnames = [
                    'timestamp_s', 'edge_id', 'mean_speed_ms', 'vehicle_count',
                    'queue_length', 'occupancy_pct', 'upstream_flow_veh_h',
                    'signal_phase', 'signal_time_in_phase_s', 'incident_severity',
                    'congestion_level', 'travel_time_5min_s'
                ]
                self.csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
                self.csv_writer.writeheader()
        except Exception as e:
            logger.error(f"[TrafficDataset] Failed to create log file: {e}")

    def record_snapshot(self, snapshot: TrafficSnapshot):
        """
        Record a traffic snapshot.

        Args:
            snapshot: TrafficSnapshot to record
        """
        if not self.csv_writer or not self.current_log_file:
            logger.warning("[TrafficDataset] Recording not started. Snapshot dropped.")
            return

        self.snapshots.append(snapshot)

        # Write to CSV
        try:
            with open(self.current_log_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp_s', 'edge_id', 'mean_speed_ms', 'vehicle_count',
                    'queue_length', 'occupancy_pct', 'upstream_flow_veh_h',
                    'signal_phase', 'signal_time_in_phase_s', 'incident_severity',
                    'congestion_level', 'travel_time_5min_s'
                ])
                writer.writerow({
                    'timestamp_s': snapshot.timestamp_s,
                    'edge_id': snapshot.edge_id,
                    'mean_speed_ms': snapshot.mean_speed_ms,
                    'vehicle_count': snapshot.vehicle_count,
                    'queue_length': snapshot.queue_length,
                    'occupancy_pct': snapshot.occupancy_pct,
                    'upstream_flow_veh_h': snapshot.upstream_flow_veh_h,
                    'signal_phase': snapshot.signal_phase,
                    'signal_time_in_phase_s': snapshot.signal_time_in_phase_s,
                    'incident_severity': snapshot.incident_severity,
                    'congestion_level': snapshot.congestion_level,
                    'travel_time_5min_s': snapshot.travel_time_5min_s
                })
        except Exception as e:
            logger.error(f"[TrafficDataset] Failed to write snapshot: {e}")

    def stop_recording(self) -> Optional[Path]:
        """
        Stop recording and finalize dataset.

        Returns:
            Path to the generated dataset file
        """
        if not self.current_log_file:
            logger.warning("[TrafficDataset] No active recording to stop")
            return None

        logger.info(
            f"[TrafficDataset] Stopped recording. Collected {len(self.snapshots)} snapshots "
            f"from {self.current_log_file}"
        )

        result = self.current_log_file
        self.current_log_file = None
        self.csv_writer = None
        self.snapshots = []
        return result

    def get_dataset_files(self, limit: Optional[int] = None) -> List[Path]:
        """
        Get all available dataset files.

        Args:
            limit: Maximum number of files to return (most recent first)

        Returns:
            List of Path objects to CSV dataset files
        """
        files = sorted(self.output_dir.glob("traffic_data_*.csv"), reverse=True)

        if limit:
            files = files[:limit]

        return files

    def load_dataset(self, file_path: Path) -> List[Dict]:
        """
        Load a dataset from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            List of dictionaries (rows) from CSV
        """
        rows = []

        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields
                    row['timestamp_s'] = float(row['timestamp_s'])
                    row['mean_speed_ms'] = float(row['mean_speed_ms'])
                    row['vehicle_count'] = int(row['vehicle_count'])
                    row['queue_length'] = int(row['queue_length'])
                    row['occupancy_pct'] = float(row['occupancy_pct'])
                    row['upstream_flow_veh_h'] = float(row['upstream_flow_veh_h'])
                    row['signal_phase'] = int(row['signal_phase'])
                    row['signal_time_in_phase_s'] = float(row['signal_time_in_phase_s'])
                    row['incident_severity'] = int(row['incident_severity'])
                    row['travel_time_5min_s'] = float(row['travel_time_5min_s'])
                    rows.append(row)

            logger.info(f"[TrafficDataset] Loaded {len(rows)} rows from {file_path}")
            return rows

        except Exception as e:
            logger.error(f"[TrafficDataset] Failed to load dataset: {e}")
            return []

    def combine_datasets(self, run_ids: List[str]) -> Tuple[Path, int]:
        """
        Combine multiple dataset files into a single training file.

        Args:
            run_ids: List of run IDs to combine

        Returns:
            (combined_file_path, total_rows)
        """
        combined_rows = []
        total_files = 0

        for run_id in run_ids:
            # Find file matching run_id
            matching_files = [f for f in self.output_dir.glob(f"traffic_data_{run_id}_*.csv")]

            for file_path in matching_files:
                rows = self.load_dataset(file_path)
                combined_rows.extend(rows)
                total_files += 1

        # Write combined dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_file = self.output_dir / f"combined_training_{timestamp}.csv"

        try:
            with open(combined_file, 'w', newline='') as f:
                if combined_rows:
                    fieldnames = list(combined_rows[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(combined_rows)

            logger.info(
                f"[TrafficDataset] Combined {total_files} datasets into {combined_file} "
                f"({len(combined_rows)} rows)"
            )
            return combined_file, len(combined_rows)

        except Exception as e:
            logger.error(f"[TrafficDataset] Failed to combine datasets: {e}")
            return None, 0


# Global instance
traffic_dataset = TrafficDataset()
