"""Entry point for local math runs and config generation."""

import os

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs


def env_int(var_name: str, default: int) -> int:
    """Read integer environment variables with sane fallbacks."""
    try:
        return int(os.environ.get(var_name, default))
    except (TypeError, ValueError):
        return default


def env_bool(var_name: str, default: bool) -> bool:
    """Read boolean environment variables such as BOOKS_COMPRESSION=0/1."""
    value = os.environ.get(var_name)
    if value is None:
        return default
    return value.lower() not in {"0", "false", "no"}


if __name__ == "__main__":
    num_threads = env_int("SIM_THREADS", 8)
    rust_threads = env_int("SIM_RUST_THREADS", 8)
    batching_size = env_int("SIM_BATCH_SIZE", 2500)
    profiling = env_bool("SIM_PROFILING", False)

    compression = env_bool("BOOKS_COMPRESSION", True)

    num_sim_args = {
        "base": env_int("SIMS_BASE", 15000),
        "bonus_hunt": env_int("SIMS_BONUS_HUNT", 15000),
        "regular_buy": env_int("SIMS_REGULAR_BUY", 15000),
        "super_buy": env_int("SIMS_SUPER_BUY", 15000),
    }

    run_conditions = {
        "run_sims": env_bool("RUN_SIMS", True),
        "run_optimization": env_bool("RUN_OPTIMIZATION", True),
        "run_analysis": env_bool("RUN_ANALYSIS", True),
        "run_format_checks": env_bool("RUN_FORMAT_CHECKS", True),
    }
    target_modes = [
        mode.strip()
        for mode in os.environ.get("TARGET_MODES", "").split(",")
        if mode.strip()
    ]

    config = GameConfig()
    gamestate = GameState(config)
    OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
