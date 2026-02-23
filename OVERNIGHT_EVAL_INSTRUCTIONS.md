# Overnight Evaluation Instructions

## 🌙 Running the Evaluation Tonight

The evaluation will take approximately **3-4 hours** to complete all 14 test scenarios.

### Step 1: Start the Evaluation

Run this command in your terminal:

```bash
cd "/Users/shenry/Documents/Personal/Training/Project/Kaggle/MedGemma Impact Challenge"
nohup ./run_overnight_eval.sh > /dev/null 2>&1 &
```

**Or** if you want to see it running:

```bash
cd "/Users/shenry/Documents/Personal/Training/Project/Kaggle/MedGemma Impact Challenge"
./run_overnight_eval.sh
```

The script will save all output to `overnight_eval.log`.

### Step 2: In the Morning - Check Results

1. **Check if it's done:**
   ```bash
   tail -20 overnight_eval.log
   ```

2. **View the summary:**
   ```bash
   cat overnight_eval.log | grep -A 10 "SUMMARY"
   ```

3. **Check the detailed results:**
   - `data/evaluation_results_improved.csv` - All scenario results
   - `data/evaluation_summary_improved.json` - Performance metrics

## 📊 What to Look For

### Success Criteria:
- ✅ **Overall Accuracy ≥ 70%** (vs. baseline 21.4%)
- ✅ **Emergency Accuracy = 100%** (maintain safety)
- ✅ **No false negatives on critical cases**

### Expected Improvements:
- **URGENT**: 0% → 66-100%
- **SEMI-URGENT**: 33% → 66-100%  
- **NON-URGENT**: 0% → 66-100%
- **EMERGENCY**: 100% (maintained)

## 🔧 What Was Implemented

### 1. **Severity-Aware Red Flag Detection**
   - Split flags into CRITICAL (auto-EMERGENCY) vs WARNING (context-dependent)
   - Added severity scoring based on keywords
   - Fixed false positive detection from AI-generated text

### 2. **Enhanced Prompts**
   - Added concrete examples for each urgency level
   - Included decision criteria and severity checklists
   - Few-shot learning examples

### 3. **Improved Classification Logic**
   - CRITICAL flags → automatic EMERGENCY
   - WARNING flags → suggest minimum urgency, let AI decide final level
   - No flags → full AI reasoning

## 📝 Next Steps (Morning)

### If Accuracy ≥ 70%:
1. ✅ Update performance dashboard with new metrics
2. ✅ Generate new visualizations
3. ✅ Update kaggle_submission_package
4. ✅ Submit to Kaggle!

### If Accuracy < 70%:
1. Review overnight_eval.log for patterns
2. Adjust temperature settings
3. Refine prompts based on failure cases
4. Run targeted fixes on problem categories

## 🐛 Troubleshooting

If the evaluation failed or stopped:

1. **Check the log:**
   ```bash
   grep "ERROR" overnight_eval.log
   ```

2. **Check progress:**
   ```bash
   grep "Testing:" overnight_eval.log | wc -l
   ```
   Should show 14 lines when complete.

3. **Resume if needed:**
   Just run the script again - it will create new results.

## 💾 Files Created

- `overnight_eval.log` - Full evaluation output
- `data/evaluation_results_improved.csv` - Detailed per-scenario results
- `data/evaluation_summary_improved.json` - Aggregate metrics

---

**Estimated completion time:** 3-4 hours
**Started:** Check overnight_eval.log for timestamp
**Status:** Run `ps aux | grep run_evaluation` to check if still running
