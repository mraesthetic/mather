from game_executables import *
from src.events.events import update_freespin_event, update_global_mult_event
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        # Reset global values used across multiple projects
        super().reset_book()
        # Reset parameters relevant to local game only
        self.tumble_win = 0
        self.entry_was_buy = False
        self.pending_feature_type = None

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.global_multiplier = 1

    def check_freespin_entry(self, scatter_key: str = "scatter") -> bool:
        """Allow natural scatter triggers when the distribution is not forcing a feature."""
        conditions = self.get_current_distribution_conditions()
        # Preserve legacy behaviour for forced freegames (buy bonuses, scripted distributions, etc.)
        if conditions.get("force_freegame"):
            return super().check_freespin_entry(scatter_key)

        # Natural base-game triggers rely on determine_feature_trigger setting pending_feature_type
        if getattr(self, "pending_feature_type", None):
            self.pending_feature_type = None
            return True

        self.repeat = True
        return False

    def check_game_repeat(self):
        """Verify final win matches required betmode conditions."""
        if self.repeat == False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

    def assign_special_sym_function(self):
        self.special_symbol_functions = {"M": [self.assign_mult_property]}

    def assign_mult_property(self, symbol):
        """Use betmode conditions to assign multiplier attribute to multiplier symbol."""
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})
