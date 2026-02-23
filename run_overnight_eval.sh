#!/bin/bash
# Overnight evaluation script
# Run with: ./run_overnight_eval.sh

cd "/Users/shenry/Documents/Personal/Training/Project/Kaggle/MedGemma Impact Challenge"

# Activate virtual environment
source venv/bin/activate

# Record start time
echo "========================================" | tee overnight_eval.log
echo "Evaluation started at: $(date)" | tee -a overnight_eval.log
echo "========================================" | tee -a overnight_eval.log
echo "" | tee -a overnight_eval.log

# Run evaluation with full output logging
python run_evaluation.py 2>&1 | tee -a overnight_eval.log

# Record end time
echo "" | tee -a overnight_eval.log
echo "========================================" | tee -a overnight_eval.log
echo "Evaluation completed at: $(date)" | tee -a overnight_eval.log
echo "========================================" | tee -a overnight_eval.log

# Display summary
echo "" | tee -a overnight_eval.log
echo "Results saved to:" | tee -a overnight_eval.log
echo "  - data/evaluation_results_improved.csv" | tee -a overnight_eval.log
echo "  - data/evaluation_summary_improved.json" | tee -a overnight_eval.log
echo "  - overnight_eval.log (this file)" | tee -a overnight_eval.log
echo "" | tee -a overnight_eval.log

# Extract key metrics if evaluation completed
if [ -f "data/evaluation_summary_improved.json" ]; then
    echo "Quick Summary:" | tee -a overnight_eval.log
    python3 -c "
import json
try:
    with open('data/evaluation_summary_improved.json', 'r') as f:
        data = json.load(f)
        metrics = data.get('metrics', {})
        print(f\"  Overall Accuracy: {metrics.get('overall_accuracy', 'N/A'):.2f}%\")
        print(f\"  Emergency Accuracy: {metrics.get('emergency_accuracy', 'N/A'):.2f}%\")
        print(f\"  Urgent Accuracy: {metrics.get('urgent_accuracy', 'N/A'):.2f}%\")
        print(f\"  Semi-Urgent Accuracy: {metrics.get('semi_urgent_accuracy', 'N/A'):.2f}%\")
        print(f\"  Non-Urgent Accuracy: {metrics.get('non_urgent_accuracy', 'N/A'):.2f}%\")
except Exception as e:
    print(f\"  Could not parse results: {e}\")
" | tee -a overnight_eval.log
fi

echo ""
echo "Done! Check overnight_eval.log for full details."
