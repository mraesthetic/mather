# How to Run and Verify Optimization

## Quick Run (Recommended)

### Option 1: Using Makefile (Easiest)
```bash
cd /Users/anthony/Downloads/math-sdk-4
make run GAME=candy_carnage_1000
```

This will:
1. Build math config
2. Run simulations
3. Run optimization for all modes
4. Generate analysis

### Option 2: Direct Python Script
```bash
cd /Users/anthony/Downloads/math-sdk-4/games/candy_carnage_1000
python3 run.py
```

### Option 3: Just Optimization (Fastest)
```bash
cd /Users/anthony/Downloads/math-sdk-4

# Step 1: Rebuild math config with new fence RTPs
python3 build_math_config.py

# Step 2: Run optimization for specific mode
cd games/candy_carnage_1000
python3 -c "
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution

config = GameConfig()
OptimizationSetup(config)
OptimizationExecution().run_opt_single_mode(config, 'base', 8)
"
```

## Verify Results

### Check Output CSV Files

After optimization completes, check the RTP in the output files:

```bash
# Check base mode RTP
cat games/candy_carnage_1000/library/optimization_files/base_0_1.csv | grep "^Rtp,"

# Check bonus_hunt mode RTP  
cat games/candy_carnage_1000/library/optimization_files/bonus_hunt_0_1.csv | grep "^Rtp,"

# Or view full file
cat games/candy_carnage_1000/library/optimization_files/base_0_1.csv
```

**Expected Output:**
```
Rtp,0.962
```
(or close to 0.962, like 0.960-0.964)

### What to Look For

1. **RTP Value**: Should be around 0.962 (96.2%)
2. **Score**: Higher is better (optimization quality metric)
3. **No Errors**: Should not see "RTP too high..." repeatedly

### Example Output File Structure

```
Name,Pig1
Score,0.95
LockedUpRTP,
Rtp,0.962
[distribution data...]
```

## Troubleshooting

### If you see "RTP too high..." errors:

1. **Check current fence RTPs**:
   ```bash
   python3 games/candy_carnage_1000/verify_config.py
   ```

2. **Reduce fence RTPs further** in `game_optimization.py`:
   - Reduce each by 2-3%
   - Adjust `zero_rtp` to keep sum = 0.962

3. **Reduce scaling factors**:
   - Change `1.10` → `1.05`
   - Change `1.15` → `1.10`

### If RTP is too low (<95.9%):

1. **Increase fence RTPs** by 1-2%
2. **Increase scaling factors** slightly
3. **Check if optimization completed** - may need more `num_per_fence`

## Quick Verification Script

Create a simple check script:

```bash
#!/bin/bash
cd /Users/anthony/Downloads/math-sdk-4

echo "Checking optimization results..."
for mode in base bonus_hunt; do
    file="games/candy_carnage_1000/library/optimization_files/${mode}_0_1.csv"
    if [ -f "$file" ]; then
        rtp=$(grep "^Rtp," "$file" | cut -d',' -f2)
        echo "$mode: RTP = $rtp"
        if (( $(echo "$rtp > 0.959 && $rtp < 0.965" | bc -l) )); then
            echo "  ✅ GOOD (within 95.9%-96.5%)"
        else
            echo "  ⚠️  OUT OF RANGE"
        fi
    else
        echo "$mode: File not found - optimization may not have run"
    fi
done
```

Save as `check_rtp.sh`, make executable: `chmod +x check_rtp.sh`, then run: `./check_rtp.sh`

## Files Generated

After running, you'll find:

- **Optimization results**: `library/optimization_files/{mode}_0_{n}.csv`
- **Lookup tables**: `library/publish_files/lookUpTable_{mode}_0.csv`
- **Math config**: `library/configs/math_config.json` (updated)

## Running Individual Modes

To run optimization for just one mode, edit `run.py`:

```python
target_modes = ["base"]  # Only run base mode
# or
target_modes = ["bonus_hunt"]  # Only run bonus_hunt mode
```

Then run: `python3 run.py`
