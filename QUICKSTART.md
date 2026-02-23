# Quick Start Guide

Get the MedGemma AI Medical Triage System up and running in minutes!

## Prerequisites

- Python 3.9 or higher
- Hugging Face account with MedGemma access
- 8GB+ RAM (16GB recommended)
- GPU optional but recommended for faster inference

## Step 1: Setup Environment

```bash
# Clone the repository
cd /Users/shenry/Documents/Personal/Training/Project/Kaggle/MedGemma\ Impact\ Challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get MedGemma Access

1. Visit https://huggingface.co/google/medgemma-2b
2. Accept the HAI-DEF Terms of Use
3. Create a Hugging Face access token at https://huggingface.co/settings/tokens
4. Copy your token

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your HF token
# HF_TOKEN=your_token_here
```

## Step 4: Run the Demo

### Option A: Web Interface (Recommended)

```bash
python demo/app.py
```

Then open your browser to http://localhost:7860

### Option B: Command Line

```bash
python demo/simple_cli.py
```

## Step 5: Try Example Scenarios

Try these inputs:

**Emergency:**
```
I'm having severe chest pain that started 30 minutes ago. 
It feels like pressure and it's radiating to my left arm.
```

**Non-Emergency:**
```
I have a mild cold with a runny nose that started yesterday.
```

## Testing the System

Run the test suite:
```bash
# Unit tests
pytest tests/

# Scenario evaluation
python tests/test_scenarios.py
```

## Troubleshooting

### Model Loading Issues

If you get authentication errors:
```bash
# Login to Hugging Face CLI
huggingface-cli login
```

### Memory Issues

If running out of memory, use the smaller model or quantization:

Edit `config.py`:
```python
# Use 8-bit quantization
LOAD_IN_8BIT = True
```

### Slow Inference

- Use a GPU if available
- Or reduce MAX_LENGTH in config.py
- Or use quantization (8-bit or 4-bit)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [video script](docs/video_script.md) to understand the workflow
- Review the [technical writeup](docs/writeup.md) for competition details
- Explore the Jupyter notebook in `notebooks/evaluation.ipynb`

## Getting Help

- Check logs in `logs/app.log`
- Review the architecture diagram in README.md
- See test scenarios in `data/test_scenarios.json`

## Key Files

- `demo/app.py` - Main web application
- `src/workflows/triage_workflow.py` - Core triage logic
- `src/agents/` - Individual agent implementations
- `config.py` - Configuration settings
- `tests/test_scenarios.py` - Evaluation script

## Important Notes

⚠️ **Medical Disclaimer**: This is a demonstration system for research purposes only. It does NOT replace professional medical advice. For emergencies, call 911.

🔧 **Development**: System requires internet access to download the MedGemma model on first run (~2-5 GB).

📊 **Performance**: First inference may be slow as model loads into memory. Subsequent inferences are faster.

---

Happy triaging! 🏥🤖
