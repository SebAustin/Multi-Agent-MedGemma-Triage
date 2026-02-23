# What to Upload to GitHub for the Hackathon

Use this checklist so your repo is complete for the MedGemma Impact Challenge but stays clean and under size limits.

---

## ✅ INCLUDE (upload these)

### Source code
- **`src/`** – all agents, models, workflows, utils (full application code)
- **`config.py`** – configuration (no secrets; use env vars)
- **`demo/`** – Gradio app and any demo assets
- **`tests/`** – unit and integration tests
- **`run_evaluation.py`** – evaluation script
- **`quick_test.py`** – quick test script (if you use it)

### Dependencies & environment
- **`requirements.txt`** – Python dependencies
- **`.env.example`** – example env file with placeholder values (e.g. `HF_TOKEN=your_token_here`), **no real secrets**

### Data (for reproducibility)
- **`data/test_scenarios.json`** – test scenarios used for evaluation
- **`data/evaluation_results_improved.csv`** – detailed results (optional but good for judges)
- **`data/evaluation_summary_improved.json`** – summary metrics (optional)

### Documentation
- **`README.md`** – main project readme (installation, usage, 92.86% accuracy)
- **`LICENSE`** – e.g. CC BY 4.0 or your chosen license
- **`docs/`** – writeup, video script, guides, and **images**:
  - `docs/writeup.md` – full competition writeup
  - `docs/video_script.md`
  - `docs/KAGGLE_WRITEUP_FIELDS.md`
  - `docs/VIDEO_WHAT_TO_SHOW.md`
  - `docs/MEDIA_GALLERY_IMAGES.md`
  - `docs/GITHUB_UPLOAD_FOR_HACKATHON.md` (this file)
  - `docs/*.png` – metrics dashboard, architecture, flowcharts, confusion matrix, card image
- **`FINAL_ACCURACY_REPORT.md`** – accuracy report (root or in `docs/`)
- **`QUICKSTART.md`** or **`QUICK_START.txt`** – if you have one

### Optional but useful
- **`notebooks/`** – exploration or evaluation notebooks (clear outputs or use small outputs; avoid huge logs)
- **`kaggle_submission_package/`** – optional; duplicate of key docs + images for submission
- **`ACCURACY_IMPROVEMENTS.md`**, **`PROJECT_SUMMARY.md`** – if you want to show methodology

---

## ❌ DO NOT UPLOAD

- **`venv/`** – virtual environment (recreate with `pip install -r requirements.txt`)
- **`.env`** – real secrets (Hugging Face token, etc.); only commit `.env.example`
- **`models/cache/`** – downloaded model weights (too large; users download via Hugging Face)
- **`logs/`** – local log files
- **`.cache/`** – Hugging Face cache, etc.
- **`__pycache__/`**, **`.pytest_cache/`**, **`.ipynb_checkpoints/`** – already in `.gitignore`
- **Large evaluation logs** – e.g. multi‑MB `.log` files (keep one small sample if needed)
- **Video files** – host on YouTube/Vimeo and link in README; don’t put large `.mp4` in the repo
- **`.DS_Store`**, **`Thumbs.db`** – already in `.gitignore`

---

## 📁 Suggested repo structure (what judges will see)

```
medgemma-triage-system/
├── README.md                 # Start here: 92.86% accuracy, install, run demo
├── LICENSE
├── requirements.txt
├── .env.example
├── config.py
├── run_evaluation.py
├── quick_test.py
├── src/
│   ├── agents/
│   ├── models/
│   ├── workflows/
│   └── utils/
├── demo/
├── tests/
├── data/
│   ├── test_scenarios.json
│   ├── evaluation_results_improved.csv   # optional
│   └── evaluation_summary_improved.json   # optional
├── docs/
│   ├── writeup.md
│   ├── video_script.md
│   ├── *.png                              # gallery + card image
│   └── ... (other docs)
├── notebooks/                             # optional
├── FINAL_ACCURACY_REPORT.md
└── .gitignore
```

---

## 🔧 Before first push

1. **Create repo on GitHub** (public), then:
   ```bash
   git init
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   ```

2. **Confirm `.gitignore`** so you don’t commit:
   - `venv/`, `.env`, `models/cache/`, `logs/`, `.cache/`
   - Your `.gitignore` already includes these and now allows `docs/*.png` and `kaggle_submission_package/images/*.png`, and evaluation CSV/JSON in `data/`.

3. **Add and commit:**
   ```bash
   git add .
   git status   # double-check no .env, venv, or huge files
   git commit -m "MedGemma AI Medical Triage - 92.86% accuracy, 6 agents, 7 enforcement layers"
   git branch -M main
   git push -u origin main
   ```

4. **README:** In README.md, add at the top:
   - Short line: “92.86% accuracy (13/14 scenarios); 100% on EMERGENCY/URGENT/SEMI-URGENT/NON-URGENT.”
   - Link to competition: `https://www.kaggle.com/competitions/med-gemma-impact-challenge`
   - In “Installation” or “Setup”, remind users to:
     - Copy `.env.example` to `.env` and add their Hugging Face token
     - Accept MedGemma terms on Hugging Face

5. **Optional:** Add a “Submission” or “Hackathon” section in README with:
   - MedGemma Impact Challenge 2026
   - Tracks: Main Track, Agentic Workflow Prize
   - Writeup link (Kaggle)
   - Video link (YouTube/Vimeo)

---

## 📌 One-line summary

**Upload:** All source (`src/`, `demo/`, `tests/`), `config.py`, `requirements.txt`, `.env.example`, `data/test_scenarios.json` (+ optional evaluation CSV/JSON), `docs/` (writeup + PNGs), README, LICENSE.  
**Do not upload:** `venv/`, `.env`, model cache, logs, large video files.
