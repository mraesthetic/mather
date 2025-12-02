import os
import random
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Load all game specific parameters and elements"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "candy_carnage_1000"
        self.game_name = "Candy Carnage 1000"
        self.provider_numer = 0
        self.working_name = "Candy Carnage 1000 (scatter pays)"
        self.wincap = 25000.0
        self.win_type = "scatter"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 6
        # Optionally include variable number of rows per reel
        self.num_rows = [5] * self.num_reels
        # Board and Symbol Properties
        t1, t2, t3 = (8, 9), (10, 11), (12, 36)
        pay_group = {
            (t1, "H1"): 10.0,
            (t2, "H1"): 25.0,
            (t3, "H1"): 50.0,
            (t1, "H2"): 2.5,
            (t2, "H2"): 10.0,
            (t3, "H2"): 25.0,
            (t1, "H3"): 2.0,
            (t2, "H3"): 5.0,
            (t3, "H3"): 15.0,
            (t1, "H4"): 1.5,
            (t2, "H4"): 2.0,
            (t3, "H4"): 12.0,
            (t1, "L1"): 1.0,
            (t2, "L1"): 1.5,
            (t3, "L1"): 10.0,
            (t1, "L2"): 0.8,
            (t2, "L2"): 1.2,
            (t3, "L2"): 8.0,
            (t1, "L3"): 0.5,
            (t2, "L3"): 1.0,
            (t3, "L3"): 5.0,
            (t1, "L4"): 0.4,
            (t2, "L4"): 0.9,
            (t3, "L4"): 4.0,
            (t1, "L5"): 0.25,
            (t2, "L5"): 0.75,
            (t3, "L5"): 2.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.initial_free_spins = 10
        self.retrigger_spins = 5
        self.max_free_spins = 20
        # Probability thresholds for retrigger caps (CDF order)
        self.retrigger_distribution = [
            (0, 0.6899),
            (1, 0.8899),
            (2, 0.9899),
            (3, 0.9999),
            (4, 1.0),
        ]
        self.scatter_symbol = "S"
        self.super_scatter_symbol = "BS"
        self.special_symbols = {
            "wild": ["W"],
            "scatter": [self.scatter_symbol],
            "super_scatter": [self.super_scatter_symbol],
            "bomb": ["M"],
        }
        self.bomb_settings = {
            "regular": {
                "appearance_chance": 0.15,
                "count_weights": {1: 92, 2: 7, 3: 1},
                "mult_weights": {
                    2: 320,
                    3: 260,
                    4: 200,
                    5: 160,
                    6: 120,
                    8: 80,
                    10: 55,
                    12: 35,
                    15: 25,
                    20: 15,
                    25: 8,
                    50: 3,
                    100: 2,
                    250: 1,
                    500: 0.5,
                    1000: 0.2,
                },
            },
            "super": {
                "appearance_chance": 0.35,
                "count_weights": {1: 75, 2: 20, 3: 5},
                "mult_weights": {
                    20: 260,
                    25: 220,
                    30: 170,
                    40: 130,
                    50: 95,
                    60: 70,
                    75: 50,
                    100: 35,
                    150: 18,
                    250: 10,
                    500: 5,
                    1000: 2,
                },
            },
        }

        self.freespin_triggers = {
            self.basegame_type: {
                3: 8,
                4: 12,
                5: 15,
                6: 17,
                7: 19,
                8: 21,
                9: 23,
                10: 24,
            },
            self.freegame_type: {
                2: 3,
                3: 5,
                4: 8,
                5: 12,
                6: 14,
                7: 16,
                8: 18,
                9: 10,
                10: 12,
            },
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {
            "BR0": "BR0.csv",
            "BR_HUNT": "BR_HUNT.csv",
            "FR0": "FR0.csv",
            "WCAP": "WCAP.csv",
        }
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        self.bet_modes = [
            self._build_main_mode(
                "base",
                reel_id="BR0",
                zero_quota=0.45,
                base_quota=0.35,
                reg_quota=0.0,
                super_quota=0.0,
            ),
            self._build_main_mode(
                "bonus_hunt",
                reel_id="BR_HUNT",
                zero_quota=0.3,
                base_quota=0.25,
                reg_quota=0.0,
                super_quota=0.0,
            ),
            self._build_regular_buy_mode(),
            self._build_super_buy_mode(),
        ]

    def sample_retrigger_cap(self) -> int:
        roll = random.random()
        for cap, threshold in self.retrigger_distribution:
            if roll <= threshold:
                return cap
        return 0

    def _build_main_mode(
        self,
        name: str,
        reel_id: str,
        zero_quota: float,
        base_quota: float,
        reg_quota: float,
        super_quota: float,
    ) -> BetMode:
        return BetMode(
            name=name,
            cost=1.0,
            rtp=self.rtp,
            max_win=self.wincap,
            auto_close_disabled=False,
            is_feature=True,
            is_buybonus=False,
            distributions=self._main_mode_distributions(
                reel_id,
                zero_quota,
                base_quota,
                reg_quota,
                super_quota,
            ),
        )

    def _main_mode_distributions(
        self,
        reel_id: str,
        zero_quota: float,
        base_quota: float,
        reg_quota: float,
        super_quota: float,
    ) -> list:
        dists: list = []
        if super_quota > 0:
            dists.append(
                Distribution(
                    criteria="super_fs",
                    quota=super_quota,
                    conditions={
                        "reel_weights": {
                            self.basegame_type: {reel_id: 1},
                            self.freegame_type: {"FR0": 1},
                        },
                        "force_freegame": True,
                        "feature_type": "super",
                        "scatter_triggers": {4: 10, 5: 5, 6: 1},
                        "mult_values": {
                            self.basegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10},
                            self.freegame_type: {2: 100, 4: 80, 5: 50, 7: 20, 10: 10},
                        },
                    },
                )
            )
        if reg_quota > 0:
            dists.append(
                Distribution(
                    criteria="regular_fs",
                    quota=reg_quota,
                    conditions={
                        "reel_weights": {
                            self.basegame_type: {reel_id: 1},
                            self.freegame_type: {"FR0": 1},
                        },
                        "force_freegame": True,
                        "feature_type": "regular",
                        "scatter_triggers": {4: 5, 5: 1},
                        "mult_values": {
                            self.basegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10},
                            self.freegame_type: {2: 100, 4: 80, 5: 50, 7: 20, 10: 10},
                        },
                    },
                )
            )
        dists.append(
            Distribution(
                criteria="zero",
                quota=zero_quota,
                win_criteria=0.0,
                conditions={
                    "reel_weights": {
                        self.basegame_type: {reel_id: 1},
                        self.freegame_type: {"FR0": 1},
                    },
                    "mult_values": {
                        self.basegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10},
                        self.freegame_type: {2: 100, 4: 80, 5: 50, 7: 20, 10: 10},
                    },
                    "force_freegame": False,
                },
            )
        )
        dists.append(
            Distribution(
                criteria="basegame",
                quota=base_quota,
                conditions={
                    "reel_weights": {
                        self.basegame_type: {reel_id: 1},
                        self.freegame_type: {"FR0": 1},
                    },
                    "mult_values": {
                        self.basegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10},
                        self.freegame_type: {2: 100, 4: 80, 5: 50, 7: 20, 10: 10},
                    },
                    "force_freegame": False,
                },
            )
        )
        return dists

    def _build_regular_buy_mode(self) -> BetMode:
        return BetMode(
            name="regular_buy",
            cost=100.0,
            rtp=self.rtp,
            max_win=self.wincap,
            auto_close_disabled=False,
            is_feature=False,
            is_buybonus=True,
            distributions=[
                Distribution(
                    criteria="regular_fs",
                    quota=1.0,
                    conditions={
                        "reel_weights": {
                            self.basegame_type: {"BR0": 1},
                            self.freegame_type: {"FR0": 1},
                        },
                        "force_freegame": True,
                        "feature_type": "regular",
                        "scatter_triggers": {4: 1},
                        "buy_entry_pattern": {"scatter": 4, "super_scatter": 0},
                        "mult_values": {
                            self.basegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10},
                            self.freegame_type: {2: 100, 4: 80, 5: 50, 7: 20, 10: 10},
                        },
                    },
                )
            ],
        )

    def _build_super_buy_mode(self) -> BetMode:
        return BetMode(
            name="super_buy",
            cost=500.0,
            rtp=self.rtp,
            max_win=self.wincap,
            auto_close_disabled=False,
            is_feature=False,
            is_buybonus=True,
            distributions=[
                Distribution(
                    criteria="super_fs",
                    quota=1.0,
                    conditions={
                        "reel_weights": {
                            self.basegame_type: {"BR0": 1},
                            self.freegame_type: {"FR0": 1},
                        },
                        "force_freegame": True,
                        "feature_type": "super",
                        "scatter_triggers": {3: 1},
                        "buy_entry_pattern": {"scatter": 3, "super_scatter": 1},
                        "mult_values": {
                            self.basegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10},
                            self.freegame_type: {2: 100, 4: 80, 5: 50, 7: 20, 10: 10},
                        },
                    },
                )
            ],
        )
