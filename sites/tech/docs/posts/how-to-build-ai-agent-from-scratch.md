---
title: "How to Build an AI Agent from Scratch with Python"
date: "2026-03-31"
type: "how-to"
description: "A practical guide to building an AI agent from scratch using the ReAct pattern, tool use, and memory. Includes full Python implementation with Claude and OpenAI APIs."
keywords: "how to build ai agent from scratch, ai agent python, react agent pattern, llm tool use"
---

<div class="tldr">

**TL;DR:** An AI agent is an LLM that can reason about problems and take actions by calling tools in a loop. The core pattern is simple: the model thinks, decides which tool to call, observes the result, then repeats until the task is done. You can build a functional agent in under 200 lines of Python using the ReAct (Reason + Act) pattern with either the Claude or OpenAI API. The key components are a reasoning loop, tool definitions, an execution layer, and a memory system.

</div>

## What Makes an Agent Different from a Chatbot?

A chatbot takes a prompt and returns a response. An agent takes a goal and works toward it autonomously, calling tools, interpreting results, and adjusting its approach based on what it observes.

The difference is the loop. A chatbot runs inference once. An agent runs inference repeatedly, using each response to decide the next action.

Concretely, an agent needs three things a chatbot does not:

1. **Tools** -- functions the agent can call (web search, database queries, file operations, APIs).
2. **A reasoning loop** -- logic that feeds tool results back to the model and asks "what next?"
3. **Memory** -- a way to accumulate context across multiple steps.

## The ReAct Pattern

ReAct (Reasoning + Acting) is the most widely used agent architecture. Published by Yao et al. in 2022, it interleaves chain-of-thought reasoning with tool use. The loop looks like this:

```
1. THINK: Reason about the current state and what to do next
2. ACT: Call a tool with specific arguments
3. OBSERVE: Read the tool's output
4. Repeat until the task is complete, then return a final answer
```

This pattern works because it forces the model to articulate its reasoning before acting, which improves accuracy and makes the agent's behavior interpretable.

## Project Setup

We will build a ReAct agent in Python that can answer questions by searching the web and performing calculations. The full implementation requires only the `anthropic` or `openai` SDK and the `requests` library.

```bash
mkdir ai-agent && cd ai-agent
python -m venv venv
source venv/bin/activate
pip install anthropic requests
```

Set your API key:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Step 1: Define Your Tools

Tools are Python functions with clear descriptions that the LLM can understand. Each tool needs a name, a description, input parameters, and an execution function.

```python
import requests
import json
import math

# Tool definitions for the LLM
TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for current information. Use this when you need up-to-date facts, statistics, or information you don't know.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculator",
        "description": "Perform mathematical calculations. Use this for any arithmetic, unit conversions, or numerical analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python math expression to evaluate, e.g. '2**10' or 'math.sqrt(144)'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "final_answer",
        "description": "Provide the final answer to the user's question. Call this when you have gathered enough information to fully answer the question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "The complete final answer"
                }
            },
            "required": ["answer"]
        }
    }
]
```

## Step 2: Implement Tool Execution

Each tool definition maps to a real Python function. The execution layer dispatches tool calls to the right function and returns results.

```python
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string."""

    if tool_name == "web_search":
        return _web_search(tool_input["query"])

    elif tool_name == "calculator":
        return _calculator(tool_input["expression"])

    elif tool_name == "final_answer":
        return tool_input["answer"]

    else:
        return f"Error: Unknown tool '{tool_name}'"


def _web_search(query: str) -> str:
    """Search using SerpAPI (replace with your preferred search API)."""
    api_key = os.environ.get("SERPAPI_KEY", "")
    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
        "num": 3
    }
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = resp.json()
        results = []
        for item in data.get("organic_results", [])[:3]:
            results.append(f"- {item['title']}: {item.get('snippet', 'No snippet')}")
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {e}"


def _calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    allowed_names["abs"] = abs
    allowed_names["round"] = round
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"
```

## Step 3: Build the Agent Loop

This is the core of the agent. It sends messages to the LLM, checks if the response includes tool calls, executes them, appends the results, and loops.

```python
import os
import anthropic


def run_agent(user_query: str, max_steps: int = 10, verbose: bool = True) -> str:
    """Run the ReAct agent loop until a final answer is produced."""

    client = anthropic.Anthropic()

    system_prompt = (
        "You are a helpful research agent. You can search the web and perform "
        "calculations to answer questions. Think step by step. When you have "
        "enough information, use the final_answer tool to respond."
    )

    messages = [{"role": "user", "content": user_query}]

    for step in range(max_steps):
        if verbose:
            print(f"\n--- Step {step + 1} ---")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        # Check if the model wants to use tools
        if response.stop_reason == "tool_use":
            # Add the assistant's response to the conversation
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    if verbose:
                        print(f"Tool: {tool_name}({json.dumps(tool_input)})")

                    # Check for final answer
                    if tool_name == "final_answer":
                        return tool_input["answer"]

                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)

                    if verbose:
                        print(f"Result: {result[:200]}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            # Model responded with text only (no tool call)
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text

    return "Agent reached maximum steps without producing a final answer."
```

## Step 4: Add Conversation Memory

The basic agent above stores context within a single run. For a persistent agent that remembers across conversations, add a simple memory store.

```python
import hashlib
from datetime import datetime


class AgentMemory:
    """Simple memory system that stores facts and retrieves relevant ones."""

    def __init__(self):
        self.facts: list[dict] = []
        self.conversation_history: list[dict] = []

    def store_fact(self, fact: str, source: str = "agent"):
        """Store a learned fact with metadata."""
        self.facts.append({
            "fact": fact,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "id": hashlib.md5(fact.encode()).hexdigest()[:8]
        })

    def get_relevant_facts(self, query: str, max_facts: int = 5) -> list[str]:
        """Retrieve facts relevant to a query using keyword matching.

        For production systems, replace this with vector similarity search.
        """
        query_words = set(query.lower().split())
        scored = []
        for entry in self.facts:
            fact_words = set(entry["fact"].lower().split())
            overlap = len(query_words & fact_words)
            if overlap > 0:
                scored.append((overlap, entry["fact"]))
        scored.sort(reverse=True)
        return [fact for _, fact in scored[:max_facts]]

    def get_context_string(self, query: str) -> str:
        """Format relevant memories as context for the system prompt."""
        facts = self.get_relevant_facts(query)
        if not facts:
            return ""
        formatted = "\n".join(f"- {f}" for f in facts)
        return f"\n\nRelevant information from previous interactions:\n{formatted}"
```

Integrate memory into the agent by prepending relevant facts to the system prompt before each run:

```python
memory = AgentMemory()

def run_agent_with_memory(user_query: str, memory: AgentMemory) -> str:
    context = memory.get_context_string(user_query)
    system_prompt = (
        "You are a helpful research agent. You can search the web and perform "
        "calculations to answer questions. Think step by step."
        f"{context}"
    )
    # ... rest of the agent loop, same as before
```

## Step 5: Using OpenAI Instead of Claude

The same architecture works with OpenAI. The main difference is the tool call format.

```python
from openai import OpenAI


def run_agent_openai(user_query: str, max_steps: int = 10) -> str:
    client = OpenAI()

    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            }
        }
        for tool in TOOLS
    ]

    messages = [
        {"role": "system", "content": "You are a helpful research agent."},
        {"role": "user", "content": user_query},
    ]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=openai_tools,
        )

        choice = response.choices[0]
        messages.append(choice.message)

        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if name == "final_answer":
                    return args["answer"]

                result = execute_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            return choice.message.content

    return "Max steps reached."
```

## Putting It All Together

Here is how to run the complete agent:

```python
if __name__ == "__main__":
    query = "What is the population of Tokyo, and what percentage of Japan's total population does that represent?"
    answer = run_agent(query, verbose=True)
    print(f"\nFinal Answer: {answer}")
```

A typical execution trace looks like this:

```
--- Step 1 ---
Tool: web_search({"query": "Tokyo population 2026"})
Result: - Tokyo Population 2026: The Greater Tokyo Area has approximately 37.1 million residents...

--- Step 2 ---
Tool: web_search({"query": "Japan total population 2026"})
Result: - Japan Population: Japan's population stands at approximately 122.5 million...

--- Step 3 ---
Tool: calculator({"expression": "(37.1 / 122.5) * 100"})
Result: 30.285714285714285

--- Step 4 ---
Tool: final_answer({"answer": "Tokyo's Greater Metropolitan Area has approximately 37.1 million residents, which represents about 30.3% of Japan's total population of 122.5 million."})

Final Answer: Tokyo's Greater Metropolitan Area has approximately 37.1 million residents...
```

## Error Handling and Robustness

Production agents need guardrails. Add these to your implementation:

```python
# 1. Timeout per step
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Step timed out")

# 2. Retry logic for API failures
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def call_llm(client, messages, tools, system_prompt):
    return client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        tools=tools,
        messages=messages,
    )

# 3. Cost tracking
def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    rates = {
        "claude-sonnet-4-20250514": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
        "gpt-4o": {"input": 2.5 / 1_000_000, "output": 10.0 / 1_000_000},
    }
    r = rates.get(model, rates["claude-sonnet-4-20250514"])
    return input_tokens * r["input"] + output_tokens * r["output"]
```

## Common Pitfalls and How to Avoid Them

**Infinite loops.** Always set `max_steps` and enforce it. Some queries cause the model to repeatedly search without converging.

**Tool errors crashing the loop.** Wrap every `execute_tool` call in a try/except and return the error message as the tool result. The LLM can often recover from errors by trying a different approach.

**Context window overflow.** As the conversation grows, you may exceed the model's context limit. Implement a summarization step that compresses older messages when the total token count approaches the limit.

**Hallucinated tool names.** The model may try to call tools that do not exist. Always validate tool names against your registered set before executing.

## Next Steps

This agent handles simple research tasks, but you can extend it significantly:

- **Add more tools**: file I/O, database queries, code execution, API integrations.
- **Implement planning**: Before the ReAct loop, have the model create a step-by-step plan, then execute it.
- **Add vector memory**: Replace the keyword-based memory with embeddings and a vector database for better retrieval.
- **Multi-agent orchestration**: Have specialized agents delegate subtasks to each other.

The ReAct pattern is the foundation that most agent frameworks (LangChain, CrewAI, AutoGen) build on. Understanding it from scratch gives you the ability to debug, customize, and optimize agent behavior far beyond what pre-built frameworks allow.
