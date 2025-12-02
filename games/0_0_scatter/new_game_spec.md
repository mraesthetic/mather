# Core Game Model

- **Grid:** 6 × 5.
- **Model:** All-ways scatter pays; no fixed paylines (Sweet Bonanza–style).
- **Mechanics:** Cascading/tumbling reels after every win, free spins with multiplier bombs, two bonus types (Regular and Super FS).
- **RTP Target (per mode):** 96.2% ± 0.5%.
- **Max Win:** 25,000× bet (hard engine cap).
- **Volatility:** Very high (aligned with Sweet Bonanza 1000).

---

# Bet Modes

| Mode | Description | Cost | Entry Behavior | Notes |
| --- | --- | --- | --- | --- |
| `base` | Standard base game with natural free-spin triggers. | 1× | Draw from BR0.csv | Baseline mode. |
| `bonus_hunt` | Scatter-heavier base variant; more frequent regular FS, slightly drier base hits. | 1× | Draw from BR_HUNT.csv | Same overall RTP as `base`. |
| `regular_buy` | Direct entry to Regular Free Spins. | 100× | Clamped board with exactly 4×S (no BS) before FS; no scatter payout. | All RTP from FS session. |
| `super_buy` | Direct entry to Super Free Spins. | 500× | Clamped board with exactly 3×S + 1×BS; no scatter payout. | All RTP from FS session. |

Each mode must individually converge to ≈96.2% RTP after tuning.

---

# Symbol Set

- **Paying symbols:** H1–H4 (high), L1–L5 (low).
- **Scatters:** `S` (regular) and `BS` (super). `BS` also counts toward scatter totals/payouts but only appears in base modes.
- **Wilds / blockers / bombs:** None on the reels. Bombs are generated objects during free spins only.
- **Total distinct symbols:** 11.

---

# Base-Game Paytable Thresholds

Scatter-pay thresholds across the 6×5 grid:

| Threshold | Count | Notes |
| --- | --- | --- |
| `t1` | 8–9 | Minimum win count. |
| `t2` | 10–11 | Mid tier. |
| `t3` | 12–36 | Top tier (12+). |

Paytable (multipliers of base bet):

| Symbol | `t1` | `t2` | `t3` |
| --- | --- | --- | --- |
| H1 | 10.0 | 25.0 | 50.0 |
| H2 | 2.5 | 10.0 | 25.0 |
| H3 | 2.0 | 5.0 | 15.0 |
| H4 | 1.5 | 2.0 | 12.0 |
| L1 | 1.0 | 1.5 | 10.0 |
| L2 | 0.8 | 1.2 | 8.0 |
| L3 | 0.5 | 1.0 | 5.0 |
| L4 | 0.4 | 0.9 | 4.0 |
| L5 | 0.25 | 0.75 | 2.0 |

Only these three thresholds exist (no `t4`).

---

# Base-Game Targets (Feel & Stats)

For `mode="base"`:

- Overall hit rate (incl. cascades): 30–35%.
- Average cascades per winning spin: 1.6–2.0.
- Avg. payout on winning spins: 0.8–1.2× bet.
- RTP composition: base contributes ≈62%; remainder from free spins (regular + super).
- Tuning levers: reel symbol weights, scatter densities.

---

# Reel Strips & Scatter Density

- **BR0.csv (base mode):**
  - Scatter counts per reel ≈ [9, 9, 8, 8, 7, 6].
  - Minimum spacing of 5 symbols between scatters per reel.
  - Reels 1–3: swap ~12% of lows into H2/H3/H4 for higher hit quality.

- **BR_HUNT.csv (bonus_hunt):**
  - Scatter counts per reel ≈ [12, 11, 11, 11, 9, 9].
  - Same 5-symbol spacing.
  - Reels 1–4 are scatter heavy; reels 5–6 convert ~10% highs back into lows.

- **Free-spin reels:** FR0.csv and WCAP.csv remain as defined in existing math books.

Whenever reel CSVs change, rebuild lookup tables/books before simulations.

---

# Scatter Trigger Logic

- **Minimum scatters:** 4 total (S and/or BS) anywhere on the board.

Feature routing:

1. **Super Free Spins (natural)**  
   - Trigger: 3+ `S` plus exactly 1 `BS` (only one `BS` can appear).  
   - Overrides regular FS if both conditions are met.  
   - Awards Super FS package.

2. **Regular Free Spins (natural)**  
   - Trigger: 4–6 scatters with no `BS`.  
   - Awards 10 free spins.

Bonus buys override triggers with clamped entry boards (see Bet Modes section) and do **not** pay scatter wins.

---

# Scatter Payouts

- 4 scatters: trigger only, no payout.
- 5 scatters: 5× bet.
- 6 scatters: 100× bet.
- `BS` counts toward total scatter count for payouts.
- Order of resolution: pay scatter win → enter feature.
- Bonus buys skip scatter payouts (boards are clamped).

---

# Free Spins – Shared Rules

- **Spin counts:** Regular and Super FS both start with 10 spins (tunable later).
- **Tumble mechanics:** Same as base (scatter pays anywhere, cascading).
- **Retriggers:** 3+ `S` during FS awards +5 spins (flat). No `BS` in bonuses.
- **Super scatters:** Base-only, for triggering Super FS.

---

# Bomb Mechanics – General

- Bombs exist only in free-spin modes.
- Bombs can appear on any tumble (winning or dead). On dead tumbles they are purely visual.
- On winning tumbles: sum all bomb multipliers and multiply the tumble’s total win by this sum.
- Bombs do not occupy reel positions and have no standalone payout.

---

# Regular Free Spins – Bomb Distribution

Multiplier set: `{2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100, 500, 1000}`

Example weights (to normalize later):

| Mult | Weight |
| --- | --- |
| 2× | 430 |
| 3× | 360 |
| 4× | 300 |
| 5× | 280 |
| 6× | 240 |
| 8× | 180 |
| 10× | 135 |
| 12× | 115 |
| 15× | 95 |
| 20× | 55 |
| 25× | 15 |
| 50× | 4 |
| 100× | 1.0 |
| 500× | 0.2 |
| 1000× | 0.03 |

Behavior targets:

- Winning tumbles spawn bombs ~40–50% of the time.
- When bombs spawn: ~80% single-bomb, ~20% multi-bomb.
- Distribution shape: ≈70% low bombs, 25% mid, 5% high+.

---

# Super Free Spins – Bomb Distribution

Multiplier set: `{20, 25, 50, 100, 500, 1000}`

Example weights:

| Mult | Weight |
| --- | --- |
| 20× | 420 |
| 25× | 250 |
| 50× | 70 |
| 100× | 22 |
| 500× | 2.5 |
| 100× | 0.4 |

Behavior targets:

- Winning tumbles spawn bombs ~60–70% of the time.
- Bomb-count mix: ~60% single, 30% double, 10% triple+.
- High bombs (100×/500×/1000×) are rare but frequently teased, including on dead boards.

---

# Bonus Buy Economics

| Mode | Cost | Target EV | Entry Pattern | RTP Source |
| --- | --- | --- | --- | --- |
| `regular_buy` | 100× | 95.7–96.7× | Exactly 4×S, no BS; no scatter pay | Entirely from Regular FS session |
| `super_buy` | 500× | 481–490× | Exactly 3×S + 1×BS; no scatter pay | Entirely from Super FS session |

Tuning levers: bomb frequency/distribution, retrigger rate, FS reel symbol mix.

---

# Bonus Hunt Mode Details

- Regular FS trigger frequency target: ~1 in 70 spins (≈1.4%).
- Base hit rate ≈30% but slightly drier than normal to preserve volatility.
- `BS` frequency identical to normal mode (same per-reel counts; positions differ).
- Approximate RTP composition:
  - **Normal mode:** 58–62% base hits, 26–30% regular FS, ~8% super FS.
  - **Bonus hunt:** ~45% base hits, ~51% free spins (mostly regular, some super).
- Implementation: `mode="bonus_hunt"` bet mode flag, BR_HUNT reels, bespoke distribution tuning.

---

# Win Bucket Targets (Optimizer Guidance)

**Base/Normal spins (≈62% RTP slice):**

- 0× spins: 30–35% of spins (0% RTP slice).
- 0–1×: ~10% of RTP slice.
- 1–5×: ~20%.
- 5–20×: ~14%.
- 20–50×: ~6%.
- 50–100×: ~2%.

**Regular Free Spins slice:**

- 0–20×: ~10%.
- 20–50×: ~20%.
- 50–100×: ~25%.
- 100–250×: ~25%.
- 250–500×: ~15%.
- 500–1000×: ~4%.
- 1000–25,000×: ~1%.

**Super Free Spins slice:**

- 0–50×: 5–8%.
- 50–100×: 10–15%.
- 100–250×: ~25%.
- 250–500×: ~25%.
- 500–1000×: ~20%.
- 1000–2,500×: ~7%.
- 2,500–25,000×: 2–3%.

These are optimization targets, not rigid code constraints.

---

# Max Win Logic

- Cap: 25,000× bet (includes any scatter pay prior to entering feature).
- When cumulative feature payout ≥25,000×:
  - Immediately end the feature.
  - Lock total win at exactly 25,000×.
- Design expectation: requires near full-board H1 + huge bombs in Super FS.
- Provide ≥5 scripted max-win scenarios for QA/marketing.

---

# Notes & Open Items

- Bomb logic implementation (spawn rules per tumble, multi-bomb aggregation).
- Free-spin reel specifics (FR0, WCAP) assumed to be inherited from math books; confirm adjustments needed.
- Optimization program must honor mode-specific RTP splits and bucket targets.
- Dedicated documentation (this file) should remain the source of truth for future math/engine work.

