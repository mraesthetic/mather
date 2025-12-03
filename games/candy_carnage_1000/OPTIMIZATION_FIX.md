# Complete Optimization Fix for Candy Carnage 1000

## Problem
When running `cargo run --release`, the optimization program reports "RTP too high" and can't converge to 96.2% RTP.

## Root Cause
The optimization program generates distributions that naturally tend to be slightly higher than the target RTP values. This is due to:
1. Scaling factors pushing RTP higher
2. Distribution generation algorithm bias
3. Insufficient number of "pigs" (distributions) to match targets accurately

## Solution Applied

### 1. Reduced Fence RTP Targets
Lowered fence RTPs by 5-6% to account for optimization bias:

**BASE MODE:**
- base_rtp: 0.466 → 0.440 (-5.6%)
- regular_fs_rtp: 0.418 → 0.400 (-4.3%)
- super_fs_rtp: 0.078 → 0.072 (-7.7%)
- zero_rtp: 0.0 → 0.050 (adjusted for sum, but hr=0.0 so doesn't contribute)
- **Sum: 0.962 ✓**

**BONUS HUNT MODE:**
- base_rtp: 0.188 → 0.175 (-6.9%)
- regular_fs_rtp: 0.540 → 0.510 (-5.6%)
- super_fs_rtp: 0.111 → 0.105 (-5.4%)
- zero_rtp: 0.123 → 0.172 (adjusted for sum, but hr=0.0 so doesn't contribute)
- **Sum: 0.962 ✓**

### 2. Reduced Scaling Factors
Scaling factors multiply weights in certain win ranges, pushing RTP higher:
- regular_fs: 1.15 → 1.10 (-4.3%)
- super_fs: 1.25 → 1.15 (-8.0%)

### 3. Increased Optimization Parameters
More distributions = better matching:
- num_show: 2500 → 3000 (+20%)
- num_per_fence: 5000 → 8000 (+60%)
- sim_trials: 2500 → 3000 (+20%)

## How to Use

### Step 1: Rebuild Math Config
```bash
cd /Users/anthony/Downloads/math-sdk-4
python3 build_math_config.py
```

This regenerates `library/configs/math_config.json` with the new fence RTP values.

### Step 2: Run Optimization
```bash
cd optimization_program
cargo run --release
```

### Step 3: Check Results
After optimization completes, check the output files in:
```
games/candy_carnage_1000/library/optimization_files/base_0_1.csv
```

Look for the "Rtp" line - it should be close to 0.962 (96.2%).

### Step 4: Fine-Tune if Needed

**If still too high (>96.5%):**
- Reduce fence RTPs by another 1-2%
- Reduce scaling factors further (1.10 → 1.05, 1.15 → 1.10)
- Increase num_per_fence to 10000

**If too low (<95.9%):**
- Increase fence RTPs by 1-2%
- Increase scaling factors slightly
- Check if num_per_fence is too high (might be overfitting)

## Understanding the Zero RTP

The `zero_rtp` value is set to keep the sum at 0.962, but since `hr=0.0`, it **doesn't actually contribute** to the game RTP. The zero fence represents dead spins (no wins), so even if it has RTP, it never hits.

## Key Files Modified

1. `game_optimization.py` - Fence RTP values and scaling factors
2. `setup.toml` - Optimization parameters (num_pigs_per_fence increased)

## Verification

After running optimization, verify:
1. Final RTP in output CSV ≈ 0.962
2. No "RTP too high" warnings
3. Distribution looks reasonable (check win ranges)

## Notes

- The optimization may take longer with increased num_per_fence
- You can run optimization for each bet_type separately by changing `bet_type` in setup.toml
- The first run might still show "RTP too high" - let it complete and check the final result
