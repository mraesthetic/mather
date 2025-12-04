# Simple Explanation: Why "RTP Too High" Happens

## The Core Problem (Super Simple)

The optimization algorithm is like trying to balance a scale:

```
     [Positive Pigs]  vs  [Negative Pigs]
     (RTP > target)       (RTP < target)
```

**It needs BOTH sides to balance!**

Right now, it's finding tons of positive pigs but can't find enough negative pigs.

## What's Actually Happening

### Step 1: Set a Target
For basegame fence:
- Hit Rate = 0.35 (hits 35% of spins)
- Fence RTP = 0.240
- **Target avg_win = 0.35 × 0.240 = 0.084**

### Step 2: Generate Distributions
The algorithm generates 30,000 distributions and checks each one:

```
Distribution #1: RTP = 0.095 → ABOVE target (0.084) → Positive pig ✓
Distribution #2: RTP = 0.092 → ABOVE target (0.084) → Positive pig ✓
Distribution #3: RTP = 0.088 → ABOVE target (0.084) → Positive pig ✓
Distribution #4: RTP = 0.090 → ABOVE target (0.084) → Positive pig ✓
Distribution #5: RTP = 0.087 → ABOVE target (0.084) → Positive pig ✓
...
Distribution #5000: RTP = 0.085 → ABOVE target (0.084) → Positive pig ✓
Distribution #5001: RTP = 0.083 → BELOW target (0.084) → Negative pig ✓ (FINALLY!)
Distribution #5002: RTP = 0.091 → ABOVE target (0.084) → Positive pig ✓
...
```

### Step 3: The Problem
After generating 150,000 distributions:
- Found: 500 positive pigs ✓
- Found: 5 negative pigs ✗ (NEED 173!)

**Result**: "RTP too high..." because not enough negative pigs!

## Why Can't It Find Negative Pigs?

The distributions are **naturally** generating RTPs that are too high. This could be because:

1. **The target is still too high** - Even at 0.240 fence RTP, the generated distributions tend to be higher
2. **Scaling factors** - Even at 1.0, there might be other biases pushing RTP up
3. **Distribution generation algorithm** - The way it creates distributions might naturally favor higher RTPs

## The Solution (What We've Been Doing)

### Option 1: Lower the Target Even More ✅
Reduce fence RTPs so low that it becomes easier to find distributions below target:
- base_rtp: 0.240 → 0.200 (or even 0.150)
- This makes the target lower, so more distributions will be "above" it (negative pigs)

Wait, that doesn't make sense... Let me think again.

Actually:
- **Lower target** = easier to find distributions **above** target (positive pigs)
- **Lower target** = easier to find distributions **below** target (negative pigs) too!

The issue is the **ratio**. We're getting way more positive than negative.

### Option 2: Generate WAY More Distributions ✅
- Increase `num_per_fence` from 30,000 → 100,000
- More distributions = more chances to find those rare negative pigs

### Option 3: Remove ALL Biases ✅
- Already removed scaling factors (set to 1.0)
- Already removed distribution bias
- Maybe there are other hidden biases?

## The Real Question

**Why are the generated distributions consistently above the target?**

Possible reasons:
1. The distribution generation algorithm has a built-in bias toward higher RTPs
2. The win ranges available don't allow for low enough RTPs
3. The target calculation is wrong somehow

## What To Do Right Now

1. **Try even lower fence RTPs:**
   - base_rtp: 0.240 → **0.180** (25% lower)
   - regular_fs_rtp: 0.220 → **0.180** (18% lower)
   - super_fs_rtp: 0.045 → **0.040** (11% lower)

2. **Increase num_per_fence:**
   - 30,000 → **100,000** (3x more distributions)

3. **Check if there's a minimum RTP constraint** - Maybe distributions can't physically go below a certain RTP due to win ranges?

## Bottom Line

The algorithm needs BOTH:
- Distributions with RTP > target (positive pigs) ✓ Easy to find
- Distributions with RTP < target (negative pigs) ✗ Hard to find

We're stuck because we can't find enough negative pigs. The solution is to either:
- Lower the target so much that negative pigs become easier to find
- Generate so many distributions that we eventually find enough negative pigs
- Figure out why distributions can't go below the target and fix that

