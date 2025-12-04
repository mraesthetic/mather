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
                base_rtp=0.60,  # Target 60% of RTP from base spins
                regular_fs_rtp=0.34,  # Target 34% from regular FS
                super_fs_rtp=0.022,  # Target 2.2% from super FS
                zero_rtp=0.0,
                regular_hr=1 / 190,
                super_hr=1 / 1500,
            ),
            "bonus_hunt": self._main_mode_setup(
                base_rtp=0.30,  # Target 30% of RTP from base spins
                regular_fs_rtp=0.60,  # Target 60% from regular FS
                super_fs_rtp=0.062,  # Target 6.2% from super FS
                zero_rtp=0.0,
                regular_hr=1 / 70,
                super_hr=1 / 900,
            ),
            "regular_buy": self._regular_buy_setup(),
            "super_buy": self._super_buy_setup(),
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)

    def _main_mode_setup(
        self,
        base_rtp: float,
        regular_fs_rtp: float,
        super_fs_rtp: float,
        zero_rtp: float,
        regular_hr: float,
        super_hr: float,
    ):
        conditions = {}
        conditions["wincap"] = ConstructConditions(
            rtp=0.0,
            av_win=25000,
            search_conditions=25000,
        ).return_dict()

        conditions["regular_fs"] = ConstructConditions(
            rtp=regular_fs_rtp,
            hr=regular_hr,
            search_conditions={"gametype": "freegame"},
        ).return_dict()

        conditions["super_fs"] = ConstructConditions(
            rtp=super_fs_rtp,
            hr=super_hr,
            search_conditions={"gametype": "freegame"},
        ).return_dict()

        conditions["basegame"] = ConstructConditions(
            rtp=base_rtp,
            hr=0.35,
        ).return_dict()

        if zero_rtp > 0:
            conditions["zero"] = ConstructConditions(rtp=zero_rtp, hr=1.0).return_dict()

        return {
                "conditions": conditions,
                "scaling": ConstructScaling(
                    [
                        {
                        "criteria": "regular_fs",
                        "scale_factor": 1.10,  # Reduced from 1.15 to lower RTP
                        "win_range": (100, 500),
                            "probability": 1.0,
                        },
                        {
                        "criteria": "super_fs",
                        "scale_factor": 1.15,  # Reduced from 1.25 to lower RTP
                        "win_range": (500, 25000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                num_show=3000,  # Increased for better distribution matching
                num_per_fence=8000,  # Increased for better RTP convergence
                min_m2m=3,
                max_m2m=6,
                    pmb_rtp=1.0,
                sim_trials=3000,  # Increased for better accuracy
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
