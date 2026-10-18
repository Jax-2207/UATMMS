"""
UATMMS Controller Evaluation & Benchmarking Harness
Compares: Fixed-time vs Queue-based Adaptive vs Max-Pressure vs RL Policy
"""
import argparse
from backend.app.core.logging import logger


def main():
    parser = argparse.ArgumentParser(description="Evaluate and compare traffic controllers")
    parser.add_argument("--controllers", nargs="+", default=["fixed_time", "queue_adaptive", "max_pressure"], help="Controllers to evaluate")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 101, 777], help="Evaluation seeds")
    parser.add_argument("--steps", type=int, default=500, help="Evaluation duration steps")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("UATMMS REPRODUCIBLE CONTROLLER BENCHMARK HARNESS")
    logger.info(f"Target Controllers: {args.controllers}")
    logger.info(f"Evaluation Seeds: {args.seeds} (Total: {len(args.seeds)} runs per controller)")
    logger.info(f"Simulation Steps per Run: {args.steps}")
    logger.info("=" * 60)
    logger.info("Harness registered. Benchmark execution will bind to TraCI in Phase 4.")


if __name__ == "__main__":
    main()
