#!/usr/bin/env python3
"""Verify optimization configuration is correct"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from games.candy_carnage_1000.game_config import GameConfig
from games.candy_carnage_1000.game_optimization import OptimizationSetup

print("=" * 70)
print("VERIFYING CANDY CARNAGE 1000 OPTIMIZATION CONFIGURATION")
print("=" * 70)
print()

gc = GameConfig()
opt = OptimizationSetup(gc)

target_rtp = gc.rtp
print(f"Target Game RTP: {target_rtp:.4f} ({target_rtp*100:.2f}%)")
print()

errors = []
warnings = []

for mode_name, mode_config in gc.opt_params.items():
    print(f"{mode_name.upper()} MODE:")
    print("-" * 70)
    
    total_rtp = 0.0
    fence_details = []
    
    for fence_name, fence_config in mode_config['conditions'].items():
        rtp = fence_config.get('rtp', 0.0)
        hr = fence_config.get('hr', 'N/A')
        av_win = fence_config.get('av_win', None)
        
        # Skip wincap (special case)
        if fence_name == 'wincap':
            print(f"  {fence_name:15s} RTP: {rtp:6.3f} (special - win cap)")
            continue
            
        total_rtp += rtp
        rtp_pct = rtp * 100
        
        hr_str = str(hr) if hr != 'x' else 'calculated'
        fence_details.append((fence_name, rtp, hr_str))
        print(f"  {fence_name:15s} RTP: {rtp:6.3f} ({rtp_pct:5.1f}%)  HR: {hr_str}")
    
    print(f"  {'TOTAL':15s} RTP: {total_rtp:6.3f} ({total_rtp*100:5.1f}%)")
    print(f"  Target RTP:    {target_rtp:.4f} ({target_rtp*100:.2f}%)")
    
    diff = abs(total_rtp - target_rtp)
    if diff < 0.001:
        print("  ✅ CORRECT - Sum matches target!")
    else:
        error_msg = f"  ❌ ERROR - Sum is {total_rtp:.4f}, should be {target_rtp:.4f} (diff: {diff:.4f})"
        print(error_msg)
        errors.append(f"{mode_name}: {error_msg}")
    
    # Check scaling factors
    scaling = mode_config.get('scaling', [])
    if scaling:
        print("  Scaling Factors:")
        for scale in scaling:
            crit = scale.get('criteria', 'unknown')
            factor = scale.get('scale_factor', 1.0)
            win_range = scale.get('win_range', (0, 0))
            print(f"    {crit}: {factor:.2f}x for wins {win_range[0]}-{win_range[1]}")
            if factor > 1.2:
                warnings.append(f"{mode_name}/{crit}: High scaling factor {factor:.2f} may push RTP high")
    
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)

if errors:
    print("❌ ERRORS FOUND:")
    for error in errors:
        print(f"  {error}")
    print()
else:
    print("✅ All fence RTP sums match target!")
    print()

if warnings:
    print("⚠️  WARNINGS:")
    for warning in warnings:
        print(f"  {warning}")
    print()

print("Next Steps:")
print("1. Run: python3 build_math_config.py")
print("2. Run: cd optimization_program && cargo run --release")
print("3. Check output files in library/optimization_files/")
