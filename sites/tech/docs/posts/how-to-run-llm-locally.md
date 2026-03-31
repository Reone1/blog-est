---
title: "How to Run LLM Locally: A Complete Guide to Ollama, llama.cpp, and LM Studio"
date: "2026-03-31"
type: "how-to"
description: "Step-by-step guide to running large language models locally on your own hardware using Ollama, llama.cpp, and LM Studio. Covers hardware requirements, setup, and performance optimization."
keywords: "how to run llm locally, local llm setup, ollama tutorial, llama.cpp guide, lm studio"
---

<div class="tldr">

**TL;DR:** You can run capable LLMs locally with 16 GB of RAM and no GPU using quantized models. Ollama is the easiest path for beginners, llama.cpp gives the most control, and LM Studio offers a polished GUI. For serious work, a GPU with at least 8 GB VRAM (RTX 3060 or better) dramatically improves token generation speed -- from roughly 5 tokens/sec on CPU to 40+ tokens/sec on GPU for a 7B parameter model.

</div>

## Why Run LLMs Locally?

Running a large language model on your own machine eliminates API costs, removes rate limits, keeps your data entirely private, and lets you work offline. A single heavy day of GPT-4-class API usage can cost $20-50; a local 7B model costs nothing after the initial hardware investment.

The tradeoff is straightforward: local models are smaller and less capable than frontier cloud models, but for many tasks -- code completion, summarization, drafting, data extraction -- a well-chosen local model performs surprisingly well.

## Hardware Requirements

Before installing anything, verify your machine meets the minimum specs for the model size you plan to run.

### RAM and VRAM Guidelines

| Model Size | Minimum RAM (CPU) | Recommended VRAM (GPU) | Example Models |
|---|---|---|---|
| 3B params | 4 GB | 4 GB | Phi-3 Mini, Llama 3.2 3B |
| 7B params | 8 GB | 6 GB | Mistral 7B, Llama 3.1 8B |
| 13B params | 16 GB | 10 GB | Llama 2 13B, CodeLlama 13B |
| 34B params | 32 GB | 24 GB | CodeLlama 34B, Yi 34B |
| 70B params | 64 GB | 48 GB (2x 24 GB) | Llama 3.1 70B |

These figures assume Q4_K_M quantization, which reduces model size by roughly 4x compared to full FP16 weights while retaining most of the quality.

### CPU vs. GPU Performance

On CPU alone, expect 3-8 tokens per second for a 7B model -- usable but slow. A modern NVIDIA GPU (RTX 3060 12 GB or better) pushes that to 30-60 tokens/sec. Apple Silicon Macs with unified memory are particularly strong here: an M2 Pro with 16 GB handles 7B models at roughly 25 tokens/sec using Metal acceleration.

## Method 1: Ollama (Recommended for Beginners)

Ollama wraps llama.cpp in a simple CLI with automatic model management. It runs on macOS, Linux, and Windows.

### Installation

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

On Windows, download the installer from ollama.com.

### Pulling and Running a Model

```bash
# Download and run Llama 3.1 8B (4.7 GB download)
ollama run llama3.1:8b

# For a smaller, faster model
ollama run phi3:mini

# List downloaded models
ollama list
```

Once the model loads, you get an interactive chat prompt. Type your query and press Enter.

### Using the Ollama API

Ollama exposes a local REST API on port 11434, making it easy to integrate into applications.

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Explain quicksort in three sentences.",
  "stream": false
}'
```

In Python:

```python
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.1:8b",
    "prompt": "Write a Python function to merge two sorted lists.",
    "stream": False
})

print(response.json()["response"])
```

### Ollama with OpenAI-Compatible Endpoint

Ollama also serves an OpenAI-compatible API, so existing code that targets the OpenAI SDK works without changes:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="unused")

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "What is a Merkle tree?"}]
)
print(response.choices[0].message.content)
```

## Method 2: llama.cpp (Maximum Control)

llama.cpp is the foundational C/C++ inference engine that Ollama and many other tools build on. Use it directly when you need fine-grained control over quantization, context length, or batch processing.

### Building from Source

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# CPU-only build
make -j$(nproc)

# NVIDIA GPU build (requires CUDA toolkit)
make -j$(nproc) GGML_CUDA=1

# Apple Silicon (Metal)
make -j$(nproc) GGML_METAL=1
```

### Downloading a GGUF Model

Models for llama.cpp use the GGUF format. Download them from Hugging Face:

```bash
# Install huggingface-hub CLI
pip install huggingface-hub

# Download a quantized Llama 3.1 8B model
huggingface-cli download \
  bartowski/Meta-Llama-3.1-8B-Instruct-GGUF \
  Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
  --local-dir ./models
```

### Running Inference

```bash
./llama-cli \
  -m models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
  -p "Explain the difference between TCP and UDP:" \
  -n 256 \
  --ctx-size 4096 \
  --threads 8 \
  --n-gpu-layers 35
```

Key parameters:

- `-n 256`: Generate up to 256 tokens.
- `--ctx-size 4096`: Context window size in tokens.
- `--threads 8`: CPU threads to use (set to your physical core count).
- `--n-gpu-layers 35`: Offload 35 transformer layers to GPU. Set to a high number to offload the entire model.

### Running a Local Server

```bash
./llama-server \
  -m models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
  --ctx-size 4096 \
  --n-gpu-layers 35 \
  --port 8080
```

This exposes an OpenAI-compatible API at `http://localhost:8080/v1`.

## Method 3: LM Studio (Best GUI Experience)

LM Studio provides a desktop application with a model browser, chat interface, and built-in server. It is free for personal use and runs on macOS, Windows, and Linux.

### Setup Steps

1. Download LM Studio from lmstudio.ai.
2. Open the app and use the built-in search to find a model (e.g., search "llama 3.1 8b").
3. Click Download on the quantization variant you want (Q4_K_M is a good default).
4. Navigate to the Chat tab, select the model, and start chatting.

### Running the Local Server

LM Studio includes a one-click local server. Go to the Server tab, select your model, and click Start Server. It serves an OpenAI-compatible API on `http://localhost:1234/v1` by default.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

response = client.chat.completions.create(
    model="llama-3.1-8b-instruct",
    messages=[{"role": "user", "content": "How does HTTPS work?"}],
    temperature=0.7
)
print(response.choices[0].message.content)
```

## Performance Optimization Tips

### 1. Choose the Right Quantization

Quantization reduces model precision to shrink file size and speed up inference. Common levels:

| Quantization | Bits per Weight | Quality Loss | Speed Gain |
|---|---|---|---|
| Q2_K | ~2.5 | Noticeable | Fastest |
| Q4_K_M | ~4.5 | Minimal | Good balance |
| Q5_K_M | ~5.5 | Very small | Moderate |
| Q8_0 | ~8.0 | Near zero | Slowest quantized |
| FP16 | 16.0 | None | Baseline |

**Q4_K_M is the sweet spot** for most users. It cuts memory use by roughly 70% compared to FP16 with only marginal quality degradation.

### 2. Maximize GPU Offloading

Every transformer layer you offload to the GPU speeds up inference. If your model has 32 layers and you can fit 24 on the GPU, set `--n-gpu-layers 24`. Monitor VRAM usage with `nvidia-smi` and increase until you approach your limit.

### 3. Tune Context Length

Larger context windows consume more memory. If you only need short conversations, reduce `--ctx-size` from the default 4096 to 2048. Conversely, some models support 128K context but you will need substantially more RAM to use it.

### 4. Use Flash Attention

llama.cpp supports Flash Attention, which reduces memory usage for long contexts:

```bash
./llama-cli -m model.gguf --flash-attn --ctx-size 8192
```

### 5. Batch Processing

When processing multiple prompts, use the server mode with parallel request support:

```bash
./llama-server -m model.gguf --parallel 4 --ctx-size 4096 --n-gpu-layers 35
```

This serves up to 4 concurrent requests, each with their own context.

## Choosing the Right Tool

| Criteria | Ollama | llama.cpp | LM Studio |
|---|---|---|---|
| Ease of setup | High | Low | High |
| GUI interface | No | No | Yes |
| Customization | Medium | High | Medium |
| Model management | Automatic | Manual | Built-in browser |
| API compatibility | OpenAI-compatible | OpenAI-compatible | OpenAI-compatible |
| Best for | Developers, CLI users | Power users, research | Non-technical users |

## Troubleshooting Common Issues

**Model loads but generation is extremely slow.** You are likely running entirely on CPU. Verify GPU offloading is active. For Ollama, check `ollama ps` to see if the GPU is being used.

**Out of memory errors.** Switch to a smaller quantization (Q4_K_M instead of Q8_0) or a smaller model. Reduce `--ctx-size` if you set it higher than the default.

**Garbled or repetitive output.** This usually means the wrong chat template is being applied. Ensure you are using an "Instruct" variant of the model, and that your tool applies the correct prompt format.

## What to Do Next

Start with Ollama and a 7B-8B parameter model. Run `ollama run llama3.1:8b` and test it on real tasks from your workflow. If you find yourself needing more control, move to llama.cpp. If you want a visual interface to experiment with different models, try LM Studio.

Local LLMs are not a replacement for frontier cloud models on complex reasoning tasks, but for everyday development work -- generating boilerplate, explaining code, summarizing documents -- they are fast, free, and completely private.
