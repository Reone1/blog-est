---
title: "LLM Context Window Explained Simply: What It Is and Why It Matters"
date: "2026-03-31"
type: "explainer"
description: "A clear explanation of LLM context windows, how tokens work, how major models compare, and the practical implications of context length for real-world applications."
keywords: "llm context window explained simply, what is context window, llm token limit, context length comparison"
---

<div class="tldr">

**TL;DR:** A context window is the maximum amount of text an LLM can process in a single request -- both your input and the model's output combined. It is measured in tokens (roughly 0.75 words per token for English). Current models range from 8K tokens (some open-source models) to 1M+ tokens (Gemini 1.5 Pro). Larger context windows let you process longer documents and maintain longer conversations, but they cost more, increase latency, and do not guarantee the model will actually attend to all the information equally. For most practical applications, how you use the context window matters more than its raw size.

</div>

## What Is a Context Window?

A context window is the total number of tokens a language model can "see" at once during a single interaction. Think of it as the model's working memory. Everything the model considers when generating a response -- your system prompt, the conversation history, any documents you provide, and the output it generates -- must fit within this window.

When you exceed the context window, one of two things happens: the API returns an error, or the system silently truncates earlier content. Either way, the model loses access to information that did not fit.

## How Tokens Work

LLMs do not process raw text. They first convert text into tokens -- small units that might be a word, part of a word, or a punctuation mark. The exact tokenization depends on the model's tokenizer.

### Token Counting Rules of Thumb

- **1 token is approximately 4 characters or 0.75 words** in English.
- A typical page of English text (500 words) is roughly 670 tokens.
- Code tends to use more tokens per line than prose because variable names, symbols, and whitespace each consume tokens.
- Non-English languages often require more tokens per word. Chinese, Japanese, and Korean text can use 1.5-2x more tokens per character compared to English.

### Counting Tokens Precisely

For exact counts, use the model's tokenizer:

```python
# OpenAI models use tiktoken
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")
text = "The context window determines how much text the model can process."
tokens = encoder.encode(text)
print(f"Text: {text}")
print(f"Token count: {len(tokens)}")
print(f"Tokens: {tokens}")
# Output: Token count: 12
```

```python
# For Claude, use the Anthropic token counting API
import anthropic

client = anthropic.Anthropic()
result = client.messages.count_tokens(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "How many tokens is this?"}]
)
print(f"Input tokens: {result.input_tokens}")
```

```python
# For open-source models, use the Hugging Face tokenizer
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
tokens = tokenizer.encode("Count these tokens for me.")
print(f"Token count: {len(tokens)}")
```

### Why Token Counting Matters for Costs

API providers charge per token. Every token in your input and output costs money. Here is what a 100K-token context looks like financially:

| Model | Input Cost (100K tokens) | Output Cost (1K tokens) |
|---|---|---|
| GPT-4o | $0.25 | $0.01 |
| Claude Sonnet | $0.30 | $0.015 |
| GPT-4o Mini | $0.015 | $0.0006 |
| Gemini 1.5 Flash | $0.0075 | $0.0003 |

Filling a large context window is not free. A single GPT-4o request with 100K input tokens and 2K output tokens costs about $0.27. Run that 10,000 times a day and you are looking at $2,700/day.

## Context Window Comparison Across Models

Model capabilities have expanded dramatically. Here is where major models stand:

### Proprietary Models

| Model | Context Window | Release | Notes |
|---|---|---|---|
| GPT-4o | 128K tokens | 2024 | ~96K words |
| GPT-4o Mini | 128K tokens | 2024 | Same window, much cheaper |
| Claude Sonnet/Opus | 200K tokens | 2024-2025 | ~150K words |
| Claude with extended thinking | 200K tokens | 2025 | Output can use more via thinking |
| Gemini 1.5 Pro | 1M tokens | 2024 | ~750K words, largest production window |
| Gemini 1.5 Flash | 1M tokens | 2024 | Same window, faster and cheaper |

### Open-Source Models

| Model | Context Window | Parameters | Notes |
|---|---|---|---|
| Llama 3.1 8B/70B | 128K tokens | 8B / 70B | Requires significant RAM at full context |
| Mistral Large | 128K tokens | ~100B | Strong multilingual performance |
| Qwen 2.5 | 128K tokens | 7B-72B | Good for Chinese + English |
| Yi-34B-200K | 200K tokens | 34B | Extended from base 4K via fine-tuning |
| Phi-3 Mini 128K | 128K tokens | 3.8B | Small model, large context |
| Command R+ | 128K tokens | 104B | Optimized for RAG |

## How Context Windows Actually Work

### The Attention Mechanism

The context window exists because of how transformers process text. The self-attention mechanism, which allows each token to "attend to" every other token, has computational cost that grows quadratically with sequence length. Processing 200K tokens requires roughly 4x the computation of processing 100K tokens.

```
Attention cost = O(n^2 * d)
where n = sequence length, d = embedding dimension
```

This is why longer context windows increase both latency and cost. The model is doing exponentially more work.

### Efficient Attention Variants

Modern models use techniques to reduce the quadratic cost:

- **Flash Attention**: Optimizes memory access patterns to speed up attention computation by 2-4x without changing the output. Nearly universal in current models.
- **Sliding Window Attention**: Each token only attends to a fixed window of nearby tokens rather than all tokens. Used in Mistral models.
- **Ring Attention**: Distributes the attention computation across multiple GPUs for very long sequences. Enables the million-token windows in Gemini.

These techniques make long context windows feasible, but they do not eliminate the fundamental cost increase.

## The "Lost in the Middle" Problem

A larger context window does not mean the model uses all of it equally well. Research from Liu et al. (2023) demonstrated a phenomenon called "lost in the middle": models are better at using information placed at the beginning or end of the context than information buried in the middle.

In their experiments, when a relevant fact was placed in the middle of a 20-document context, model accuracy dropped by 10-20% compared to when the same fact was at the beginning or end.

### What This Means in Practice

```
[System prompt]          <-- Model attends well here
[Document 1]             <-- Good attention
[Document 2]             <-- Good attention
...
[Document 10]            <-- Weaker attention ("lost in the middle")
[Document 11]            <-- Weaker attention
...
[Document 19]            <-- Improving attention
[Document 20]            <-- Good attention (recency)
[User question]          <-- Model attends well here
```

Newer models (GPT-4o, Claude Sonnet, Gemini 1.5 Pro) have improved on this significantly, but the effect has not been fully eliminated. When accuracy matters, place the most important information at the beginning of the context and repeat key details near the end.

## Practical Implications

### Conversation Length

Each message in a conversation accumulates tokens. A context window determines how long a conversation can be before the model starts losing earlier messages.

A rough breakdown for a 128K-token model:

| Component | Tokens | Cumulative |
|---|---|---|
| System prompt | 500 | 500 |
| Reserved for output | 4,000 | 4,500 |
| Available for conversation | 123,500 | 128,000 |
| Average message pair (user + assistant) | ~400 | -- |
| Maximum conversation turns | ~300 | -- |

In practice, you rarely reach 300 turns because earlier turns become less useful. Most applications implement a sliding window or summarization strategy.

### Document Processing

Context window size directly determines what you can fit in a single request:

| Content Type | Approximate Token Count |
|---|---|
| 1-page document | 500-700 tokens |
| 10-page report | 5,000-7,000 tokens |
| 50-page whitepaper | 25,000-35,000 tokens |
| Full novel (80,000 words) | ~107,000 tokens |
| Medium codebase (50 files) | 50,000-150,000 tokens |

With a 128K context, you can process a short novel or a medium codebase in a single request. With Gemini's 1M context, you can process most books.

### Code Analysis

Context window matters enormously for code tasks. A developer asking the model to refactor a function needs the model to see:

- The function itself
- The functions it calls
- The functions that call it
- Type definitions and interfaces
- Relevant tests

This often adds up to 10,000-50,000 tokens. For large-scale code analysis (reviewing an entire module or finding cross-file bugs), you may need 100K+ tokens of context.

## Strategies for Working Within Context Limits

### 1. Trim Conversation History

Instead of sending the entire conversation, keep only the most recent N turns plus a summary of earlier turns.

```python
def manage_conversation(messages: list, max_tokens: int = 100000) -> list:
    """Keep conversation within token budget."""
    total = count_tokens(messages)

    if total <= max_tokens:
        return messages

    # Keep system message and last 10 turns
    system = messages[0]
    recent = messages[-20:]  # 10 user + 10 assistant messages

    # Summarize older messages
    older = messages[1:-20]
    summary = summarize_messages(older)

    return [system, {"role": "user", "content": f"[Previous conversation summary: {summary}]"}] + recent
```

### 2. Use RAG Instead of Stuffing

Do not paste entire documents into the prompt when you only need specific sections. Use retrieval-augmented generation to find and inject only the relevant passages.

```python
# Instead of this (wasteful):
prompt = f"Here is the entire 200-page manual:\n{full_manual}\n\nQuestion: {question}"

# Do this (efficient):
relevant_chunks = retrieve_relevant_sections(question, manual_index)
prompt = f"Relevant sections:\n{relevant_chunks}\n\nQuestion: {question}"
```

This can reduce token usage by 90% or more while actually improving answer quality, because the model is not distracted by irrelevant content.

### 3. Compress and Filter

Remove boilerplate, whitespace, and irrelevant sections before injecting content into the context.

```python
def prepare_code_context(files: list[str]) -> str:
    """Prepare code files for LLM context, removing noise."""
    processed = []
    for filepath in files:
        with open(filepath) as f:
            code = f.read()
        # Remove comments that are not docstrings
        code = remove_inline_comments(code)
        # Remove blank lines
        code = "\n".join(line for line in code.split("\n") if line.strip())
        processed.append(f"# {filepath}\n{code}")
    return "\n\n".join(processed)
```

### 4. Choose the Right Model for the Job

If your task requires only a small context, do not use a large-context model just because it is available. Smaller context requests are faster and cheaper. Conversely, if you genuinely need to process a 500-page document, choose a model that can handle it without truncation -- Gemini 1.5 Pro's 1M context exists for exactly this purpose.

## Context Window vs. Output Length

An important distinction: the context window is the total capacity, but models also have a separate maximum output length. For most models, the maximum output is much shorter than the context window.

| Model | Context Window | Max Output |
|---|---|---|
| GPT-4o | 128K | 16K tokens |
| Claude Sonnet | 200K | 8K tokens (up to 64K with extended output) |
| Gemini 1.5 Pro | 1M | 8K tokens |
| Llama 3.1 70B | 128K | Varies by implementation |

This means you can input a lot of information, but the model's response is still bounded. If you need a very long output (generating a full report, for example), you need to break it into multiple requests, each generating a section.

## The Future of Context Windows

Context windows have grown from 2K (original GPT-3) to 1M (Gemini 1.5) in just a few years. Research continues to push this boundary further, with techniques like linear attention, state-space models (Mamba), and infinite context via recurrent memory.

But the practical lesson remains: a larger context window is a tool, not a solution. Structuring your prompts well, placing important information strategically, and using retrieval to select relevant content will outperform blindly stuffing tokens into a million-token window in almost every real application.
