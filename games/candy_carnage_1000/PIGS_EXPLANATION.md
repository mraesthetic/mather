# Understanding "Positive Pigs" and "Negative Pigs"

## What Are "Pigs"?

**"Pigs"** = Individual win distributions (probability distributions of wins)

The optimization algorithm generates thousands of these distributions and evaluates them to find the best ones.

## Positive vs Negative Pigs

### Positive Pigs (RTP Too High)
- **Definition**: Distributions where `pig.rtp > target_avg_win`
- **Meaning**: The distribution's average RTP is **higher** than the target
- **Example**: Target is 0.084, but pig generates 0.095 RTP → **Positive pig**

### Negative Pigs (RTP Too Low)  
- **Definition**: Distributions where `pig.rtp < target_avg_win`
- **Meaning**: The distribution's average RTP is **lower** than the target
- **Example**: Target is 0.084, but pig generates 0.075 RTP → **Negative pig**

## How The Algorithm Works

### Step 1: Generate Distributions
The algorithm generates `num_per_fence` distributions (e.g., 30,000) for each fence.

### Step 2: Categorize Pigs
For each generated distribution, it checks:
```rust
if new_pig.rtp > pig_heaven.avg_win {
    pos_pigs.push(new_pig);  // RTP too high
} else if new_pig.rtp < pig_heaven.avg_win {
    neg_pigs.push(new_pig);  // RTP too low
}
```

### Step 3: Need Both Types
The algorithm needs **BOTH** positive and negative pigs to create a balanced final distribution.

It needs at least `sqrt(num_pigs)` of each type:
- If `num_pigs = 30,000`, need ~173 positive pigs AND ~173 negative pigs

### Step 4: Combine Pigs
Once it has both types, it combines them with a weighted average:
```rust
weight = (target - neg_pig.rtp) / (pos_pig.rtp - neg_pig.rtp)
final_rtp = weight * pos_pig.rtp + (1 - weight) * neg_pig.rtp
```

This creates a distribution that hits the exact target RTP!

## Why "RTP Too High" Error Occurs

The error happens when:
- **Too many positive pigs** (RTP > target) are found
- **Not enough negative pigs** (RTP < target) are found

After generating `5 * num_pigs` distributions (150,000 in our case), if:
- `pos_pigs.len() > neg_pigs.len()` → **"RTP too high..."**
- `neg_pigs.len() > pos_pigs.len()` → **"RTP too low..."**

## How To Fix It

### Option 1: Lower the Target (What We Did)
By reducing fence RTPs dramatically:
- **Before**: Target avg_win = 0.35 * 0.466 = 0.163
- **After**: Target avg_win = 0.35 * 0.240 = 0.084

Lower target = easier to find distributions **above** it (positive pigs) AND **below** it (negative pigs)

### Option 2: Generate More Distributions
Increase `num_per_fence`:
- More distributions = more chances to find negative pigs
- We increased from 5,000 → 30,000

### Option 3: Remove Biases
Remove things that push RTP higher:
- Scaling factors (set to 1.0)
- Distribution bias (removed)

## Real Example

For **basegame** fence:
- **Hit Rate (HR)**: 0.35 (hits 35% of spins)
- **Fence RTP**: 0.240
- **Target avg_win**: 0.35 * 0.240 * 1.0 = **0.084**

The algorithm generates distributions and checks:
- Distribution A: avg RTP = 0.095 → **Positive pig** (too high)
- Distribution B: avg RTP = 0.075 → **Negative pig** (too low) ✓
- Distribution C: avg RTP = 0.092 → **Positive pig** (too high)
- Distribution D: avg RTP = 0.071 → **Negative pig** (too low) ✓

It needs many of both types to create the final balanced distribution!

## Summary

- **Positive pigs** = Distributions with RTP **above** target (easy to find)
- **Negative pigs** = Distributions with RTP **below** target (hard to find)
- **Problem**: Can't find enough negative pigs
- **Solution**: Lower targets, generate more distributions, remove biases

The algorithm combines positive and negative pigs to hit the exact target RTP!

