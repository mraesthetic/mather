import os
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
        self.win_levels = {
            "standard": {
                0: (0.0, 2.0),
                1: (2.0, 5.0),
                2: (5.0, 10.0),
                3: (10.0, 15.0),
                4: (15.0, 20.0),
                5: (20.0, 20.0),  # Reserved / unused
                6: (20.0, 50.0),
                7: (50.0, 100.0),
                8: (100.0, 250.0),
                9: (250.0, 1000.0),
                10: (1000.0, float("inf")),
            },
            "endFeature": {
                0: (0.0, 2.0),
                1: (2.0, 5.0),
                2: (5.0, 10.0),
                3: (10.0, 15.0),
                4: (15.0, 20.0),
                5: (20.0, 20.0),
                6: (20.0, 50.0),
                7: (50.0, 100.0),
                8: (100.0, 250.0),
                9: (250.0, 1000.0),
                10: (1000.0, float("inf")),
            },
        }

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
        self.retrigger_scatter_requirement = 3
        self.super_scatter_upgrade_requirement = 3
        self.scatter_symbol = "S"
        self.super_scatter_symbol = "BS"
        self.basegame_win_scale = 0.313
        self.freegame_win_scale = 8.0
        self.buy_bonus_scales = {
            "regular": 0.71,
            "super": 1.26,
        }
        self.base_bonus_scale = 2.78
        self.mode_freegame_scales = {
            "bonus_hunt": 1.05,
        }
        self.special_symbols = {
            "wild": [],
            "scatter": [self.scatter_symbol],
            "super_scatter": [self.super_scatter_symbol],
            "bomb": ["M"],
        }
        self.bomb_settings = {
            "regular": {
                "appearance_chance": 0.55,
                "count_weights": {1: 55, 2: 30, 3: 12, 4: 3},
                "mult_weights": {
                    2: 160,
                    3: 150,
                    4: 120,
                    5: 100,
                    6: 80,
                    8: 60,
                    10: 50,
                    12: 35,
                    15: 25,
                    20: 18,
                    25: 12,
                    50: 5,
                    100: 2,
                    500: 1,
                    1000: 1,
                },
            },
            "super": {
                "appearance_chance": 0.45,
                "count_weights": {1: 60, 2: 25, 3: 10, 4: 4, 5: 1},
                "mult_weights": {
                    20: 260,
                    25: 220,
                    50: 30,
                    100: 5,
                    500: 1,
                    1000: 1,
                },
            },
        }

        self.buy_bomb_settings = {
            "regular": {
                "appearance_chance": 0.65,
                "count_weights": {1: 45, 2: 30, 3: 20, 4: 5},
                "mult_weights": {
                    2: 90,
                    3: 85,
                    4: 80,
                    5: 70,
                    6: 60,
                    8: 55,
                    10: 45,
                    12: 35,
                    15: 25,
                    20: 18,
                    25: 12,
                    50: 8,
                    100: 4,
                    500: 1,
                    1000: 1,
                },
            },
            "super": {
                "appearance_chance": 0.5,
                "count_weights": {1: 50, 2: 30, 3: 12, 4: 6, 5: 2},
                "mult_weights": {
                    20: 150,
                    25: 130,
                    50: 25,
                    100: 6,
                    500: 2,
                    1000: 1,
                },
            },
        }

        self.regular_bonus_mults = {
            2: 320,
            3: 260,
            4: 210,
            5: 160,
            6: 120,
            8: 90,
            10: 65,
            12: 40,
            15: 25,
            20: 15,
            25: 10,
            50: 4,
            100: 1,
            500: 1,
            1000: 1,
        }
        self.super_bonus_mults = {
            20: 260,
            25: 200,
            50: 20,
            100: 3,
            500: 1,
            1000: 1,
        }

        self.freespin_triggers = {
            self.basegame_type: {
                3: self.initial_free_spins,
                4: self.initial_free_spins,
                5: self.initial_free_spins,
                6: self.initial_free_spins,
            },
            self.freegame_type: {
                3: self.retrigger_spins,
                4: self.retrigger_spins,
                5: self.retrigger_spins,
                6: self.retrigger_spins,
                7: self.retrigger_spins,
                8: self.retrigger_spins,
                9: self.retrigger_spins,
                10: self.retrigger_spins,
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
        optimizer_mode = os.environ.get("OPTIMIZER_MODE") == "1"
        if optimizer_mode:
            base_profile = {"zero": 0.0, "base": 0.60, "reg": 0.34, "super": 0.022}
            hunt_profile = {"zero": 0.0, "base": 0.30, "reg": 0.60, "super": 0.062}
        else:
            base_profile = {"zero": 0.0, "base": 1.0, "reg": 0.0, "super": 0.0}
            hunt_profile = {"zero": 0.0, "base": 1.0, "reg": 0.0, "super": 0.0}

        self.bet_modes = [
            self._build_main_mode(
                "base",
                reel_id="BR0",
                zero_quota=base_profile["zero"],
                base_quota=base_profile["base"],
                reg_quota=base_profile["reg"],
                super_quota=base_profile["super"],
                cost=1.0,
            ),
            self._build_main_mode(
                "bonus_hunt",
                reel_id="BR_HUNT",
                zero_quota=hunt_profile["zero"],
                base_quota=hunt_profile["base"],
                reg_quota=hunt_profile["reg"],
                super_quota=hunt_profile["super"],
                cost=3.0,
            ),
            self._build_regular_buy_mode(),
            self._build_super_buy_mode(),
        ]

    def _build_main_mode(
        self,
        name: str,
        reel_id: str,
        zero_quota: float,
        base_quota: float,
        reg_quota: float,
        super_quota: float,
        cost: float = 1.0,
    ) -> BetMode:
        return BetMode(
            name=name,
            cost=cost,
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
                            self.freegame_type: {
                                20: 210,
                                25: 130,
                                50: 70,
                                100: 30,
                                500: 5,
                                1000: 1,
                            },
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
                            self.freegame_type: {
                                2: 320,
                                3: 240,
                                4: 170,
                                5: 120,
                                6: 90,
                                8: 60,
                                10: 35,
                                12: 20,
                                15: 12,
                                20: 8,
                                25: 5,
                                50: 3,
                                100: 2,
                                500: 1,
                                1000: 1,
                            },
                        },
                    },
                )
            )
        if zero_quota > 0:
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
                            self.freegame_type: {
                                2: 320,
                                3: 240,
                                4: 170,
                                5: 120,
                                6: 90,
                                8: 60,
                                10: 35,
                                12: 20,
                                15: 12,
                                20: 8,
                                25: 5,
                                50: 3,
                                100: 2,
                                500: 1,
                                1000: 1,
                            },
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
                        self.freegame_type: {
                            2: 320,
                            3: 240,
                            4: 170,
                            5: 120,
                            6: 90,
                            8: 60,
                            10: 35,
                            12: 20,
                            15: 12,
                            20: 8,
                            25: 5,
                            50: 3,
                            100: 2,
                            500: 1,
                            1000: 1,
                        },
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
                            self.freegame_type: {
                                2: 20,
                                3: 20,
                                4: 25,
                                5: 75,
                                6: 80,
                                8: 100,
                                10: 110,
                                12: 200,
                                15: 125,
                                20: 250,
                                25: 70,
                                50: 55,
                                100: 30,
                                500: 8,
                                1000: 2,
                            },
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
                            self.freegame_type: {
                                20: 280,
                                25: 180,
                                50: 40,
                                75: 15,
                                100: 8,
                                250: 3,
                                500: 1,
                                1000: 1,
                            },
                        },
                    },
                )
            ],
        )
