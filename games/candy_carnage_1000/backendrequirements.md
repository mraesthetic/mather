# Backend Requirements - Candy Carnage 1000

**Generated from actual frontend code analysis**

---

## Table of Contents
1. [API Endpoints](#1-api-endpoints)
2. [Book Events (Game State)](#2-book-events-game-state)
3. [Symbols](#3-symbols)
4. [Bet Modes](#4-bet-modes)
5. [Win Levels](#5-win-levels)
6. [Board Structure](#6-board-structure)
7. [Status Codes](#7-status-codes)

---

## 1. API Endpoints

### POST `/wallet/authenticate`

**Request:**
```json
{
  "sessionID": "uuid-string",
  "language": "en"
}
```

**Response:**
```json
{
  "status": {
    "statusCode": "SUCCESS",
    "statusMessage": "OK"
  },
  "balance": {
    "amount": 100000,
    "currency": "USD"
  },
  "round": {
    "roundID": 12345,
    "amount": 100,
    "payout": 0,
    "payoutMultiplier": 0,
    "active": true,
    "mode": "base",
    "event": "0",
    "state": []
  },
  "config": {
    "betLevels": [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000],
    "betModes": {
      "base": { "mode": "base", "costMultiplier": 1, "feature": false },
      "bonus_hunt": { "mode": "bonus_hunt", "costMultiplier": 3, "feature": false },
      "regular_buy": { "mode": "regular_buy", "costMultiplier": 100, "feature": true },
      "super_buy": { "mode": "super_buy", "costMultiplier": 500, "feature": true }
    },
    "defaultBetLevel": 100,
    "jurisdiction": {
      "socialCasino": false,
      "disabledFullscreen": false,
      "disabledTurbo": false,
      "disabledSuperTurbo": false,
      "disabledAutoplay": false,
      "disabledSlamstop": false,
      "disabledSpacebar": false,
      "disabledBuyFeature": false,
      "displayNetPosition": false,
      "displayRTP": false,
      "displaySessionTimer": false,
      "minimumRoundDuration": 0
    }
  }
}
```

---

### POST `/wallet/play`

**Request:**
```json
{
  "sessionID": "uuid-string",
  "amount": 100,
  "currency": "USD",
  "mode": "base"
}
```

**Response:**
```json
{
  "status": {
    "statusCode": "SUCCESS",
    "statusMessage": "OK"
  },
  "balance": {
    "amount": 99900,
    "currency": "USD"
  },
  "round": {
    "roundID": 12345,
    "amount": 100,
    "payout": 500,
    "payoutMultiplier": 5.0,
    "active": true,
    "mode": "base",
    "event": null,
    "state": [/* BookEvent[] */]
  }
}
```

---

### POST `/bet/event`

**Request:**
```json
{
  "sessionID": "uuid-string",
  "event": "5"
}
```

**Response:**
```json
{
  "event": "5",
  "status": {
    "statusCode": "SUCCESS",
    "statusMessage": "OK"
  }
}
```

---

### POST `/wallet/end-round`

**Request:**
```json
{
  "sessionID": "uuid-string"
}
```

**Response:**
```json
{
  "balance": {
    "amount": 100400,
    "currency": "USD"
  },
  "status": {
    "statusCode": "SUCCESS",
    "statusMessage": "OK"
  }
}
```

---

## 2. Book Events (Game State)

The `state` array contains ordered events that the frontend plays through sequentially.

### `reveal`
Initial board reveal after spin.

```typescript
{
  "index": 0,
  "type": "reveal",
  "board": [
    // 6 reels, each with 7 rows (1 top padding + 5 visible + 1 bottom padding)
    [
      { "name": "H1" },                    // padding row
      { "name": "L2" },                    // visible row 0
      { "name": "H3" },                    // visible row 1
      { "name": "S", "scatter": true },    // visible row 2 (scatter)
      { "name": "M", "multiplier": 5 },    // visible row 3 (bomb)
      { "name": "L1" },                    // visible row 4
      { "name": "H4" }                     // padding row
    ],
    // ... 5 more reels
  ],
  "paddingPositions": [0, 0, 0, 0, 0, 0],
  "anticipation": [0, 0, 0, 0, 0, 0],
  "gameType": "basegame"  // or "freegame"
}
```

**Notes:**
- `board` is 6 reels × 7 rows (includes 2 padding rows)
- `gameType` must be `"basegame"` or `"freegame"`
- Frontend ignores `anticipation` (always sets to all zeros)

---

### `winInfo`
Cluster win information.

```typescript
{
  "index": 1,
  "type": "winInfo",
  "totalWin": 250,
  "wins": [
    {
      "symbol": "H1",
      "win": 150,
      "positions": [
        { "reel": 0, "row": 1 },
        { "reel": 0, "row": 2 },
        { "reel": 1, "row": 1 }
      ],
      "meta": {
        "clusterMult": 1,
        "winWithoutMult": 150,
        "overlay": { "reel": 0, "row": 1 }
      }
    }
  ]
}
```

**Required fields in `meta`:**
- `clusterMult` - multiplier applied to cluster (1 if none)
- `winWithoutMult` - base win before multipliers
- `overlay` - position to show win amount popup

---

### `updateTumbleWin`
Updates running tumble win total (cumulative).

```typescript
{
  "index": 2,
  "type": "updateTumbleWin",
  "amount": 250
}
```

---

### `tumbleBoard`
Symbols explode and new symbols fall.

```typescript
{
  "index": 3,
  "type": "tumbleBoard",
  "explodingSymbols": [
    { "reel": 0, "row": 1 },
    { "reel": 0, "row": 2 },
    { "reel": 1, "row": 1 }
  ],
  "newSymbols": [
    // New symbols per reel (from top)
    [{ "name": "L3" }, { "name": "H2" }],
    [{ "name": "L1" }],
    [],
    [],
    [],
    []
  ]
}
```

---

### `boardMultiplierInfo`
Bomb multipliers applied to tumble win (free spins only).

```typescript
{
  "index": 4,
  "type": "boardMultiplierInfo",
  "multInfo": {
    "positions": [
      { "reel": 2, "row": 3, "multiplier": 8, "name": "M" },
      { "reel": 4, "row": 2, "multiplier": 5, "name": "M" }
    ]
  },
  "winInfo": {
    "tumbleWin": 1234,
    "boardMult": 13,
    "totalWin": 16042
  }
}
```

**Fields:**
- `tumbleWin` - win before bomb multipliers
- `boardMult` - sum of all bomb multipliers
- `totalWin` - final win (tumbleWin × boardMult)

---

### `freeSpinTrigger`
Free spins feature triggered by scatters.

```typescript
{
  "index": 5,
  "type": "freeSpinTrigger",
  "totalFs": 10,
  "positions": [
    { "reel": 1, "row": 2 },
    { "reel": 3, "row": 4 },
    { "reel": 4, "row": 1 },
    { "reel": 5, "row": 3 }
  ]
}
```

**Notes:**
- `positions` - scatter symbol positions that triggered the feature
- Frontend animates these positions before showing intro

---

### `enterBonus`
Signals actual bonus start (sent after `freeSpinTrigger`).

```typescript
{
  "index": 6,
  "type": "enterBonus",
  "reason": "regular"  // or "super"
}
```

---

### `updateFreeSpin`
Updates free spin counter.

```typescript
{
  "index": 7,
  "type": "updateFreeSpin",
  "amount": 3,
  "total": 10
}
```

---

### `freeSpinRetrigger`
Additional free spins awarded (3+ scatters during bonus).

```typescript
{
  "index": 8,
  "type": "freeSpinRetrigger",
  "totalFs": 15
}
```

**Note:** Frontend always shows "+5 FREE SPINS" popup

---

### `freeSpinEnd`
Free spins feature ended.

```typescript
{
  "index": 9,
  "type": "freeSpinEnd",
  "amount": 5000,
  "winLevel": 7
}
```

---

### `setWin`
Big win animation trigger.

```typescript
{
  "index": 10,
  "type": "setWin",
  "amount": 10000,
  "winLevel": 8
}
```

---

### `setTotalWin`
Sets total win amount.

```typescript
{
  "index": 11,
  "type": "setTotalWin",
  "amount": 500
}
```

---

### `finalWin`
Final win at end of round (triggers round completion).

```typescript
{
  "index": 12,
  "type": "finalWin",
  "amount": 10000
}
```

---

### `createBonusSnapshot`
Stores bonus events for resume (optional).

```typescript
{
  "index": 13,
  "type": "createBonusSnapshot",
  "bookEvents": [/* previous BookEvent[] */]
}
```

---

## 3. Symbols

### Symbol Object Structure

```typescript
{
  "name": "H1",           // Required - symbol identifier
  "multiplier": 5,        // Only for M (bomb) symbols
  "scatter": true         // Only for S and BS symbols
}
```

### Symbol Names

| Name | Type | Description |
|------|------|-------------|
| `H1` | High Pay | High symbol 1 |
| `H2` | High Pay | High symbol 2 |
| `H3` | High Pay | High symbol 3 |
| `H4` | High Pay | High symbol 4 |
| `L1` | Low Pay | Low symbol 1 |
| `L2` | Low Pay | Low symbol 2 |
| `L3` | Low Pay | Low symbol 3 |
| `L4` | Low Pay | Low symbol 4 |
| `L5` | Low Pay | Low symbol 5 |
| `M` | Bomb | Multiplier bomb (requires `multiplier` field) |
| `W` | Wild | Wild symbol |
| `S` | Scatter | Regular scatter (requires `scatter: true`) |
| `BS` | Super Scatter | Super scatter (requires `scatter: true`) |

### Bomb Multiplier Values

```typescript
// Valid multiplier values for M symbols:
[2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100, 500, 1000]
```

---

## 4. Bet Modes

| Mode | Cost Multiplier | Description |
|------|-----------------|-------------|
| `base` | 1× | Standard base game spin |
| `bonus_hunt` | 3× | Enhanced scatter frequency |
| `regular_buy` | 100× | Buy regular bonus (10 free spins) |
| `super_buy` | 500× | Buy super bonus (10 free spins with better bombs) |

**Frontend sends `mode` in `/wallet/play` request.**

---

## 5. Win Levels

| Level | Alias | Type | Animation |
|-------|-------|------|-----------|
| 1 | zero | small | None |
| 2 | standard | small | None |
| 3 | small | small | None |
| 4 | nice | medium | None |
| 5 | substantial | medium | None |
| 6 | big | big | Big win celebration |
| 7 | superwin | big | Super win celebration |
| 8 | mega | big | Mega win celebration |
| 9 | epic | big | Epic win celebration |
| 10 | max | big | Max win celebration |

**Used in:** `setWin.winLevel`, `freeSpinEnd.winLevel`

---

## 6. Board Structure

### Dimensions
- **Reels:** 6 (columns)
- **Visible Rows:** 5 per reel
- **Total Rows:** 7 per reel (1 top padding + 5 visible + 1 bottom padding)

### Position Mapping

```
Row 0: Top padding (not visible)
Row 1: Visible row 0 (top)
Row 2: Visible row 1
Row 3: Visible row 2
Row 4: Visible row 3
Row 5: Visible row 4 (bottom)
Row 6: Bottom padding (not visible)
```

**All positions in events use the full array index (including padding).**

---

## 7. Status Codes

| Code | Description |
|------|-------------|
| `SUCCESS` | Operation completed successfully |
| `ERR_SCR` | Invalid secret |
| `ERR_OPT` | Invalid operator ID |
| `ERR_IPB` | Insufficient player balance |
| `ERR_IS` | Invalid session / timeout |
| `ERR_ATE` | Authentication failed / expired |
| `ERR_GLE` | Gambling limits exceeded |
| `ERR_BNF` | Bet not found |
| `ERR_BE` | Player already has active bet |
| `ERR_UE` | Unknown server error (rollback) |
| `ERR_GE` | General server error (no rollback) |

---

## Example Event Sequences

### Base Game Win (No Feature)

```
1. reveal (gameType: "basegame")
2. winInfo (cluster wins)
3. updateTumbleWin
4. tumbleBoard (explode + new symbols)
5. [repeat 2-4 for each tumble]
6. setTotalWin
7. finalWin
```

### Feature Trigger

```
1. reveal (gameType: "basegame")
2. [optional tumbles]
3. freeSpinTrigger (4+ scatters)
4. enterBonus (reason: "regular" or "super")
5. [free spin sequence - see below]
6. freeSpinEnd
7. finalWin
```

### Free Spin Sequence

```
1. updateFreeSpin (current spin #, total)
2. reveal (gameType: "freegame")
3. winInfo
4. updateTumbleWin
5. boardMultiplierInfo (if bombs present)
6. tumbleBoard
7. [repeat 3-6 for each tumble]
8. [optional: freeSpinRetrigger if 3+ scatters]
9. [repeat for each spin]
```

### Buy Bonus

Same as Feature Trigger, but:
- Frontend sends `mode: "regular_buy"` or `mode: "super_buy"`
- `freeSpinTrigger.positions` should contain the clamped scatter positions
- No scatter payout before entering feature

---

## Amount Format

**All amounts are integers multiplied by 100.**

| Value | Meaning |
|-------|---------|
| 100 | $1.00 |
| 1000 | $10.00 |
| 10000 | $100.00 |

---

## Notes

1. **Max Win:** 25,000× bet
2. **Cluster Minimum:** 8 adjacent symbols
3. **Free Spins:** Always 10 initial spins
4. **Retrigger:** +5 spins per retrigger (3+ scatters)
5. **BS (Super Scatter):** Only appears in base game, max 1 per board

