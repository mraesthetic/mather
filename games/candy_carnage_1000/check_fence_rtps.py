#!/usr/bin/env python3
"""Check current fence RTP configuration"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from games.candy_carnage_1000.game_config import GameConfig
from games.candy_carnage_1000.game_optimization import OptimizationSetup

gc = GameConfig()
opt = OptimizationSetup(gc)

print('=' * 70)
print('CURRENT FENCE RTP CONFIGURATION FOR CANDY CARNAGE 1000')
print('=' * 70)
print()

for mode_name, mode_config in gc.opt_params.items():
    print(f'\n{mode_name.upper()} MODE:')
    print('-' * 70)
    total_rtp = 0.0
    for fence_name, fence_config in mode_config['conditions'].items():
        rtp = fence_config.get('rtp', 0.0)
        hr = fence_config.get('hr', 'N/A')
        total_rtp += rtp
        rtp_pct = rtp * 100
        print(f'  {fence_name:15s} RTP: {rtp:6.3f} ({rtp_pct:5.1f}%)  HR: {hr}')
    print(f'  {"TOTAL":15s} RTP: {total_rtp:6.3f} ({total_rtp*100:5.1f}%)')
    print(f'  Target RTP: {gc.rtp:.3f} ({gc.rtp*100:.1f}%)')
    if abs(total_rtp - gc.rtp) < 0.001:
        print('  ✅ CORRECT - Sum matches target!')
    else:
        print(f'  ❌ ERROR - Sum is {total_rtp:.3f}, should be {gc.rtp:.3f}')
    print()

print('=' * 70)
print('SUMMARY:')
print('=' * 70)
print(f'Game Target RTP: {gc.rtp:.3f} ({gc.rtp*100:.1f}%)')
print()
print('KEY POINTS:')
print('  • Fence RTPs are DECIMAL values (0.466 = 46.6%, NOT 466%)')
print('  • The SUM of all fence RTPs must equal the target RTP')
print('  • HR = "x" means hit rate is calculated automatically')
print('  • Individual fences can have RTP > 1.0, but weighted sum = target')
print()
print('To modify fence RTPs, edit game_optimization.py:')
print('  - Change values in _main_mode_setup()')
print('  - Ensure sum always equals target RTP (0.962)')
