"""

"""

import random
from typing import List, Tuple

from game_calculations import GameCalculations
from src.calculations.scatter import Scatter
from src.calculations.statistics import get_random_outcome
from game_events import send_mult_info_event
from src.events.events import (
    set_win_event,
    set_total_event,
    fs_trigger_event,
    update_global_mult_event,
    update_freespin_event,
    wincap_event,
)


class GameExecutables(GameCalculations):
    """Game specific executable functions. Used for grouping commonly used/repeated applications."""

    SCATTER_PAYOUTS = {5: 5.0, 6: 100.0}

    def set_end_tumble_event(self):
        """Finalize tumble results."""
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

    def get_scatterpays_update_wins(self):
        """Return the board since we are assigning the 'explode' attribute."""
        self.win_data = Scatter.get_scatterpay_wins(
            self.config, self.board, global_multiplier=self.global_multiplier
        )  # Evaluate wins, self.board is modified in-place
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])  # Update wallet
        self._handle_bombs_for_current_tumble(self.win_data["totalWin"])

    def determine_feature_trigger(self):
        """Return ('regular'|'super'|None, total_scatter_count)."""
        total_s = self.count_symbol(self.config.scatter_symbol)
        total_bs = self.count_symbol(self.config.super_scatter_symbol)
        total = total_s + total_bs

        if total_bs == 1 and total_s >= 3:
            return "super", total
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
        # This game does not reset the global multiplier on each spin
        self.global_multiplier = 1
        update_global_mult_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}

    def _handle_bombs_for_current_tumble(self, base_win: float) -> None:
        """Generate RNG bombs for the current tumble."""
        if self.gametype != self.config.freegame_type:
            return

        feature_type = getattr(self, "current_feature_type", "regular")
        bomb_settings = self.config.bomb_settings.get(feature_type, self.config.bomb_settings["regular"])

        if feature_type == "super":
            if random.random() >= self.config.super_bomb_show_chance:
                return
            if base_win > 0 and random.random() >= self.config.super_bomb_win_ratio:
                return
        else:
            if base_win <= 0:
                return
            if not self._roll_for_bombs(bomb_settings["appearance_chance"]):
                return

        num_bombs = self._get_bomb_count(bomb_settings["count_weights"])
        bomb_positions = self._get_valid_bomb_positions(num_bombs)
        if not bomb_positions:
            return

        bomb_multipliers = [self._get_bomb_multiplier(bomb_settings["mult_weights"]) for _ in bomb_positions]
        total_bomb_mult = sum(bomb_multipliers)

        if base_win > 0:
            bombed_win = base_win * total_bomb_mult
            prior_spin_total = self.win_manager.spin_win - base_win
            self.win_manager.set_spin_win(prior_spin_total + bombed_win)
            self.win_manager.tumble_win = bombed_win
            self.win_data["totalWin"] = bombed_win
            for win in self.win_data["wins"]:
                win.setdefault("meta", {})
                win["meta"]["winWithoutBombs"] = win["win"]
                win["win"] = win["win"] * total_bomb_mult
                win["meta"]["bombMult"] = total_bomb_mult
        else:
            bombed_win = 0.0

        bomb_symbol = self.config.special_symbols["bomb"][0]
        bomb_payload = []
        for (reel, row), multiplier in zip(bomb_positions, bomb_multipliers):
            bomb_payload.append({"reel": reel, "row": row, "value": multiplier, "name": bomb_symbol})

        send_mult_info_event(self, total_bomb_mult, bomb_payload, base_win, bombed_win)

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """Retrigger on three or more regular scatters only."""
        if self.gametype != self.config.freegame_type:
            return False
        scatter_count = self.count_symbol(self.config.scatter_symbol)
        return scatter_count >= 3

    def _roll_for_bombs(self, appearance_chance: float) -> bool:
        """Random chance for bombs to appear on a tumble."""
        return random.random() < appearance_chance

    def _get_bomb_count(self, weight_table: dict) -> int:
        """Determine how many bombs to drop on this tumble."""
        bomb_count = get_random_outcome(weight_table)
        return max(1, bomb_count)

    def _get_bomb_multiplier(self, weight_table: dict) -> int:
        """Sample a multiplier value for a bomb."""
        return get_random_outcome(weight_table)

    def _get_valid_bomb_positions(self, desired_count: int) -> List[Tuple[int, int]]:
        """Return random non-exploding positions for bombs."""
        candidates = []
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if not self.board[reel][row].check_attribute("explode"):
                    candidates.append((reel, row))

        if not candidates:
            return []

        random.shuffle(candidates)
        return candidates[: min(desired_count, len(candidates))]

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
