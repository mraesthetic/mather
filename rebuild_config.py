#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from games.candy_carnage_1000.game_config import GameConfig
from games.candy_carnage_1000.game_optimization import OptimizationSetup
from games.candy_carnage_1000.gamestate import GameState
from src.write_data.write_configs import generate_configs

print("Rebuilding math config with reduced fence RTPs...")
config = GameConfig()
gamestate = GameState(config)
OptimizationSetup(config)
generate_configs(gamestate)
print("✅ Config rebuilt! Fence RTPs reduced by additional 7-8%")
print("   Base mode: 0.410 + 0.375 + 0.067 + 0.110 = 0.962")
print("   Bonus hunt: 0.160 + 0.480 + 0.098 + 0.224 = 0.962")

