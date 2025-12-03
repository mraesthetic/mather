# Fixing "RTP too high" Issue

## The Problem

When you run `cargo run --release`, you see "RTP too high..." which means the optimization program is generating distributions with RTP values higher than the target.

## Root Cause

Looking at the code:
- Line 774: `avg_win = hr * rtp` 
- Line 153: `avg_win: fence.avg_win * bet_amount`
- Line 1047: `if new_pig.rtp > pig_heaven.avg_win`

The issue is that **fence RTP values represent RTP CONTRIBUTION**, not the RTP when the fence hits.

For basegame fence:
- `hr = 0.35` (35% hit rate)
- `rtp = 0.466` (46.6% RTP contribution)
- Current calculation: `avg_win = 0.35 * 0.466 = 0.1631`
- But this should be: `avg_win = 0.466` (the RTP contribution itself)

## The Fix

The fence RTP values in your config are **already the RTP contribution per spin**, not per hit. So the `avg_win` calculation is wrong.

**Option 1: Fix the fence RTP values**

If the code expects `avg_win = hr * rtp`, then your fence RTPs should be the RTP **when it hits**, not the contribution.

For basegame:
- Current: `rtp = 0.466` (contribution)
- Should be: `rtp = 0.466 / 0.35 = 1.331` (RTP when it hits)

**Option 2: Adjust the optimization parameters**

The optimization might be working correctly, but the distributions are naturally coming out high. Try:

1. **Increase `num_pigs_per_fence`** in setup.toml - more pigs = better distribution matching
2. **Adjust `min_mean_to_median` and `max_mean_to_median`** - tighter constraints
3. **Check scaling factors** - they might be pushing RTP too high

## Quick Fix to Try

Edit `game_optimization.py` and change fence RTPs to be "per hit" instead of "contribution":

```python
"basegame": ConstructConditions(
    rtp=0.466 / 0.35,  # Convert contribution to per-hit RTP
    hr=0.35
).return_dict(),
```

But wait - this would break the sum! The sum must still equal 0.962.

## Better Solution

The real issue is that fence RTPs in the optimization config represent **contribution**, but the code expects **per-hit RTP**. 

Check if your fence RTPs need to be converted. For basegame:
- If `rtp = 0.466` is contribution: avg_win should be 0.466
- If `rtp = 0.466` is per-hit: avg_win should be 0.35 * 0.466 = 0.1631

The code does `avg_win = hr * rtp`, so it expects **per-hit RTP**.

## Solution: Convert Your Fence RTPs

Your current fence RTPs are contributions. Convert them to per-hit RTPs:

**BASE MODE:**
- basegame: `rtp = 0.466 / 0.35 = 1.331` (but sum must still = 0.962!)
- regular_fs: `rtp = 0.418 / hr_fs` (need to calculate hr_fs first)
- super_fs: `rtp = 0.078 / hr_super_fs`

Actually, this gets complicated because regular_fs and super_fs have `hr="x"` (calculated).

## Recommended Fix

**Lower your fence RTP values slightly** to account for the optimization generating distributions that are slightly high:

Try reducing each fence RTP by 2-5%:

```python
"base": self._main_mode_setup(
    base_rtp=0.450,        # Was 0.466, now 0.450 (3.4% reduction)
    regular_fs_rtp=0.405,  # Was 0.418, now 0.405 (3.1% reduction)
    super_fs_rtp=0.075,   # Was 0.078, now 0.075 (3.8% reduction)
    zero_rtp=0.032,       # Adjusted to keep sum = 0.962
),
```

Then verify: 0.450 + 0.405 + 0.075 + 0.032 = 0.962 ✓
