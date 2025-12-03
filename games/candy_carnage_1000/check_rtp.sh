#!/bin/bash
# Quick script to check RTP results after optimization

cd "$(dirname "$0")/../.."

echo "=========================================="
echo "Checking Optimization RTP Results"
echo "=========================================="
echo ""

for mode in base bonus_hunt; do
    file="games/candy_carnage_1000/library/optimization_files/${mode}_0_1.csv"
    if [ -f "$file" ]; then
        rtp=$(grep "^Rtp," "$file" | cut -d',' -f2)
        echo "📊 $mode mode:"
        echo "   RTP = $rtp ($(echo "$rtp * 100" | bc -l | xargs printf "%.2f")%)"
        
        # Check if within acceptable range (95.9% - 96.5%)
        if (( $(echo "$rtp >= 0.959 && $rtp <= 0.965" | bc -l) )); then
            echo "   ✅ GOOD (within target range 95.9%-96.5%)"
        elif (( $(echo "$rtp > 0.965" | bc -l) )); then
            echo "   ⚠️  TOO HIGH (above 96.5%)"
        else
            echo "   ⚠️  TOO LOW (below 95.9%)"
        fi
        echo ""
    else
        echo "❌ $mode: File not found"
        echo "   Path: $file"
        echo "   Run optimization first!"
        echo ""
    fi
done

echo "=========================================="
echo "Done!"
echo "=========================================="
