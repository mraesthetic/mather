## Candy Carnage 1000 — Ideal Specification

This document captures the math + gameplay requirements we are targeting before locking the final build. Treat it as the source of truth for tuning, instrumentation, and optimizer expectations.

---

### 1. Game Structure
- 6 reels × 5 visible rows, 1-row padding above/below (include padding in events).
- Cascade/tumble mechanic; wins clear, drop from reelstrips, refill from padding.
- Base-game only (no bombs/retrigs) except when a free-spin feature is in progress.
- Feature entry via scatters (`S`) or super scatter (`BS`).
- Scatter placement rule: **max one scatter per reel** at all times (base, free, tumbles, buys). Duplicates must be replaced before emitting events.

---

### 2. Bet Modes & RTP Split Targets

| Mode        | Cost | Base RTP | Regular FS RTP | Super FS RTP | Notes |
|-------------|------|----------|----------------|--------------|-------|
| base        | 1x   | 0.6000   | 0.3400         | 0.0220       | Zero fence disabled |
| bonus_hunt  | 3x   | 0.3000   | 0.6000         | 0.0620       | Dividing by cost yields 0.962 total |
| regular_buy | 100x | 0.0385   | 0.9235         | 0.0000       | >95% RTP from free spins |
| super_buy   | 500x | 0.0200   | 0.0000         | 0.9420       | Bomb-heavy, no base contribution |

- Optimizer fences must align with the above (no zero fence unless explicitly reintroduced).
- Hit-rate (HR) inputs for PigFarm:
  - Base regular: **1 / 190** (per-spin).
  - Base super: **1 / 1500**.
  - Bonus_hunt regular: **1 / 70**.
  - Bonus_hunt super: **1 / 900**.

---

### 3. Scatter & Reel Distribution
- `BR0.csv` (base) target counts per reel (visible + padding combined):
  - S: `[8, 7, 6, 4, 3, 2]`
  - BS: `[0, 0, 1, 1, 2, 2]`
- `FR0.csv` (feature) includes dense bomb + retrigger-friendly scatter placement (at least 1 scatter per reel, ideally 2 every other reel to sustain retriggers while staying under max spins).
- Buy-entry boards must be seeded with `S/BS` according to mode spec and must randomize fillers (no striped boards).

---

### 4. Free-Spin Mechanics

**Triggering:**
- Base game: 4+ `S` for regular, `BS + ≥3 S` for super (upgrade requirement = 3).
- Bonus hunt uses same logic but reel strips increase scatter density.
- No forced global multiplier; bombs drive multipliers exclusively.

**Initial spin counts:**
- Regular: 12 spins.
- Super: 12 spins plus bomb-heavy FR reelset.

**Retriggers:**
- Require ≥3 regular scatters during feature.
- Grant +7 spins; capped at total 30 spins.
- Retrigger probability distribution (CDF): `(0:0.45, 1:0.75, 2:0.92, 3:0.985, 4:1.0)`; buys override caps (regular buy allows 2 retrigs, super buy allows 1).

**Bomb Settings (during features):**
- Regular FS:
  - Appearance: 68%.
  - Counts: `{1:40, 2:40, 3:15, 4:5}`.
  - Multipliers: `[2–500]` weighted toward low/mid but including 75, 100, 250, 500, 1000.
- Super FS:
  - Appearance: 78%.
  - Counts: `{1:32, 2:33, 3:20, 4:10, 5:5}`.
  - Multipliers: `[20–1000]` with heavy weight on 20–50 but long tail to 1000.
- Buy bonuses reuse `buy_bomb_settings` (high appearance, flatter mid-tier multipliers).

**Bomb application sequence:**
1. Evaluate tumble win.
2. Sum bomb multipliers present on board for that tumble.
3. Multiply tumble win by the summed value.
4. Send `boardMultiplierInfo` after `winInfo`/`updateTumbleWin`, before `tumbleBoard`.
5. Mark bombs with `explode` attribute so they clear.

---

### 5. Scatter / Bomb Visibility Rules
- `reveal` payloads must include `multiplier` for bomb symbols.
- Bomb symbols are placed directly on the board (no invisible bombs).
- Every board (base or free) must be validated for unique scatter columns before events are emitted.
- During tumbles, any new scatter falling onto a reel that already contains an active scatter must be immediately replaced with a filler symbol (`_dedupe_scatter_columns`).

---

### 6. Simulator Configuration
- `run.py` defaults:
  - `num_threads = rust_threads = 8`, `batching_size = 2500`.
  - `num_sim_args = {"base": 15000, others: 0}` for quick iterations.
  - Set `OPTIMIZER_MODE=1` when generating data for PigFarm (forces distribution quotas to match fence targets). Set `0` to get natural math baselines.
- Before running PigFarm, always:
  1. `make run GAME=candy_carnage_1000` (with `OPTIMIZER_MODE=1`).
  2. Confirm `library/configs/math_config.json` shows the correct fence order and HR values.
  3. Run `cargo run --release -- ../games/candy_carnage_1000/optimization/setup.json` with `bet_type` set accordingly.

---

### 7. Analyzer / Format Requirements
- Analyzer (pay splits, symbol hits) should tolerate free wins in base fence (assertion removed).
- Format checks rely on quantized payouts (0.1 increments). Ensure `_0` LUT publish files stay in sync (`write_configs` already copies lookup tables when missing).
- No `ERR_MATH_OUTSIDE_RANGE` once `_0` LUTs mirror the optimized tables.

---

### 8. Frontend Contract Highlights
- Event order in free spins: `updateFreeSpin → reveal → winInfo → updateTumbleWin → boardMultiplierInfo → tumbleBoard`.
- `enterBonus` must include `reason` = `regular` or `super`.
- `boardMultiplierInfo` should contain each bomb’s reel/row + multiplier so the UI can animate.
- No global multiplier events.

---

### 9. Outstanding Targets for the Revamp
- Base mode natural math: ~0.60 base RTP, ~0.36 free RTP once new bomb/retrigger math is tuned.
- Regular free-spin trigger rate: 1 in 180–200 spins (base), 1 in 70 (bonus hunt).
- Super trigger rate: 1 in 1500 (base), 1 in 900 (bonus hunt).
- Free-spin average payout per trigger must reach ~60× to satisfy the regular fence target.
- After math tuning, rerun PigFarm to polish (expect small adjustments only).

---

Use this spec to cross-check every future change (reels, bomb tables, optimizer input, pipeline). If a knob isn’t listed above, call it out before implementing so we can keep this document authoritative.***


