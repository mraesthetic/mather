# Candy Carnage 1000 – Frontend Data Contract

This document enumerates every payload the engine emits for **Candy Carnage 1000** so the client can safely parse a spin, bonus, and buy-bonus flow.  All win amounts that reach the client are integer cents (value × 100) and every board is 6 reels × 5 rows with padding rows enabled. The canonical frontend requirements live in `games/candy_carnage_1000/backendrequirements.md`; this file is a condensed reference that stays in lockstep with that spec.

---

## 1. Bet Modes and Entry Assumptions

| Mode name | Cost | Entry behaviour | Notes |
|-----------|------|-----------------|-------|
| `base` | 1x bet | Natural scatters only | Uses `BR0.csv` reels, regular RTP mix |
| `bonus_hunt` | 3x bet | Natural scatters only | Uses `BR_HUNT.csv` (higher scatter density) |
| `regular_buy` | 100x bet | Clamped board with exactly 4×`S`, 0×`BS` | No scatter payout; jumps straight into regular free spins |
| `super_buy` | 500x bet | Clamped board with 3×`S` + 1×`BS` | No scatter payout; jumps straight into super free spins |

- Pass these names to `/spin?mode=<name>` or equivalent.  
- RTP target per mode is 96.2 % with a hard cap of 25,000× bet (`wincap`).

---

## 2. Symbol Legend

| Symbol | Meaning | Extra data in payloads |
|--------|---------|------------------------|
| `H1`–`H4` | High symbols | none |
| `L1`–`L5` | Low symbols | none |
| `S` | Regular scatter | appears in base and bonuses; positions listed in triggers |
| `BS` | Super scatter | base game only; at most one per board; never shares a reel with `S` |
| `M` | Bomb overlay used in free spins | emitted through `boardMultiplierInfo` with a `value` |

The JSON board positions expose symbol names plus any attributes listed in `special_symbols` (`scatter`, `super_scatter`, `bomb`). Padding rows are included because `include_padding = True`.

---

## 3. Board / Reveal Payload

`reveal` (type `reveal`) always arrives first for a spin:

```json
{
  "type": "reveal",
  "board": [ [ { "name": "L3" }, ... ], ... ],   // 6 columns
  "paddingPositions": [ {"reel":0,"row":15}, ... ],
  "gameType": "basegame" | "freegame",
  "anticipation": bool
}
```

- Each column already includes the top/bottom padding rows (the engine prepends/appends them).  
- Scatter validation guarantees **max one scatter per reel** and at most one `BS` overall.

---

## 4. Event Timeline

### 4.1 Base Spin (no feature)
1. `reveal`
2. `winInfo` *(per tumble that produces a win)* – includes win entries, cluster positions, optional `meta.winWithoutMult`.
3. `setTumbleWin` / `updateTumbleWin` – running tumble win meters.
4. `tumbleBoard` – exploding positions + new symbols.
5. Repeat steps 2–4 until no more wins.
6. `setWin` – cumulative spin win (only emitted in basegame context).
7. `setTotalWin` – cumulative bet-mode win (also only emitted in basegame context).
8. `finalWin` – final payout multiplier for the spin.

### 4.2 Feature Trigger (natural spins)
When 4+ scatters are present:

1. `freeSpinTrigger`
2. `enterBonus` with `{"reason": "regular"|"super"}` once the feature actually starts.
3. Scatter payouts (5× on 5 scatters, 100× on 6) are applied before entering the feature, except buy modes.

### 4.3 Free-Spin Loop
For both regular and super bonuses we now emit the exact cadence the frontend requested:

1. `updateFreeSpin` – `amount` starts at 1 and increments each spin, `total` already includes any retriggers.
2. `reveal` (`gameType: "freegame"`).
3. Per tumble (if there is a win): `winInfo` → `updateTumbleWin` *(pre-bomb amount)* → `boardMultiplierInfo` (bombs drop onto the live board) → a second `updateTumbleWin` that reflects the multiplied total → `tumbleBoard`.
4. On 3+ scatters: `freeSpinRetrigger` with updated `totalFs`.
5. After the last spin: `freeSpinEnd`, then `finalWin`. We do **not** emit `setWin` / `setTotalWin` inside the feature anymore; those are reserved for base spins per §4.1.

Retriggers use only `S` symbols (no `BS` in bonuses) and add +5 spins, capped via the configured retrigger distribution (max 20 spins total).

---

## 5. Bomb / Multiplier Event

Bombs exist only during free spins. The event payload is:

```json
{
  "type": "boardMultiplierInfo",
  "multInfo": {
    "positions": [
      { "reel": 2, "row": 4, "multiplier": 8, "name": "M" },
      ...
    ]
  },
  "winInfo": {
    "tumbleWin": 1234,      // base tumble win in cents
    "boardMult": 25,        // sum of bomb multipliers on the tumble
    "totalWin": 30850       // tumbleWin * boardMult, capped at wincap
  }
}
```

- Rows already account for padding (`row = actual_row + 1`).  
- `winInfo.tumbleWin` is the pre-bomb amount, `totalWin` is the post-bomb amount.  
- Individual `winInfo` entries inside `winInfo` events also gain `meta.winWithoutBombs` when bombs apply so the UI can animate pre/post values.

Buy-bonus spins reuse the same event but pull bomb odds from `buy_bomb_settings`.

---

## 6. Lookup Tables and Books

For each mode we output:

- `books_<mode>.jsonl.zst`: array of per-spin books, with keys:
  - `id` – sequential spin number.
  - `events` – ordered list described above.
  - `baseGameWins`, `freeGameWins`, `payoutMultiplier`.
- `lookUpTable_<mode>_0.csv`: `id,weight,payoutMultiplier` rows (weight defaults to 1 until optimizer rewrites it). These must match the `payoutMultiplier` in `books_*` when uploading; if you regenerate books, copy the fresh lookup file before publishing.

---

## 7. Miscellaneous Contract Notes

- **Game types:** the `gameType` field inside events is either `"basegame"` or `"freegame"`. Use it to decide HUD layout.
- **Anticipation:** `reveal.anticipation` flips to `True` when the current scatter count is one less than the configured trigger threshold.
- **Max win:** when cumulative win hits 25,000×, the engine emits `wincap` and terminates the feature immediately.
- **Retrigger cap telemetry:** the engine samples a retrigger cap per bonus; there is no explicit event for the cap, but `updateFreeSpin.total` shows the ceiling after each retrigger.
- **Mode display names:** surface strings like “Base Game”, “Bonus Hunt”, “Regular Buy (100×)”, “Super Buy (500×)” on the frontend, but requests must use the lowercase IDs in §1.

This file should give the client everything required to deserialize spins, bonuses, board multipliers, and lookup data for QA/publishing. Let me know if you need sample payloads or storyboard diagrams alongside this spec.


