"""

"""

from copy import copy
from game_calculations import GameCalculations
from src.calculations.scatter import Scatter
from game_events import send_mult_info_event
from src.events.events import (
    set_win_event,
    set_total_event,
    fs_trigger_event,
    update_freespin_event,
    update_tumble_win_event,
    enter_bonus_event,
    wincap_event,
)


class GameExecutables(GameCalculations):
    """Game specific executable functions. Used for grouping commonly used/repeated applications."""

    SCATTER_PAYOUTS = {5: 5.0, 6: 100.0}

    def set_end_tumble_event(self):
        """Finalize tumble results."""
        if self.gametype == self.config.freegame_type:
            board_mult, mult_info = self.get_board_multipliers()
            base_tumble_win = copy(self.win_manager.spin_win)
            self.win_manager.set_spin_win(base_tumble_win * board_mult)
            if self.win_manager.spin_win > 0 and mult_info:
                send_mult_info_event(
                    self,
                    board_mult,
                    mult_info,
                    base_tumble_win,
                    self.win_manager.spin_win,
                )
                for pos in mult_info:
                    self.board[pos["reel"]][pos["row"]].assign_attribute({"explode": True})
                update_tumble_win_event(self)

        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def update_freespin_amount(self, scatter_key: str = "scatter"):
        """Start every feature with a fixed number of spins."""
        self.tot_fs = self.config.initial_free_spins
        basegame_trigger = self.gametype == self.config.basegame_type
        fs_trigger_event(
            self,
            basegame_trigger=basegame_trigger,
            freegame_trigger=not basegame_trigger,
        )
        if basegame_trigger:
            bonus_reason = getattr(self, "current_feature_type", "regular")
            self.bonus_type = bonus_reason
            enter_bonus_event(self)

    def get_scatterpays_update_wins(self):
        """Return the board since we are assigning the 'explode' attribute."""
        self.win_data = Scatter.get_scatterpay_wins(
            self.config, self.board, global_multiplier=self.global_multiplier
        )  # Evaluate wins, self.board is modified in-place
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])  # Update wallet

    def determine_feature_trigger(self):
        """Return ('regular'|'super'|None, total_scatter_count)."""
        total_s = self.count_symbol(self.config.scatter_symbol)
        total_bs = self.count_symbol(self.config.super_scatter_symbol)
        total = total_s + total_bs
        super_req = getattr(self.config, "super_scatter_upgrade_requirement", 3)

        if total_bs == 1:
            if total_s >= super_req:
                return "super", total
            if total_s >= 3:
                return "regular", total
            return None, total
        if total_bs == 0 and 4 <= total_s <= 6:
            return "regular", total
        return None, total

    def count_symbol(self, symbol_name: str) -> int:
        count = 0
        for reel in self.board:
            for symbol in reel:
                if symbol.name == symbol_name:
                    count += 1
        return count

    def apply_scatter_payout(self, total_scatter: int) -> None:
        """Award scatter payout before entering a feature."""
        award = self.SCATTER_PAYOUTS.get(total_scatter, 0.0)
        if award <= 0:
            return
        self.win_manager.update_spinwin(award)
        set_win_event(self)
        set_total_event(self)

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        # Global multiplier mechanic is disabled for Candy Carnage; always stay at 1
        self.global_multiplier = 1
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """Retrigger on three or more regular scatters only."""
        if self.gametype != self.config.freegame_type:
            return False
        scatter_count = self.count_symbol(self.config.scatter_symbol)
        return scatter_count >= 3

    def update_global_mult(self) -> None:
        """Disable the incremental global multiplier mechanic."""
        self.global_multiplier = 1

    def evaluate_wincap(self) -> bool:
        """Clamp payouts once the 25,000x cap is hit."""
        if self.win_manager.running_bet_win >= self.config.wincap and not self.wincap_triggered:
            self._clamp_totals_to_wincap()
            self.wincap_triggered = True
            wincap_event(self)
            return True
        return False

    def _clamp_totals_to_wincap(self) -> None:
        """Adjust current spin/base/free totals so they never exceed the cap."""
        excess = self.win_manager.running_bet_win - self.config.wincap
        if excess <= 0:
            self.win_manager.running_bet_win = self.config.wincap
            return

        self.win_manager.running_bet_win = self.config.wincap
        if self.win_manager.spin_win >= excess:
            self.win_manager.spin_win -= excess
        else:
            self.win_manager.spin_win = 0

        if self.gametype == self.config.basegame_type:
            self.win_manager.basegame_wins = max(
                0.0, self.win_manager.basegame_wins - min(excess, self.win_manager.basegame_wins)
            )
        else:
            self.win_manager.freegame_wins = max(
                0.0, self.win_manager.freegame_wins - min(excess, self.win_manager.freegame_wins)
            )

        total_component = self.win_manager.basegame_wins + self.win_manager.freegame_wins
        target_total = min(self.win_manager.running_bet_win, self.config.wincap)
        if total_component > target_total:
            overflow = total_component - target_total
            if self.win_manager.freegame_wins >= overflow:
                self.win_manager.freegame_wins -= overflow
            else:
                remaining = overflow - self.win_manager.freegame_wins
                self.win_manager.freegame_wins = 0.0
                self.win_manager.basegame_wins = max(0.0, self.win_manager.basegame_wins - remaining)
        elif total_component < target_total:
            deficit = target_total - total_component
            if self.gametype == self.config.basegame_type:
                self.win_manager.basegame_wins += deficit
            else:
                self.win_manager.freegame_wins += deficit
