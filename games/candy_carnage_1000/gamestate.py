import random

from game_override import GameStateOverride
from src.calculations.scatter import Scatter
from src.events.events import reveal_event


class GameState(GameStateOverride):
    """Gamestate for a single spin"""

    def run_spin(self, sim: int, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.prepare_initial_board()

            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()  # Transmit win information

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_scatterpays_update_wins()
                self.emit_tumble_win_events()  # Transmit win information

            self.set_end_tumble_event()
            if self.wincap_triggered:
                self.win_manager.update_gametype_wins(self.gametype)
                break

            self.get_special_symbols_on_board()
            feature_type, total_scatter = self.determine_feature_trigger()
            self.pending_feature_type = feature_type
            conditions = self.get_current_distribution_conditions()
            if feature_type:
                if self.check_freespin_entry():
                    if not self.entry_was_buy:
                        self.apply_scatter_payout(total_scatter)
                    self.win_manager.update_gametype_wins(self.gametype)
                    self.current_feature_type = feature_type
                    self.bonus_type = feature_type
                    self.run_freespin_from_base()
                else:
                    self.pending_feature_type = None
                    self.win_manager.update_gametype_wins(self.gametype)
                    self.repeat = True
            elif conditions.get("force_freegame"):
                self.win_manager.update_gametype_wins(self.gametype)
                self.repeat = True
            else:
                self.pending_feature_type = None
                self.win_manager.update_gametype_wins(self.gametype)

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        self.retrigs_awarded = 0
        self.retrig_cap = self.config.sample_retrigger_cap()
        self.tot_fs = self.config.initial_free_spins
        while self.fs < self.tot_fs:
            if self.wincap_triggered:
                break
            # Resets global multiplier at each spin
            self.update_freespin()
            self.draw_board()

            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()  # Transmit win information

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.update_global_mult()  # Special mechanic - increase multiplier with every tumble

                self.get_scatterpays_update_wins()
                self.emit_tumble_win_events()  # Transmit win information

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.wincap_triggered:
                break

            if (
                self.check_fs_condition()
                and self.retrigs_awarded < self.retrig_cap
            ):
                self.retrigs_awarded += 1
                self.tot_fs = min(
                    self.tot_fs + self.config.retrigger_spins,
                    self.config.max_free_spins,
                )

        self.end_freespin()

    def prepare_initial_board(self, max_attempts: int = 1000):
        """Prepare the initial board, handling buy-entry clamps when needed."""
        conditions = self.get_current_distribution_conditions()
        buy_pattern = conditions.get("buy_entry_pattern")
        if buy_pattern:
            self.entry_was_buy = True
            self._force_buy_entry_board(buy_pattern)
            return

        self.entry_was_buy = False
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            if conditions.get("force_freegame"):
                self.draw_board(emit_event=False)
            else:
                self.create_board_reelstrips()
                self.get_special_symbols_on_board()
            if self._is_valid_scatter_board():
                reveal_event(self)
                return
        raise RuntimeError("Failed to draw a valid base board within attempt limit.")

    def _force_buy_entry_board(self, pattern: dict, max_attempts: int = 100):
        """Force exact scatter / super-scatter counts for buy modes."""
        target_scatter = pattern.get("scatter", 0)
        target_super = pattern.get("super_scatter", 0)
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            self.create_board_reelstrips()
            self._reset_board_to_filler()
            if not self._assign_buy_entry_symbols(target_scatter, target_super):
                continue
            self.get_special_symbols_on_board()
            if self._board_matches_buy_pattern(target_scatter, target_super):
                reveal_event(self)
                return
        raise RuntimeError("Failed to generate buy-entry board within attempt limit.")

    def _assign_buy_entry_symbols(self, target_scatter: int, target_super: int) -> bool:
        """Place scatter and super-scatter symbols on unique reels."""
        total_needed = target_scatter + target_super
        if total_needed > self.config.num_reels:
            return False
        reels = list(range(self.config.num_reels))
        random.shuffle(reels)
        scatter_reels = reels[:target_scatter]
        remaining_reels = reels[target_scatter:]
        if len(remaining_reels) < target_super:
            return False

        for reel in scatter_reels:
            row = random.randrange(len(self.board[reel]))
            self.board[reel][row] = self.create_symbol(self.config.scatter_symbol)

        for reel in remaining_reels[:target_super]:
            row = random.randrange(len(self.board[reel]))
            self.board[reel][row] = self.create_symbol(self.config.super_scatter_symbol)

        return True

    def _reset_board_to_filler(self) -> None:
        """Clamp the entry board to a neutral low-symbol layout before placing scatters."""
        filler_pool = self._get_buy_filler_cycle()
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                filler_name = random.choice(filler_pool)
                self.board[reel][row] = self.create_symbol(filler_name)
        self.get_special_symbols_on_board()

    def _board_matches_buy_pattern(self, target_scatter: int, target_super: int) -> bool:
        """Validate scatter mix for buy-entry boards."""
        scatter_positions = self.special_syms_on_board.get("scatter", [])
        super_positions = self.special_syms_on_board.get("super_scatter", [])
        if len(scatter_positions) != target_scatter or len(super_positions) != target_super:
            return False
        if not super_positions:
            return True
        super_reels = {pos["reel"] for pos in super_positions}
        return all(pos["reel"] not in super_reels for pos in scatter_positions)

    def _get_filler_symbol_name(self) -> str:
        """Return the primary filler symbol (first entry in the low-symbol cycle)."""
        return self._get_buy_filler_cycle()[0]

    def _get_buy_filler_cycle(self):
        """Build a deterministic cycle of low symbols for clamped boards."""
        if not hasattr(self, "_buy_filler_cycle"):
            low_symbols = sorted(
                {
                    symbol
                    for (_, symbol) in self.config.paytable.keys()
                    if symbol.startswith("L") and symbol not in (self.config.scatter_symbol, self.config.super_scatter_symbol)
                }
            )
            if not low_symbols:
                low_symbols = [
                    symbol
                    for (_, symbol) in self.config.paytable.keys()
                    if symbol not in (self.config.scatter_symbol, self.config.super_scatter_symbol)
                ]
            if not low_symbols:
                low_symbols = ["L1"]
            self._buy_filler_cycle = low_symbols
        return self._buy_filler_cycle

    def _is_valid_scatter_board(self) -> bool:
        """Ensure scatter placement rules are respected on natural boards."""
        scatter_positions = self.special_syms_on_board.get("scatter", [])
        super_positions = self.special_syms_on_board.get("super_scatter", [])

        if len(super_positions) > 1:
            return False

        scatter_reels = set()
        for pos in scatter_positions:
            reel = pos["reel"]
            if reel in scatter_reels:
                return False
            scatter_reels.add(reel)

        if not super_positions:
            return True

        super_reel = super_positions[0]["reel"]
        return all(pos["reel"] != super_reel for pos in scatter_positions)
