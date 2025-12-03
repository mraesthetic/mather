from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        self.game_config.opt_params = {
            "base": self._main_mode_setup(
                base_rtp=0.466,
                regular_fs_rtp=0.418,
                super_fs_rtp=0.078,
                zero_rtp=0.0,
            ),
            "bonus_hunt": self._main_mode_setup(
                base_rtp=0.188,
                regular_fs_rtp=0.540,
                super_fs_rtp=0.111,
                zero_rtp=0.123,
            ),
            "regular_buy": self._regular_buy_setup(),
            "super_buy": self._super_buy_setup(),
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)

    def _main_mode_setup(self, base_rtp: float, regular_fs_rtp: float, super_fs_rtp: float, zero_rtp: float):
        return {
                "conditions": {
                "wincap": ConstructConditions(rtp=0.0, av_win=25000, search_conditions=25000).return_dict(),
                "zero": ConstructConditions(rtp=zero_rtp, hr=0.0).return_dict(),
                "basegame": ConstructConditions(rtp=base_rtp, hr=0.35).return_dict(),
                "regular_fs": ConstructConditions(
                    rtp=regular_fs_rtp,
                    hr="x",
                    search_conditions={"feature_type": "regular"},
                ).return_dict(),
                "super_fs": ConstructConditions(
                    rtp=super_fs_rtp,
                    hr="x",
                    search_conditions={"feature_type": "super"},
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                        "criteria": "regular_fs",
                        "scale_factor": 1.15,
                        "win_range": (100, 500),
                            "probability": 1.0,
                        },
                        {
                        "criteria": "super_fs",
                        "scale_factor": 1.25,
                        "win_range": (500, 25000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                num_show=2500,
                num_per_fence=5000,
                min_m2m=3,
                max_m2m=6,
                    pmb_rtp=1.0,
                sim_trials=2500,
                test_spins=[50, 150, 300],
                test_weights=[0.4, 0.4, 0.2],
                    score_type="rtp",
                max_trial_dist=12,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                applied_criteria=["super_fs"],
                bias_ranges=[(500, 25000)],
                bias_weights=[0.1],
            ).return_dict(),
        }

    def _regular_buy_setup(self):
        return {
            "conditions": {
                "regular_fs": ConstructConditions(
                    rtp=self.game_config.rtp,
                    hr="x",
                ).return_dict(),
            },
            "scaling": ConstructScaling(
                [
                    {
                        "criteria": "regular_fs",
                        "scale_factor": 1.1,
                        "win_range": (100, 500),
                        "probability": 1.0,
                    }
                ]
            ).return_dict(),
            "parameters": ConstructParameters(
                num_show=1500,
                num_per_fence=3000,
                min_m2m=2,
                max_m2m=5,
                pmb_rtp=1.0,
                sim_trials=1500,
                test_spins=[25, 50, 100],
                test_weights=[0.4, 0.4, 0.2],
                score_type="rtp",
                max_trial_dist=10,
            ).return_dict(),
            "distribution_bias": ConstructFenceBias(
                applied_criteria=["regular_fs"],
                bias_ranges=[(50, 5000)],
                bias_weights=[0.2],
            ).return_dict(),
        }

    def _super_buy_setup(self):
        return {
            "conditions": {
                "super_fs": ConstructConditions(
                    rtp=self.game_config.rtp,
                    hr="x",
                ).return_dict(),
            },
            "scaling": ConstructScaling(
                [
                    {
                        "criteria": "super_fs",
                        "scale_factor": 1.2,
                        "win_range": (500, 25000),
                        "probability": 1.0,
                    }
                ]
            ).return_dict(),
            "parameters": ConstructParameters(
                num_show=1500,
                num_per_fence=3000,
                min_m2m=2,
                max_m2m=5,
                pmb_rtp=1.0,
                sim_trials=1500,
                test_spins=[25, 50, 100],
                test_weights=[0.3, 0.4, 0.3],
                score_type="rtp",
                max_trial_dist=10,
            ).return_dict(),
            "distribution_bias": ConstructFenceBias(
                applied_criteria=["super_fs"],
                bias_ranges=[(500, 25000)],
                bias_weights=[0.3],
            ).return_dict(),
        }
