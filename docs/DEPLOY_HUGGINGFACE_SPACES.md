# Deploy MedGemma Triage on Hugging Face Spaces

You can run the Gradio demo as a **Hugging Face Space** so anyone can try it in the browser without running AWS or Docker.

## Requirements

- A [Hugging Face account](https://huggingface.co/join).
- **Accepted MedGemma license**: [google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it) (Sign in → Accept).
- A [Hugging Face token](https://huggingface.co/settings/tokens) with read access (for the gated model).

## Option A: Create a new Space and push this repo

1. **Create the Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces) → **Create new Space**.
   - Name it (e.g. `medgemma-triage-demo`).
   - **SDK**: **Gradio**.
   - **Hardware**: **CPU basic** (free, but 4B model is slow or may OOM); for faster inference use **GPU T4** or **A10G** (paid).
   - **Visibility**: Public or Private.
   - Create the Space (HF will init a repo).

2. **Clone and add your code**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/medgemma-triage-demo
   cd medgemma-triage-demo
   ```
   Copy into this repo (or add as submodule) the app code:
   - `app.py` (root – already in this project; it’s the Space entry point)
   - `demo/` folder
   - `src/` folder
   - `config.py`
   - `requirements.txt` (or a slimmer `requirements.txt` for Spaces – see below)

   Or push from this repo:
   ```bash
   cd /path/to/MedGemma-Impact-Challenge
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/medgemma-triage-demo
   git push space main
   ```
   (Adjust branch if yours is not `main`.)

3. **Set your Hugging Face token**
   - In the Space page: **Settings** → **Repository secrets** (or **Variables and secrets**).
   - Add a secret: name **HF_TOKEN**, value = your Hugging Face token.
   - The app uses it to load the gated MedGemma model.

4. **Configure hardware (optional)**
   - **CPU**: Free; 4B model may be slow or OOM. Consider `MODEL_NAME=google/medgemma-1.5-2b-it` in a Space variable to use the 2B model.
   - **GPU (T4 / A10G)**: In Space **Settings** → **Hardware**, switch to a GPU. Set `USE_GPU=true`. **4-bit is enabled automatically on Spaces** for much faster inference (~2–4×); you can override with `LOAD_IN_4BIT=false` if needed.

5. **Space variables (optional)**
   In **Settings** → **Variables and secrets** you can add:
   - `MODEL_NAME` = `google/medgemma-1.5-4b-it` (default) or `google/medgemma-1.5-2b-it` for CPU.
   - `USE_GPU` = `true` if you selected GPU hardware.
   - `LOAD_IN_4BIT` = `true` (default on Spaces) or `false`. **Keep `true` on GPU for speed.**
   - `ATTN_IMPLEMENTATION` = `sdpa` for faster attention on GPU (optional; default `eager`).
   - `MAX_NEW_TOKENS` = `384` (default) or lower (e.g. `256`) for quicker replies.

## Option B: Use “Duplicate this Space” from a template

If someone publishes this project as a public Space, others can click **Duplicate this Space** to get their own copy, then add their **HF_TOKEN** in the duplicated Space’s secrets.

## App file

The Space runs **app.py** at the repo root. That file adds the project root to `sys.path` and launches the demo from `demo/app.py`. No need to change the Space’s “App file” setting.

## Slim requirements for Spaces (optional)

Spaces have limited resources. You can use a slimmer `requirements.txt` in the Space repo that omits dev/test packages. Example:

```text
transformers>=4.40.0
torch>=2.0.0
accelerate>=0.27.0
huggingface-hub>=0.21.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-core>=0.1.0
gradio>=4.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
tqdm>=4.66.0
numpy>=1.24.0
pandas>=2.0.0
pyyaml>=6.0
requests>=2.31.0
tenacity>=8.2.0
bitsandbytes>=0.41.0
optimum>=1.16.0
```

If you use **only CPU**, you can drop `bitsandbytes` (4-bit is GPU-only in this app). The 4B model on CPU needs enough RAM; free CPU Spaces may OOM – use the 2B model or a paid CPU/GPU tier.

## README for the Space

You can add a short README in the Space repo so the Space page looks good. Example YAML block for a Gradio Space (Spaces read this):

```yaml
---
title: MedGemma AI Medical Triage
emoji: 🏥
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
hardware: cpu-basic
---
```

Then describe the app below. Use `hardware: t4-small` or `a10g-small` if you switch to GPU.

## Speed (reduce inference time)

First request can take several minutes; later ones are faster with the model loaded. To speed up:

| Setting | Effect |
|--------|--------|
| **GPU + 4-bit** | Biggest gain. On Spaces, **4-bit is on by default** when using GPU. Ensure hardware is GPU (T4/A10G) and `LOAD_IN_4BIT` is not set to `false`. |
| **ATTN_IMPLEMENTATION=sdpa** | Optional. Use faster attention on GPU. Set in Space variables. |
| **MAX_NEW_TOKENS** | Default 384; set to `256` for quicker, shorter replies. |

Typical first-response time on a T4 with 4-bit: on the order of 1–2 minutes instead of 6+ minutes with full precision.

## Troubleshooting

- **“Could not load model” / 401**: Add **HF_TOKEN** in Space secrets and accept the [MedGemma model license](https://huggingface.co/google/medgemma-1.5-4b-it).
- **Out of memory on CPU**: Use the **2B model** (`MODEL_NAME=google/medgemma-1.5-2b-it`) or upgrade to a larger CPU/GPU.
- **Slow inference**: Use **GPU** hardware; 4-bit is auto-enabled on Spaces. Optionally set `ATTN_IMPLEMENTATION=sdpa` and lower `MAX_NEW_TOKENS`.
- **Build fails**: Ensure `requirements.txt` and `app.py` are at the repo root and that all imports (e.g. `config`, `src`, `demo`) are present in the Space repo.

## Summary

| Step | Action |
|------|--------|
| 1 | Create a Gradio Space on huggingface.co/spaces |
| 2 | Push this repo (or copy app.py, demo/, src/, config.py, requirements.txt) |
| 3 | Add **HF_TOKEN** in Space secrets |
| 4 | Optionally set MODEL_NAME, USE_GPU, LOAD_IN_4BIT in variables |
| 5 | Use GPU hardware for faster inference; use 2B model on free CPU to avoid OOM |
