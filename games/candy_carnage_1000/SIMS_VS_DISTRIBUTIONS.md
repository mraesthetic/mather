# Simulations vs Distributions - The Key Difference

## Two Different Phases

### Phase 1: GENERATION (Finding Positive/Negative Pigs) ⚠️ THIS IS WHERE IT FAILS
- **Parameter**: `num_per_fence` (currently 200,000)
- **What it does**: Generates random distributions (pigs)
- **When it happens**: FIRST, before testing
- **What it checks**: Is this pig's RTP above or below target?
  - If RTP > target → Positive pig ✓
  - If RTP < target → Negative pig ✓
- **The problem**: After generating 1,000,000 distributions (5 × 200k), it still can't find enough negative pigs
- **Error location**: Line 1096 - happens DURING generation, not testing

### Phase 2: TESTING (Evaluating Quality) ✅ THIS WORKS FINE
- **Parameter**: `sim_trials` (currently 3,000)
- **What it does**: Tests the QUALITY of already-generated distributions
- **When it happens**: AFTER generation, only on distributions that passed Phase 1
- **What it checks**: How well does this distribution perform in simulations?
- **The problem**: This phase never gets to run because Phase 1 fails!

## Why More Simulations Won't Help

```
Step 1: GENERATE distributions (num_per_fence = 200k)
   ├─ Distribution #1: RTP = 0.095 → Positive pig ✓
   ├─ Distribution #2: RTP = 0.092 → Positive pig ✓
   ├─ Distribution #3: RTP = 0.088 → Positive pig ✓
   ├─ ...
   ├─ Distribution #150,000: RTP = 0.085 → Positive pig ✓
   └─ ❌ ERROR: Can't find enough negative pigs!
   
Step 2: TEST distributions (sim_trials = 3k) ← NEVER REACHES HERE!
   └─ Would test the positive pigs we found
```

**The error happens in Step 1, so Step 2 never runs!**

## What Actually Helps

### ✅ Increasing `num_per_fence` (What We Did)
- Generates MORE distributions
- More chances to find negative pigs
- We increased to 200,000 (was 30,000)

### ✅ Lowering Target RTP (What We Did)
- Makes it easier to find distributions BELOW target
- We reduced fence RTPs dramatically

### ❌ Increasing `sim_trials` (Won't Help)
- Only tests distributions AFTER they're found
- Doesn't help find negative pigs
- The error happens BEFORE testing

## The Real Issue

Even with 200k distributions, the algorithm is generating distributions that are **consistently above the target**. This suggests:

1. **The target is still too high** - Even at 0.150 fence RTP, distributions are still > target
2. **There's a minimum constraint** - Maybe distributions can't physically go below a certain RTP due to `min_win` or other constraints
3. **The generation formula** - Line 970: `v * avg_win + 0.01 * max_win` might naturally favor higher values

## What To Do

1. **Lower fence RTPs even more** (we just did: 0.150, 0.150, 0.030)
2. **Check if there's a min_win constraint** preventing low RTPs
3. **Generate even more distributions** (increase num_per_fence to 500k?)

**Increasing sim_trials won't help** because the error happens during generation, not testing!

