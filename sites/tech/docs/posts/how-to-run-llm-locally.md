---
title: "How to Run LLMs Locally: A Complete Guide to Ollama, llama.cpp, and LM Studio"
date: "2026-03-31"
type: "how-to"
description: "Learn how to run large language models locally on your own hardware. Step-by-step setup guides for Ollama, llama.cpp, and LM Studio, with hardware requirements and performance optimization tips."
keywords: "how to run llm locally, local llm setup, ollama tutorial, llama.cpp guide, lm studio"
---

<div class="tldr">

**TL;DR:** You can run LLMs locally using Ollama (easiest), llama.cpp (most flexible), or LM Studio (best GUI). You need at least 8 GB of RAM for 7B models and 16 GB for 13B models. Quantized models (Q4_K_M or Q5_K_M) offer the best balance of quality and performance. GPU acceleration via CUDA or Metal cuts inference time by 5-10x compared to CPU-only.

</div>

## Why Run LLMs Locally?

Running language models on your own hardware eliminates API costs, removes rate limits, and keeps your data entirely private. For developers building applications that process sensitive documents, handle proprietary code, or simply need predictable latency, local inference is increasingly practical.

The landscape has matured significantly. In early 2024, running a capable model locally required significant technical knowledge and expensive hardware. Today, tools like Ollama have reduced the setup to a single command, and quantization techniques let you run 70B-parameter models on consumer GPUs.

This guide covers three approaches, each suited to different needs.

## Hardware Requirements

Before installing anything, verify your hardware meets the minimum requirements. The bottleneck is almost always RAM (system or GPU VRAM), not CPU.

| Model Size | Minimum RAM | Recommended RAM | GPU VRAM (Quantized) |
|-----------|-------------|-----------------|---------------------|
| 7B params | 8 GB | 16 GB | 6 GB |
| 13B params | 16 GB | 32 GB | 10 GB |
| 30B params | 32 GB | 64 GB | 24 GB |
| 70B params | 64 GB | 128 GB | 48 GB (or split) |

These numbers assume Q4_K_M quantization, which reduces model size by roughly 4x compared to full precision (FP16). If you plan to run full-precision models, multiply the RAM requirements by approximately 2x.

For GPU acceleration, NVIDIA GPUs with CUDA support offer the broadest compatibility. Apple Silicon Macs leverage Metal for GPU acceleration and benefit from unified memory architecture, making them surprisingly capable for local LLM inference.

## Option 1: Ollama (Recommended for Beginners)

Ollama wraps llama.cpp in a user-friendly CLI with a model registry, automatic GPU detection, and an OpenAI-compatible API server. It is the fastest way to go from zero to running a local model.

### Installation

On macOS and Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

On Windows, download the installer from ollama.com or use winget:

```bash
winget install Ollama.Ollama
```

Verify the installation:

```bash
ollama --version
```

### Pulling and Running Models

Ollama maintains a registry of pre-quantized models. To download and run Llama 3.1 8B:

```bash
ollama pull llama3.1:8b
ollama run llama3.1:8b
```

This opens an interactive chat. To exit, type `/bye`.

Other popular models available through Ollama:

```bash
ollama pull mistral          # Mistral 7B
ollama pull codellama:13b    # Code Llama 13B
ollama pull gemma2:9b        # Google Gemma 2 9B
ollama pull qwen2.5:14b      # Qwen 2.5 14B
ollama pull deepseek-r1:8b   # DeepSeek R1 distilled 8B
```

### Using the API

Ollama exposes an OpenAI-compatible API on port 11434 by default. This means you can point existing OpenAI SDK code at your local instance:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required but unused
)

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[
        {"role": "user", "content": "Explain TCP handshake in 3 sentences."}
    ],
    temperature=0.7,
)

print(response.choices[0].message.content)
```

### Customizing Models with Modelfiles

You can create custom model configurations using a Modelfile:

```dockerfile
FROM llama3.1:8b

PARAMETER temperature 0.3
PARAMETER num_ctx 8192

SYSTEM """You are a senior Python developer. You write clean,
well-documented code following PEP 8 conventions. You always
include type hints and docstrings."""
```

Build and run the custom model:

```bash
ollama create python-assistant -f Modelfile
ollama run python-assistant
```

## Option 2: llama.cpp (Maximum Control)

llama.cpp is the C/C++ inference engine that powers Ollama and many other tools. Using it directly gives you full control over quantization, context size, batch parameters, and memory mapping.

### Building from Source

```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# CPU-only build
cmake -B build
cmake --build build --config Release -j$(nproc)

# NVIDIA GPU build (requires CUDA toolkit)
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j$(nproc)

# Apple Silicon (Metal is enabled by default on macOS)
cmake -B build
cmake --build build --config Release -j$(sysctl -n hw.ncpu)
```

### Downloading Models

Download GGUF-format models from Hugging Face. The bartowski and QuantFactory accounts maintain well-quantized versions of popular models:

```bash
# Install huggingface-hub CLI
pip install huggingface-hub

# Download a specific quantized model
huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF \
    Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
    --local-dir ./models
```

### Running Inference

```bash
./build/bin/llama-cli \
    -m models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
    -p "Explain the difference between TCP and UDP:" \
    -n 512 \
    -c 4096 \
    --temp 0.7 \
    -ngl 99  # offload all layers to GPU
```

Key parameters:

- `-ngl`: Number of layers to offload to GPU. Use 99 to offload all layers.
- `-c`: Context window size in tokens.
- `-n`: Maximum number of tokens to generate.
- `-b`: Batch size for prompt processing (higher = faster prompt ingestion, more VRAM).
- `--mlock`: Lock model in RAM to prevent swapping.

### Running as a Server

llama.cpp includes a built-in server with an OpenAI-compatible API:

```bash
./build/bin/llama-server \
    -m models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
    -c 8192 \
    -ngl 99 \
    --host 0.0.0.0 \
    --port 8080
```

## Option 3: LM Studio (Best Desktop Experience)

LM Studio provides a polished GUI for downloading, configuring, and chatting with local models. It is built on llama.cpp but adds a model search interface, preset management, and a local server with one-click activation.

### Setup

1. Download LM Studio from lmstudio.ai for your platform (macOS, Windows, or Linux).
2. Open the application and navigate to the Discover tab.
3. Search for a model (e.g., "Llama 3.1 8B Instruct").
4. Select a quantization level. Q4_K_M is a good default.
5. Click Download.

Once downloaded, select the model in the Chat tab and begin prompting. The local server can be started from the Developer tab, which exposes the same OpenAI-compatible API on `localhost:1234`.

LM Studio also supports the `lms` CLI tool:

```bash
lms load llama-3.1-8b-instruct
lms server start
lms chat "What is the capital of France?"
```

## Performance Optimization Tips

### Choose the Right Quantization

Quantization levels represent different tradeoffs between model quality and resource usage:

| Quantization | Size (7B model) | Quality Loss | Speed |
|-------------|-----------------|-------------|-------|
| Q2_K | ~2.7 GB | Noticeable | Fastest |
| Q4_K_M | ~4.1 GB | Minimal | Fast |
| Q5_K_M | ~4.8 GB | Very small | Moderate |
| Q6_K | ~5.5 GB | Negligible | Slower |
| Q8_0 | ~7.2 GB | None | Slowest quantized |
| FP16 | ~14 GB | None | Baseline |

For most use cases, Q4_K_M provides the best tradeoff. If you have extra VRAM, Q5_K_M offers marginally better output quality with modest additional memory usage.

### GPU Layer Offloading

If your GPU VRAM cannot hold the entire model, partial offloading still helps. Even offloading 50% of layers to the GPU can double your tokens-per-second throughput. Experiment with the `-ngl` flag (llama.cpp) or layer count settings (LM Studio) to find the sweet spot.

### Context Size and Memory

Larger context windows consume proportionally more memory. A 7B model at Q4_K_M with a 4096-token context uses roughly 4.5 GB, but increasing the context to 32768 tokens can push memory usage past 8 GB. Set context size to the minimum you actually need.

### Batch Processing

When processing long prompts, increasing the batch size (`-b` flag in llama.cpp) speeds up the prompt evaluation phase significantly. A batch size of 512 or 1024 is usually optimal if you have sufficient VRAM.

### Flash Attention

Enable flash attention when available. In llama.cpp, build with `-DLLAMA_FLASH_ATTN=ON` and pass `--flash-attn` at runtime. This reduces memory usage during inference and improves throughput, especially with longer contexts.

## Benchmarking Your Setup

Measure your inference speed to establish a baseline. With llama.cpp, add the `--verbose` flag to see tokens-per-second statistics:

```bash
./build/bin/llama-cli \
    -m models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
    -p "Write a Python function to sort a list:" \
    -n 256 -ngl 99 --verbose 2>&1 | grep "tokens per second"
```

Typical throughput ranges for a Q4_K_M 7B model:

- CPU only (modern 8-core): 8-15 tokens/sec
- NVIDIA RTX 3060 (12 GB): 40-60 tokens/sec
- NVIDIA RTX 4090 (24 GB): 90-130 tokens/sec
- Apple M2 Pro (16 GB): 25-40 tokens/sec
- Apple M3 Max (48 GB): 45-70 tokens/sec

These numbers are for generation (decode) speed. Prompt processing (prefill) is typically 3-5x faster.

## Troubleshooting Common Issues

**Model loads but generation is extremely slow:** You are likely running on CPU when you intended GPU. Verify GPU offloading is active by checking the startup logs for CUDA or Metal initialization messages.

**Out of memory errors:** Reduce context size, switch to a smaller quantization (Q4_K_M to Q3_K_M), or use a smaller model. For partial GPU offloading, reduce `-ngl` until the model fits.

**Garbled or repetitive output:** This usually indicates a prompt format mismatch. Ensure you are using the correct chat template for the model. Ollama handles this automatically; with llama.cpp, check the model card on Hugging Face for the expected prompt format.

**Model downloads are slow:** Use `aria2c` for faster multi-connection downloads from Hugging Face, or use `huggingface-cli download` which supports resumable downloads.

## Choosing the Right Tool

- **Use Ollama** if you want the simplest setup, plan to use the API, or need to serve multiple models.
- **Use llama.cpp** if you need precise control over inference parameters, want to quantize your own models, or are building a custom deployment pipeline.
- **Use LM Studio** if you prefer a graphical interface, want to quickly compare different models, or are exploring local LLMs for the first time.

All three tools use the same underlying inference engine and produce identical output given the same model and parameters. The choice comes down to your workflow preferences and how much control you need.
