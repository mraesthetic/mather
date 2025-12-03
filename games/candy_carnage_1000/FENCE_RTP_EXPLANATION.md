# Fence RTP Explanation for Candy Carnage 1000

## What Are Fence RTPs?

**Fences** are different types of outcomes in your game. Each fence has:
- **RTP**: Return to Player (as a decimal, e.g., 0.466 = 46.6%)
- **HR**: Hit Rate (how often it occurs, e.g., 0.35 = 35% of spins)
- **Avg Win**: Average win amount when it hits

## How It Works

The **total game RTP** is calculated as:
```
Total RTP = Sum of (Fence RTP × Weight)
```

Where weight is based on hit rate (HR).

## Your Current Configuration

### BASE MODE (Target: 96.2% = 0.962)

| Fence Name | RTP (decimal) | RTP (%) | HR | Notes |
|------------|---------------|---------|----|----|
| wincap | 0.0 | 0% | - | Max win cap |
| zero | 0.0 | 0% | 0.0 | Dead spins |
| basegame | 0.466 | 46.6% | 0.35 | Regular base game wins |
| regular_fs | 0.418 | 41.8% | "x" | Regular free spins (calculated) |
| super_fs | 0.078 | 7.8% | "x" | Super free spins (calculated) |
| **TOTAL** | **0.962** | **96.2%** | | ✅ Matches target |

### BONUS HUNT MODE (Target: 96.2% = 0.962)

| Fence Name | RTP (decimal) | RTP (%) | HR | Notes |
|------------|---------------|---------|----|----|
| wincap | 0.0 | 0% | - | Max win cap |
| zero | 0.123 | 12.3% | 0.0 | Dead spins |
| basegame | 0.188 | 18.8% | 0.35 | Regular base game wins |
| regular_fs | 0.54 | 54.0% | "x" | Regular free spins (calculated) |
| super_fs | 0.111 | 11.1% | "x" | Super free spins (calculated) |
| **TOTAL** | **0.962** | **96.2%** | | ✅ Matches target |

### REGULAR BUY & SUPER BUY MODES
- Both have single fence with RTP = 0.962 (96.2%)
- This is correct since buy modes guarantee the feature

## Important Notes

1. **RTP values are DECIMALS**: 
   - 0.466 = 46.6% (NOT 466%)
   - 0.962 = 96.2% (NOT 962%)

2. **HR = "x" means**: Hit rate is calculated automatically based on:
   - How often the feature triggers
   - The RTP target for that fence

3. **The formula**: `avg_win = HR × RTP × bet_amount`
   - For basegame: avg_win = 0.35 × 0.466 × 1.0 = 0.1631

4. **Why fence RTPs can be > 100%**: 
   - Individual fences CAN have RTP > 1.0 (100%)
   - But they're weighted by hit rate
   - The WEIGHTED SUM must equal 96.2%

## If You're Seeing "140%" Somewhere

You might be:
- Looking at hit rates (HR) instead of RTP
- Multiplying RTP by 100 incorrectly (0.418 × 100 = 41.8%, not 418%)
- Looking at average win amounts instead of RTP
- Seeing a different metric (like multiplier values)

## How to Adjust Fence RTPs

Edit `game_optimization.py`:

```python
"base": self._main_mode_setup(
    base_rtp=0.466,        # Change this
    regular_fs_rtp=0.418, # Change this
    super_fs_rtp=0.078,    # Change this
    zero_rtp=0.0,          # Change this
),
```

**CRITICAL**: The sum MUST equal 0.962 (96.2%)

Example to get 96.2%:
- base_rtp + regular_fs_rtp + super_fs_rtp + zero_rtp = 0.962
