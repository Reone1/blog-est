---
title: "How to Reduce LLM Inference Cost: 7 Proven Strategies"
date: "2026-03-31"
type: "how-to"
description: "Practical techniques to reduce LLM inference costs by up to 90%, including quantization, prompt caching, batching, model distillation, and prompt optimization with real cost comparisons."
keywords: "how to reduce llm inference cost, llm cost optimization, ai inference savings, prompt caching"
---

<div class="tldr">

**TL;DR:** LLM inference costs can be reduced by 80-95% by combining several strategies: use prompt caching to cut repeated context costs by 90%, switch to smaller models for simple tasks (GPT-4o Mini costs 33x less than GPT-4o), compress prompts to reduce token count by 40-60%, batch requests for throughput gains, and self-host quantized models for high-volume workloads. The biggest single win for most teams is prompt caching, followed by routing requests to the cheapest model that can handle each task.

</div>

## The Cost Problem

LLM inference costs add up fast. A production application handling 100,000 requests per day with an average of 1,000 input tokens and 500 output tokens per request costs roughly:

- **GPT-4o**: $250/day input + $500/day output = **$750/day ($22,500/month)**
- **Claude Sonnet**: $300/day input + $750/day output = **$1,050/day ($31,500/month)**

These numbers force teams to either limit usage, degrade quality, or find ways to reduce per-request costs. Here are seven strategies that work.

## Strategy 1: Prompt Caching

Prompt caching is the single highest-impact optimization for applications that reuse system prompts, few-shot examples, or large context documents across requests.

### How It Works

Both Anthropic and OpenAI offer prompt caching. When you send the same prefix of tokens across multiple requests, the provider caches the KV (key-value) computations and charges a reduced rate for subsequent uses.

**Anthropic prompt caching pricing:**

| Component | Cost per Million Tokens |
|---|---|
| Cache write (first use) | 1.25x base input price |
| Cache read (subsequent) | 0.1x base input price |
| Non-cached input | 1.0x base input price |

That means cached tokens cost **90% less** on reads. If your system prompt is 2,000 tokens and you send 10,000 requests, you pay full price once and 10% for the remaining 9,999 requests.

### Implementation with Claude

```python
import anthropic

client = anthropic.Anthropic()

# The system prompt will be cached after the first request
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a customer support agent for Acme Corp. Here is our complete product documentation: [... 3000 tokens of docs ...]",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "How do I reset my password?"}]
)

# Check cache performance
print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
print(f"Cache creation tokens: {response.usage.cache_creation_input_tokens}")
```

### Implementation with OpenAI

OpenAI caches automatically for requests sharing the same prefix. No code changes needed -- the discount applies when the API detects repeated prefixes of 1,024 tokens or more.

```python
from openai import OpenAI

client = OpenAI()

# Structure prompts with static content first for maximum cache hits
system_msg = """You are a code review assistant. Follow these rules:
[... lengthy static instructions ...]
[... few-shot examples ...]
"""

# The static prefix gets cached automatically
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_msg},
        {"role": "user", "content": code_to_review},  # dynamic part last
    ]
)
```

**Key tip:** Structure your prompts so static content comes first and dynamic content comes last. Caching works on prefixes, so any change in the middle invalidates the cache for everything after it.

## Strategy 2: Model Routing

Not every request needs a frontier model. Route simple tasks to cheaper models and reserve expensive models for hard problems.

### Cost Comparison Table (per 1M tokens, as of early 2026)

| Model | Input Cost | Output Cost | Relative Cost |
|---|---|---|---|
| GPT-4o | $2.50 | $10.00 | 1.0x |
| GPT-4o Mini | $0.15 | $0.60 | 0.06x |
| Claude Sonnet | $3.00 | $15.00 | 1.2x |
| Claude Haiku | $0.25 | $1.25 | 0.1x |
| Gemini 1.5 Flash | $0.075 | $0.30 | 0.03x |
| Llama 3.1 70B (self-hosted) | ~$0.50* | ~$0.50* | 0.04x |

*Self-hosted costs depend on hardware and utilization.

### Simple Router Implementation

```python
def classify_complexity(query: str) -> str:
    """Classify query complexity to route to the right model."""
    # Use a small, fast model for classification
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": f"Classify this query as SIMPLE or COMPLEX. Only output one word.\n\nQuery: {query}"
        }]
    )
    return response.choices[0].message.content.strip().upper()


def route_request(query: str) -> str:
    complexity = classify_complexity(query)

    if complexity == "SIMPLE":
        model = "gpt-4o-mini"  # $0.15 / $0.60 per 1M tokens
    else:
        model = "gpt-4o"       # $2.50 / $10.00 per 1M tokens

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content
```

In practice, 60-80% of typical production queries can be handled by a cheaper model, cutting average costs by 50-70%.

## Strategy 3: Prompt Compression

Most prompts contain redundant words, formatting, and whitespace. Compressing prompts reduces token count and cost without meaningfully affecting output quality.

### Manual Prompt Optimization

```python
# Before: 67 tokens
prompt_verbose = """
I would like you to please analyze the following customer review
and determine whether the overall sentiment expressed in the review
is positive, negative, or neutral. Please provide your answer as
a single word: "positive", "negative", or "neutral".

Review: "{review}"
"""

# After: 28 tokens (58% reduction)
prompt_compressed = """Classify sentiment as positive/negative/neutral. One word only.

Review: "{review}"
"""
```

### Programmatic Compression with LLMLingua

For large context documents, use a compression library:

```python
from llmlingua import PromptCompressor

compressor = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
)

long_context = "... 5000 tokens of documentation ..."

compressed = compressor.compress_prompt(
    long_context,
    rate=0.5,  # target 50% compression
    force_tokens=["important_keyword"]  # preserve specific terms
)

print(f"Original tokens: {compressed['origin_tokens']}")
print(f"Compressed tokens: {compressed['compressed_tokens']}")
print(f"Ratio: {compressed['ratio']:.1f}x")
```

Typical compression ratios of 2-5x are achievable with less than 2% quality degradation on downstream tasks.

## Strategy 4: Batching Requests

Batching amortizes overhead and often qualifies for volume discounts.

### OpenAI Batch API

OpenAI's Batch API offers a 50% discount for non-time-sensitive workloads with a 24-hour completion window.

```python
import json

# Prepare batch file (JSONL format)
requests = []
for i, prompt in enumerate(prompts):
    requests.append({
        "custom_id": f"req-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256
        }
    })

with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Upload and submit
batch_file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch_job = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)

print(f"Batch ID: {batch_job.id}")
```

### Self-Hosted Batching with vLLM

For self-hosted models, vLLM provides continuous batching that dramatically improves GPU utilization:

```bash
pip install vllm

python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --max-num-batched-tokens 32768 \
    --max-num-seqs 64
```

vLLM's PagedAttention and continuous batching can increase throughput by 5-10x compared to naive sequential inference.

## Strategy 5: Response Caching

If different users frequently ask the same or similar questions, cache LLM responses to avoid redundant API calls entirely.

```python
import hashlib
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)
CACHE_TTL = 3600  # 1 hour

def cached_completion(messages: list, model: str = "gpt-4o") -> str:
    # Create a cache key from the request
    cache_key = hashlib.sha256(
        json.dumps({"model": model, "messages": messages}, sort_keys=True).encode()
    ).hexdigest()

    # Check cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)["content"]

    # Cache miss -- call the API
    response = client.chat.completions.create(model=model, messages=messages)
    content = response.choices[0].message.content

    # Store in cache
    r.setex(cache_key, CACHE_TTL, json.dumps({"content": content}))
    return content
```

For semantic caching (matching similar but not identical queries), use embedding-based lookup:

```python
from openai import OpenAI
import numpy as np

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def semantic_cache_lookup(query: str, threshold: float = 0.95) -> str | None:
    query_emb = np.array(get_embedding(query))

    for entry in cache_entries:
        similarity = np.dot(query_emb, np.array(entry["embedding"]))
        if similarity >= threshold:
            return entry["response"]
    return None
```

A cache hit rate of even 20% reduces costs by 20% with zero quality impact.

## Strategy 6: Model Distillation

Train a smaller, specialized model on outputs from a larger model. This is particularly effective when you have a narrow task domain.

### Process

1. Generate high-quality training data using a frontier model.
2. Fine-tune a smaller model on that data.
3. Deploy the smaller model for production inference.

```python
# Step 1: Generate training data with GPT-4o
training_examples = []
for input_text in raw_inputs:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a sentiment classifier. Respond with JSON: {\"sentiment\": \"positive|negative|neutral\", \"confidence\": 0.0-1.0}"},
            {"role": "user", "content": input_text}
        ]
    )
    training_examples.append({
        "messages": [
            {"role": "system", "content": "Classify sentiment. Respond with JSON."},
            {"role": "user", "content": input_text},
            {"role": "assistant", "content": response.choices[0].message.content}
        ]
    })

# Step 2: Fine-tune GPT-4o Mini (costs ~$0.30 per 1M training tokens)
# Upload training file and create fine-tuning job via OpenAI API

# Step 3: Use the fine-tuned model at GPT-4o Mini prices
response = client.chat.completions.create(
    model="ft:gpt-4o-mini-2024-07-18:org:sentiment:abc123",
    messages=[{"role": "user", "content": new_input}]
)
```

Distillation typically achieves 90-95% of the teacher model's quality at 10-30x lower cost per request.

## Strategy 7: Quantization for Self-Hosted Models

If you self-host models, quantization reduces memory requirements and increases throughput, directly lowering per-token costs.

### Quantization Impact on a Llama 3.1 70B Model

| Precision | Model Size | GPU Memory | Tokens/sec (A100) | Quality (MMLU) |
|---|---|---|---|---|
| FP16 | 140 GB | 2x A100 80 GB | 25 | 79.5% |
| INT8 | 70 GB | 1x A100 80 GB | 40 | 79.1% |
| INT4 (GPTQ) | 35 GB | 1x A100 40 GB | 55 | 78.2% |
| INT4 (AWQ) | 35 GB | 1x A100 40 GB | 60 | 78.5% |

AWQ (Activation-aware Weight Quantization) generally preserves quality better than GPTQ at the same bit level.

```bash
# Serve a quantized model with vLLM
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-3.1-70B-Instruct-AWQ \
    --quantization awq \
    --tensor-parallel-size 1 \
    --max-model-len 4096
```

## Combining Strategies: A Real-World Example

Here is how a production application might layer these techniques:

| Layer | Strategy | Savings |
|---|---|---|
| 1 | Response caching (20% hit rate) | 20% |
| 2 | Model routing (70% to Mini) | 50% of remaining |
| 3 | Prompt caching (system prompt) | 30% of remaining |
| 4 | Prompt compression | 15% of remaining |
| **Combined** | | **~85% total reduction** |

Starting from $22,500/month, these combined strategies bring the bill down to approximately $3,400/month for the same workload.

## Measuring and Monitoring

You cannot optimize what you do not measure. Track these metrics for every request:

```python
import time

def tracked_completion(messages, model):
    start = time.time()
    response = client.chat.completions.create(model=model, messages=messages)
    latency = time.time() - start

    metrics = {
        "model": model,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "latency_seconds": latency,
        "estimated_cost": estimate_cost(
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
            model
        )
    }
    log_to_monitoring(metrics)  # Send to your observability platform
    return response
```

Aggregate these into daily and weekly dashboards. Look for endpoints with high token counts (candidates for compression), repeated queries (candidates for caching), and simple queries hitting expensive models (candidates for routing).

## Where to Start

If you change one thing today, enable prompt caching. It requires minimal code changes and delivers the largest single cost reduction. Then add model routing. These two strategies alone typically cut costs by 60-80%.
