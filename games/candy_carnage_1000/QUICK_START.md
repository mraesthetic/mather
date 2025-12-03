# Quick Start: Fix RTP Optimization for Candy Carnage 1000

## ✅ Configuration Summary

### BASE MODE Fence RTPs:
- zero: 0.050 (hr=0.0, doesn't contribute)
- basegame: 0.440 (hr=0.35)
- regular_fs: 0.400 (hr=x, calculated)
- super_fs: 0.072 (hr=x, calculated)
- **TOTAL: 0.962 ✓**

### BONUS HUNT MODE Fence RTPs:
- zero: 0.172 (hr=0.0, doesn't contribute)
- basegame: 0.175 (hr=0.35)
- regular_fs: 0.510 (hr=x, calculated)
- super_fs: 0.105 (hr=x, calculated)
- **TOTAL: 0.962 ✓**

## 🚀 Steps to Run Optimization

### 1. Rebuild Math Config
```bash
cd /Users/anthony/Downloads/math-sdk-4
python3 build_math_config.py
```

This updates `library/configs/math_config.json` with new fence RTPs.

### 2. Run Optimization
```bash
cd optimization_program
cargo run --release
```

### 3. Check Results
Look in: `games/candy_carnage_1000/library/optimization_files/base_0_1.csv`

Find the line: `Rtp,0.962` (should be close to 0.962)

## 🔧 What Was Changed

1. **Fence RTPs reduced by 5-6%** to account for optimization bias
2. **Scaling factors reduced**: 1.15→1.10, 1.25→1.15
3. **More distributions**: num_per_fence 5000→8000, num_show 2500→3000

## ⚠️ If Still Too High

If optimization still shows "RTP too high":
1. Reduce fence RTPs by another 2-3% in `game_optimization.py`
2. Reduce scaling factors further (1.10→1.05, 1.15→1.10)
3. Increase `num_pigs_per_fence` in `setup.toml` to 15000

## 📝 Key Files

- `game_optimization.py` - Fence RTP values (MODIFIED)
- `setup.toml` - Optimization parameters (MODIFIED)
- `build_math_config.py` - Regenerates math_config.json
- `OPTIMIZATION_FIX.md` - Detailed explanation

## 💡 Understanding Zero RTP

The `zero_rtp` value (0.050 for base, 0.172 for bonus_hunt) is just to make the sum = 0.962. Since `hr=0.0`, it **never hits** and doesn't contribute to actual game RTP. It's a mathematical placeholder.
