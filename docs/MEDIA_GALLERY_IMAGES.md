# Media Gallery – What to Upload

Use these images in your Kaggle writeup **media gallery**. All paths are under `docs/` or `kaggle_submission_package/images/`.

---

## Recommended order (6 images)

Upload in this order so the story is clear: **overview → architecture → how it works → results**.

---

### 1. **Metrics dashboard** (lead image)
**File:** `docs/metrics_dashboard.png` or `kaggle_submission_package/images/metrics_dashboard.png`  
**Suggested caption:**  
*MedGemma AI Medical Triage System – 92.86% accuracy, 100% on EMERGENCY/URGENT/SEMI-URGENT/NON-URGENT, 6 agents, 7 enforcement layers.*

**Why first:** Single image that shows main result and structure. Good as the “hero” for the gallery.

---

### 2. **Architecture diagram**
**File:** `docs/architecture_diagram.png` or `kaggle_submission_package/images/architecture_diagram.png`  
**Suggested caption:**  
*Multi-agent architecture: 6 MedGemma agents (Intake → Symptom Assessment → Medical Knowledge → Urgency Classification → Care Recommendation → Communication) plus 7 enforcement layers.*

**Why:** Shows the agentic workflow and how agents connect.

---

### 3. **Enforcement flowchart**
**File:** `docs/enforcement_flowchart.png` or `kaggle_submission_package/images/enforcement_flowchart.png`  
**Suggested caption:**  
*Urgency classification pipeline: from patient input through 7 enforcement layers and 6 UNKNOWN checkpoints to final classification (92.86% accurate).*

**Why:** Explains how you get reliable, safe classifications.

---

### 4. **Category performance**
**File:** `docs/category_performance.png` or `kaggle_submission_package/images/category_performance.png`  
**Suggested caption:**  
*Accuracy by urgency category: 100% on EMERGENCY (3/3), URGENT (3/3), SEMI-URGENT (5/5), NON-URGENT (3/3); 50% on edge cases (1/2).*

**Why:** Backs up the “100% on critical categories” claim with a clear chart.

---

### 5. **Accuracy progression**
**File:** `docs/accuracy_progression.png` or `kaggle_submission_package/images/accuracy_progression.png`  
**Suggested caption:**  
*Accuracy improvement from 64.29% baseline to 92.86% (+28.57 pts) across development phases; 90% target exceeded.*

**Why:** Shows iteration and methodology, not just the final number.

---

### 6. **Confusion matrix**
**File:** `docs/confusion_matrix.png` or `kaggle_submission_package/images/confusion_matrix.png`  
**Suggested caption:**  
*Confusion matrix (expected vs actual urgency): strong diagonal; 13/14 correct; 1 edge case returns UNKNOWN.*

**Why:** Gives a quick, technical view of where the system succeeds and where it doesn’t.

---

## Optional 7th image

**File:** `docs/kaggle_writeup_card_560x280.png`  
**Suggested caption:**  
*Project card: MedGemma AI Medical Triage System – 92.86% accuracy, 6 agents, 7 enforcement layers.*

Use if the platform allows one more image and you want a compact “brand” shot (same as writeup thumbnail).

---

## Quick checklist

| # | Image                 | File name                     | Purpose              |
|---|-----------------------|-------------------------------|----------------------|
| 1 | Metrics dashboard     | `metrics_dashboard.png`        | Lead / overview      |
| 2 | Architecture diagram  | `architecture_diagram.png`    | Agentic workflow     |
| 3 | Enforcement flowchart | `enforcement_flowchart.png`   | Safety pipeline      |
| 4 | Category performance  | `category_performance.png`    | Results by category  |
| 5 | Accuracy progression  | `accuracy_progression.png`    | Improvement story   |
| 6 | Confusion matrix      | `confusion_matrix.png`        | Technical validation |

---

## Where the files are

- **In repo:** `docs/<filename>.png`
- **In submission zip:** `kaggle_submission_package/images/<filename>.png`

All are PNG, 300 DPI (except the 560×280 card). Use the same files for the writeup and for the media gallery.
