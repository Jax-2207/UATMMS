"""
UATMMS Simulation Runner CLI
Usage: python scripts/run_simulation.py --scenario default_6junctions --steps 100
"""
import argparse
import os
from pathlib import Path
import sys
import time

# Ensure repository root is on sys.path for standalone script execution
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.simulation.manager import simulation_manager
from backend.app.core.logging import logger


def main():
    parser = argparse.ArgumentParser(description="Run UATMMS simulation scenario")
    parser.add_argument("--scenario", type=str, default="default_6junctions", help="Scenario configuration ID")
    parser.add_argument("--steps", type=int, default=30, help="Number of simulation steps to run")
    parser.add_argument("--step-size", type=float, default=1.0, help="Step length in seconds")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    logger.info(f"Initializing simulation run for scenario '{args.scenario}' (steps={args.steps}, seed={args.seed})")
    state = simulation_manager.start(scenario_id=args.scenario, seed=args.seed)

    for i in range(args.steps):
        state = simulation_manager.step_forward()
        if (i + 1) % 10 == 0 or i == args.steps - 1:
            logger.info(
                f"Step {state.step:03d}/{args.steps} | Time: {state.simulation_time_s:.1f}s | "
                f"Vehicles: {state.active_vehicle_count} | Avg Speed: {state.average_speed_mps:.1f} m/s"
            )
        time.sleep(0.02)  # Fast CLI replay

    logger.info(f"Simulation completed successfully [Run ID: {state.run_id}]")


if __name__ == "__main__":
    main()
