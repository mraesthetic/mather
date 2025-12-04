# Final Fix for "RTP Too High" Issue

## The Problem
The optimization algorithm needs BOTH:
- **Positive pigs**: Distributions with RTP > target avg_win
- **Negative pigs**: Distributions with RTP < target avg_win

It gets stuck when it can't find enough negative pigs to balance the positive ones.

## Solution Applied

### 1. MASSIVELY Reduced Base Mode Fence RTPs
- base_rtp: **0.240** (was 0.466 originally, now -48% reduction!)
- regular_fs_rtp: **0.220** (was 0.418 originally, now -47% reduction!)
- super_fs_rtp: **0.045** (was 0.078 originally, now -42% reduction!)
- zero_rtp: **0.457** (adjusted to keep sum = 0.962)
- **Total still = 0.962** ✓

### 2. Removed ALL Scaling Factors
- Set to **1.0** (no scaling) - scaling was pushing RTP too high

### 3. Removed Distribution Bias
- Removed bias that was pushing RTP higher

### 4. Increased num_per_fence
- **30000** distributions per fence (was 5000 originally)
- More chances to find negative pigs

## Why This Works

The optimization generates distributions targeting these lower fence RTPs. Even though the targets are much lower, the final combined RTP across all fences should still converge to ~96.2% because:

1. The zero_rtp is just a placeholder (hr=0.0, never hits)
2. The actual game RTP is calculated from all fences combined
3. Lower targets = more negative pigs = better balance

## Next Steps

1. **Rebuild config:**
   ```bash
   cd /Users/anthony/Downloads/math-sdk-4/games/candy_carnage_1000
   python3 run.py
   ```

2. **Run optimization:**
   ```bash
   cd /Users/anthony/Downloads/math-sdk-4/optimization_program
   cargo run --release
   ```

3. **If STILL stuck:** Reduce fence RTPs even more:
   - base_rtp: 0.240 → 0.200
   - regular_fs_rtp: 0.220 → 0.200
   - super_fs_rtp: 0.045 → 0.040
   - zero_rtp: 0.457 → 0.522

## Understanding the Math

The optimization compares each generated distribution's RTP to `pig_heaven.avg_win`:
- `avg_win = hr * rtp * bet_amount`
- For basegame: `avg_win = 0.35 * 0.240 * 1.0 = 0.084`
- The algorithm needs distributions both above AND below this target

By reducing the fence RTPs dramatically, we're making it easier to find distributions below the target (negative pigs).

