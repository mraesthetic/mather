import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from games.candy_carnage_1000.game_config import GameConfig
from games.candy_carnage_1000.game_optimization import OptimizationSetup
from games.candy_carnage_1000.gamestate import GameState
from src.write_data.write_configs import generate_configs

config = GameConfig()
gamestate = GameState(config)

OptimizationSetup(config)
generate_configs(gamestate)
