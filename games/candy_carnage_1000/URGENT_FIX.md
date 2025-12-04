# URGENT FIX - Still Getting "RTP Too High"

## What I Just Changed

Reduced fence RTPs **EVEN MORE DRAMATICALLY**:

**BASE MODE:**
- base_rtp: 0.240 → **0.150** (-37.5% more reduction!)
- regular_fs_rtp: 0.220 → **0.150** (-32% more reduction!)
- super_fs_rtp: 0.045 → **0.030** (-33% more reduction!)
- zero_rtp: 0.457 → **0.632** (adjusted to keep sum = 0.962)
- **Total still = 0.962** ✓

## New Target Values

For **basegame** fence:
- Old target: 0.35 × 0.240 = **0.084**
- New target: 0.35 × 0.150 = **0.0525** (37.5% lower!)

This should make it MUCH easier to find distributions below the target.

## Why It's Still Failing

Looking at the distribution generation code (line 970):
```rust
mus.push(f64::max(
    v * pig_heaven.avg_win + 0.01 * random_value2 * pig_heaven.max_win,
    pig_heaven.min_win,
));
```

The mean is based on `v * avg_win`, so lower avg_win = lower means = easier to find negative pigs.

## Next Steps

1. **REBUILD CONFIG** (CRITICAL!):
   ```bash
   cd /Users/anthony/Downloads/math-sdk-4/games/candy_carnage_1000
   python3 run.py
   ```

2. **Run optimization again:**
   ```bash
   cd /Users/anthony/Downloads/math-sdk-4/optimization_program
   cargo run --release
   ```

## If STILL Failing

We might need to go even lower:
- base_rtp: 0.150 → **0.100**
- regular_fs_rtp: 0.150 → **0.100**
- super_fs_rtp: 0.030 → **0.020**

Or there might be a fundamental issue with the distribution generation algorithm that prevents low RTPs.

## The Real Problem

Even with 200k distributions, if the algorithm **physically cannot** generate distributions below a certain RTP (due to min_win constraints or the generation formula), it will never find negative pigs.

We might need to check if there's a minimum win constraint preventing low RTPs.

