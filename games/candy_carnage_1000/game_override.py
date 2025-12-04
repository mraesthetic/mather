import random

from game_executables import *
from src.events.events import update_freespin_event, fs_trigger_event, reveal_event
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
        self.current_feature_type = None
        self.bonus_type = None

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.global_multiplier = 1

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Ensure freegame boards never contain multiple scatters on the same reel."""
        if (
            self.gametype == self.config.freegame_type
            and not self.get_current_distribution_conditions().get("force_freegame")
        ):
            attempts = 0
            max_attempts = 1000
            while attempts < max_attempts:
                attempts += 1
                super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
                if self._is_valid_scatter_board():
                    break
            else:
                raise RuntimeError("Failed to draw a valid freegame board within attempt limit.")

            if emit_event:
                reveal_event(self)
            return

        super().draw_board(emit_event=emit_event, trigger_symbol=trigger_symbol)

    def tumble_board(self) -> None:
        """Run the normal tumble logic, then scrub duplicate scatters per reel."""
        super().tumble_board()
        self._dedupe_scatter_columns()

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> bool:
        """Candy Carnage retriggers grant +5 spins when 3+ scatters land."""
        scatter_count = self.count_special_symbols(scatter_key)
        if scatter_count < self.config.retrigger_scatter_requirement:
            return False
        self.tot_fs += self.config.retrigger_spins
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)
        return True

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
        use_buy_table = (
            getattr(self, "entry_was_buy", False)
            and self.gametype == self.config.freegame_type
        )
        if use_buy_table:
            bonus_key = getattr(self, "bonus_type", "regular")
            buy_table = self.config.buy_bomb_settings.get(bonus_key, {}).get("mult_weights")
            if buy_table:
                multiplier_value = get_random_outcome(buy_table)
            else:
                multiplier_value = get_random_outcome(
                    self.get_current_distribution_conditions()["mult_values"][self.gametype]
                )
        else:
            multiplier_value = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][self.gametype]
            )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def _dedupe_scatter_columns(self) -> None:
        """Replace any secondary scatters on a reel with non-scatter fillers."""
        scatter_names = {self.config.scatter_symbol, self.config.super_scatter_symbol}
        replacement_pool = self._get_non_scatter_symbol_pool()
        reels_with_scatter = set()
        replaced = False

        for reel_idx in range(self.config.num_reels):
            for row_idx, symbol in enumerate(self.board[reel_idx]):
                if symbol.name not in scatter_names:
                    continue
                if reel_idx in reels_with_scatter:
                    filler_name = random.choice(replacement_pool)
                    self.board[reel_idx][row_idx] = self.create_symbol(filler_name)
                    replaced = True
                else:
                    reels_with_scatter.add(reel_idx)

        if replaced:
            self.get_special_symbols_on_board()
