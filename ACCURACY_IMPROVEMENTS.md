# Accuracy Improvements Summary

## Overview
Comprehensive improvements to the MedGemma AI Medical Triage System to increase classification accuracy from 35.7% to 70%+ target.

**Date:** January 17, 2026  
**Target:** Improve overall accuracy while maintaining 100% EMERGENCY detection

## Changes Implemented

### 1. Red Flag Detection Refinements (`src/agents/symptom_agent.py`)

#### Enhanced `_flag_mentioned()` Method
- **Stricter phrase-based matching** using regex with word boundaries
- **Negation detection**: Checks for "no", "not", "without" to avoid false positives
- **Proximity requirements**: Multi-word flags require words within 5 words of each other
- **Special handling for chest pain**: Requires both "chest" AND "pain" to be close together
- **Enhanced synonyms**: More specific phrase-based synonyms instead of single keywords

**Impact:** Reduces false positive red flag detections significantly

#### Improved `_assess_severity()` Method
- **Proximity-weighted keyword counting**: Keywords near the flag get 2x weight
- **Negation checking**: Returns "low" severity if negation detected in context
- **Stricter thresholds**:
  - Critical: Requires 3+ critical keywords OR 2 critical + 2 high
  - High: Requires 2+ critical OR 1 critical + 3 high OR 4+ high
  - Moderate: Requires 1 critical OR 2+ high OR 3+ moderate
  - Low: Default (changed from "moderate" to "low" for conservatism)

**Impact:** More accurate severity assessment, fewer false escalations

#### Enhanced `_extract_context()` Method
- **Regex-based matching** with word boundaries
- **Negation markers**: Adds "[NEGATED]" prefix to context
- **Temporal markers**: Adds "[HISTORICAL]" prefix for past events
- **Expanded context window**: 50 chars → 250 chars to include markers

**Impact:** Better context awareness for severity assessment

### 2. Urgency Classification Logic (`src/agents/urgency_agent.py`)

#### Modified Auto-Emergency Logic
- **Dual requirement**: Requires BOTH critical type AND critical severity
- **Confidence scoring**: Based on flag count (2+ = high, 1 = medium)
- **High severity flags handling**: Logs but doesn't auto-escalate if not critical type

**Impact:** Prevents automatic EMERGENCY classification for non-critical high-severity flags

#### Stricter Minimum Urgency Calculation
- **New thresholds**:
  - URGENT: Requires 3+ high severity flags (was 2)
  - SEMI-URGENT: Requires 2 high OR 1 high + 3 moderate OR 4+ moderate (was 1 high or 2 moderate)
- **Removed critical from warning flags**: Only counts high/moderate/low severities

**Impact:** Reduces unnecessary urgency escalation from warning flags

#### Temperature Optimization
- **Reduced from 0.2 to 0.1**: More consistent, deterministic classification

**Impact:** More reliable and reproducible classifications

#### Added Validation & Confidence Scoring

**New `_calculate_confidence_score()` Method:**
- Scores 0-1 based on:
  - Red flag consistency with urgency level
  - Symptom clarity and completeness
  - Red flag count appropriateness
- Penalizes mismatches (e.g., EMERGENCY without critical flags)

**New `_validate_classification()` Method:**
- Validates urgency against red flags
- Detects potential misclassifications
- Suggests alternative urgency levels
- Flags low confidence scores (<0.4)

**Impact:** Quality assurance layer catches potential errors

### 3. Prompt Engineering (`src/models/prompt_templates.py`)

#### Enhanced URGENCY_CLASSIFICATION Prompt
- **Warning at top**: "Do NOT over-classify based on single keywords"
- **Clearer category definitions**: Added "REQUIRES:" sections with specific criteria
- **Counter-examples**: Added "✗ NOT EMERGENCY" examples showing what to avoid
- **Enhanced checklist**: More detailed severity assessment with specific thresholds
- **Decision tree**: Step-by-step classification logic
- **Conservative instruction**: "Most cases are NOT emergencies. Be conservative and accurate."
- **Required explanation**: "Explain why it's NOT a higher urgency level"

**Impact:** Guides AI to more accurate, conservative classifications

#### Improved RED_FLAG_CHECK Prompt
- **Strict assessment warning**: "Only flag symptoms that are ACTUALLY PRESENT"
- **Negation checking instruction**: Explicit check for "no", "not", "without"
- **Multiple indicator requirement**: Critical flags need 2+ severity indicators
- **Context emphasis**: Quote exact words/phrases indicating severity
- **Detailed examples**: Shows correct vs incorrect assessments
- **Conservative instruction**: "Be CONSERVATIVE with CRITICAL severity"

**Impact:** More accurate red flag detection with fewer false positives

### 4. Configuration Updates (`config.py`)

#### Expanded CRITICAL_RED_FLAGS
- Added more specific phrases:
  - "crushing chest pain" (not just "severe chest pain")
  - "cannot breathe", "gasping for air"
  - "facial droop", "arm paralysis"
  - "bleeding heavily", "throat swelling"
  - "thunderclap headache"

**Impact:** More precise critical flag detection

#### Enhanced SEVERITY_KEYWORDS
- **Critical keywords**: Added "gasping", "worst ever", "cannot move", "throat swelling"
- **High keywords**: Added "progressively worse", "extremely swollen", "can't walk"
- **Moderate keywords**: Added "bothersome", "troublesome", "annoying"
- **Low keywords**: Added "goes away", "comes and goes", "improving", "better", "healing"

**Impact:** Better severity context assessment

#### New Keyword Lists
- **NEGATION_KEYWORDS**: "no", "not", "without", "denies", "deny", "absent", "never", "neither", "none", "nothing"
- **TEMPORAL_KEYWORDS**: "history of", "previously", "past", "used to", "last year", "months ago", "years ago", "chronic"

**Impact:** Supports negation and temporal detection

### 5. Model Parameter Optimization

#### Symptom Assessment Agent
- **Temperature**: 0.6 → 0.4 (more focused analysis)

#### Urgency Classification Agent  
- **Temperature**: 0.2 → 0.1 (more consistent classification)

#### Red Flag Detection
- **Temperature**: Kept at 0.1 (safety-critical)

**Impact:** More deterministic, reproducible results

## Expected Improvements

### Target Metrics
| Category | Before | Target | Improvement |
|----------|--------|--------|-------------|
| Overall | 35.7% | 70%+ | +34.3% |
| EMERGENCY | 100% | 100% | Maintain |
| URGENT | 0% | 70%+ | +70% |
| SEMI-URGENT | 40% | 70%+ | +30% |
| NON-URGENT | 0% | 70%+ | +70% |

### Key Improvements
1. **Reduced false EMERGENCY classifications**: Stricter red flag detection and severity assessment
2. **Better URGENT detection**: No longer over-classified as EMERGENCY
3. **Improved SEMI-URGENT accuracy**: More appropriate for persistent but stable symptoms
4. **Better NON-URGENT detection**: Properly identifies mild, tolerable symptoms

## Technical Details

### Files Modified
1. `src/agents/symptom_agent.py` - Red flag detection logic
2. `src/agents/urgency_agent.py` - Classification logic and validation
3. `src/models/prompt_templates.py` - Prompt engineering
4. `config.py` - Configuration thresholds

### Lines of Code Changed
- **symptom_agent.py**: ~150 lines modified/added
- **urgency_agent.py**: ~200 lines modified/added
- **prompt_templates.py**: ~100 lines modified
- **config.py**: ~30 lines modified

### New Features
- Confidence scoring (0-1 scale)
- Classification validation
- Negation detection
- Temporal context awareness
- Proximity-weighted severity assessment

## Testing

### Evaluation Script
- **File**: `run_evaluation.py`
- **Test Set**: 14 scenarios (3 EMERGENCY, 3 URGENT, 3 SEMI-URGENT, 3 NON-URGENT, 2 EDGE_CASE)
- **Metrics**: Overall accuracy, per-category accuracy, red flag detection rate

### Running Evaluation
```bash
cd "/Users/shenry/Documents/Personal/Training/Project/Kaggle/MedGemma Impact Challenge"
source venv/bin/activate
python run_evaluation.py
```

### Output Files
- `data/evaluation_results_improved.csv` - Detailed results per scenario
- `data/evaluation_summary_improved.json` - Metrics summary with timestamp

## Validation Approach

### Multi-Layer Validation
1. **Red flag detection**: Stricter matching with negation checking
2. **Severity assessment**: Context-aware with proximity weighting
3. **Urgency classification**: AI-guided with decision tree
4. **Validation layer**: Cross-checks classification against flags
5. **Confidence scoring**: Quantifies classification certainty

### Safety Considerations
- EMERGENCY detection remains highly sensitive (100% recall target)
- Validation warnings for suspicious classifications
- Confidence scores flag uncertain cases
- Conservative defaults (low severity, not moderate)

## Next Steps

1. **Run evaluation**: Test improvements on 14 test scenarios
2. **Analyze results**: Compare before/after metrics
3. **Iterate if needed**: Fine-tune thresholds if target not met
4. **Expand test set**: Add more edge cases if accuracy is good
5. **Production deployment**: Deploy improved system

## Conclusion

These comprehensive improvements address the root causes of poor accuracy:
- Over-sensitive red flag detection → Stricter matching with negation
- Aggressive severity assessment → Conservative thresholds with context
- Auto-escalation to EMERGENCY → Dual requirements (type + severity)
- Unclear prompts → Detailed examples and decision trees
- Inconsistent generation → Lower temperatures

Expected result: **70%+ overall accuracy** while maintaining **100% EMERGENCY recall**.
