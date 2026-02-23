# Video: What to Show (3 min)

Use this as your on-screen checklist. Match it to `video_script.md` for narration.

---

## 1. Opening (0:00–0:30)

**Show:**
- **Title card:** “MedGemma AI Medical Triage System” + your 80‑char title.
- **Problem hook:** Short text or image: “Triage saves lives — but expertise is scarce in rural & disaster settings.”
- **Transition:** e.g. “What if AI could help?” → cut to your demo.

**Avoid:** Long text; keep it one line or a simple graphic.

---

## 2. Solution intro (0:30–1:00)

**Show:**
- **One slide or frame:** “6 agents · MedGemma (HAI-DEF) · 92.86% accuracy.”
- **Optional:** Simple diagram: Patient → 6 agents → Triage report (no need to name every agent yet).
- **Optional:** Thumbnail card (560×280) or a cropped version as the “product” shot.

**Goal:** Judges see it’s multi‑agent, MedGemma-based, and has a concrete accuracy number.

---

## 3. Demo 1 – Emergency (1:00–1:45)

**Show (screen record the real app):**

1. **Input:** Type (or paste) exactly:
   ```text
   I'm having severe chest pain for the last hour. It feels like pressure and it's radiating to my left arm.
   ```
2. **Run:** Click Submit / Run so the pipeline runs.
3. **Result:** Show the **final triage output** with:
   - **EMERGENCY** clearly visible (and in red if your UI does that).
   - Recommendation: “Emergency Department” / “Call 911” (or equivalent).
4. **Optional:** Brief flash of “Red flags detected” or “Critical” if your UI shows it.

**Narrate:** “Chest pain with radiation → red flags → EMERGENCY → go to ER.” No need to show code or logs.

---

## 4. Demo 2 – Non‑urgent (1:45–2:15)

**Show (same app, new case):**

1. **Input:** Type (or paste):
   ```text
   I have a mild cold with a runny nose that started yesterday. No fever.
   ```
2. **Run:** Submit and let it run.
3. **Result:** Show the **final triage output** with:
   - **NON-URGENT** (or equivalent) clearly visible.
   - Recommendation: self‑care / primary care / “no ER” (whatever your system says).

**Narrate:** “Mild, short‑duration, no red flags → NON‑URGENT → appropriate low‑acuity care.”

**Goal:** Contrast with the emergency case so judges see the system doesn’t over‑escalate.

---

## 5. How it works (2:15–2:45)

**Show one or both:**

- **Option A – Architecture:** One static slide or diagram:
  - “Intake → Symptom Assessment → Medical Knowledge → Urgency Classification → Care Recommendation → Communication.”
  - Optional short line: “7 enforcement layers, 6 UNKNOWN checks.”
- **Option B – Metrics:** One slide with:
  - 92.86% accuracy
  - 100% on EMERGENCY / URGENT / SEMI‑URGENT / NON‑URGENT
  - “300% critical flag detection” (or your wording)
  - “6 agents, 7 enforcement layers”

**Narrate:** “Six MedGemma agents; enforcement layers for safety and consistency; strong performance on all urgency levels.”

---

## 6. Impact & closing (2:45–3:00)

**Show:**
- **Use cases (text or icons):** Rural clinics · Telemedicine · Disaster triage · ED pre‑screen.
- **Final card:**
  - “MedGemma AI Medical Triage System”
  - “92.86% accuracy · 6 agents · 7 enforcement layers”
  - “MedGemma Impact Challenge 2026”
  - Your Kaggle username / repo link if allowed.

**Narrate:** “Built with MedGemma and HAI-DEF. For healthcare, every second counts.”

---

## Quick reference: Must‑show list

| Time      | Must show on screen |
|-----------|----------------------|
| 0:00–0:30 | Title + problem (triage, scarce expertise). |
| 0:30–1:00 | “6 agents, MedGemma, 92.86%” (+ optional diagram). |
| 1:00–1:45 | **Live demo:** chest pain input → **EMERGENCY** + ER recommendation. |
| 1:45–2:15 | **Live demo:** mild cold input → **NON‑URGENT** + self‑care. |
| 2:15–2:45 | Architecture and/or metrics (92.86%, 100% categories, 7 layers). |
| 2:45–3:00 | Use cases + final card + competition name. |

---

## Recording tips

- **Demo:** Use the real Gradio (or your) UI; no need to show terminal or code.
- **Resolution:** 1080p; make sure “EMERGENCY” and “NON-URGENT” are readable.
- **Pacing:** Pre-type or paste the two inputs so the run takes only a few seconds each.
- **Backup:** If the app is slow, pre-record the two demo segments and narrate over them.
- **Audio:** Narration + optional light background music; add captions for accessibility.

---

**Bottom line:** Show the **problem**, the **two contrasting demos** (emergency vs non‑urgent), and the **numbers** (92.86%, 6 agents, 7 layers). Keep the rest short and clear.
