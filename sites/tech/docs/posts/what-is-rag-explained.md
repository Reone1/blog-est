---
title: "What Is RAG? Retrieval-Augmented Generation Explained"
date: "2026-03-31"
type: "explainer"
description: "A clear explanation of Retrieval-Augmented Generation (RAG), covering architecture, embeddings, vector databases, chunking strategies, and when to use RAG vs fine-tuning."
keywords: "what is retrieval augmented generation explained, rag explained, rag vs fine-tuning, vector database rag"
---

<div class="tldr">

**TL;DR:** RAG (Retrieval-Augmented Generation) is a technique that gives an LLM access to external knowledge by retrieving relevant documents at query time and injecting them into the prompt. Instead of relying solely on what the model memorized during training, RAG fetches up-to-date, domain-specific information from a knowledge base. The architecture has three stages: index your documents as vector embeddings, retrieve the most relevant chunks for each query, and generate a response using those chunks as context. RAG is the right choice when you need current information, source attribution, or domain-specific knowledge without the cost and complexity of fine-tuning.

</div>

## The Problem RAG Solves

Large language models are trained on a static snapshot of data. They do not know about events after their training cutoff, they cannot access your company's internal documents, and they sometimes fabricate plausible-sounding answers when they lack information (hallucination).

RAG addresses all three problems by connecting the LLM to a live knowledge base. At query time, the system retrieves relevant documents and includes them in the prompt, so the model generates answers grounded in actual source material.

Consider a customer support bot for a SaaS product. Without RAG, the LLM might hallucinate feature details or give outdated pricing. With RAG, it retrieves the current documentation and pricing pages, then generates an accurate answer with the source right there in context.

## How RAG Works: The Three Stages

### Stage 1: Indexing

Before you can retrieve documents, you need to process and store them. The indexing pipeline looks like this:

```
Raw Documents --> Chunking --> Embedding --> Vector Database
```

**Step 1: Load documents.** Gather your source material -- PDFs, web pages, Markdown files, database records, API responses.

**Step 2: Chunk the documents.** Split large documents into smaller pieces (chunks) that each contain a coherent unit of information. This is critical because embeddings work best on focused passages, not entire documents.

**Step 3: Generate embeddings.** Convert each chunk into a dense vector (a list of numbers) that captures its semantic meaning. Similar texts produce similar vectors.

**Step 4: Store in a vector database.** Save the vectors alongside their source text in a database optimized for similarity search.

```python
from openai import OpenAI
import chromadb

client = OpenAI()
chroma = chromadb.PersistentClient(path="./vectordb")
collection = chroma.get_or_create_collection("knowledge_base")

def index_documents(documents: list[dict]):
    """Index a list of documents into the vector database.

    Each document is a dict with 'text' and 'metadata' keys.
    """
    for i, doc in enumerate(documents):
        chunks = chunk_text(doc["text"], chunk_size=512, overlap=50)

        for j, chunk in enumerate(chunks):
            embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            ).data[0].embedding

            collection.add(
                ids=[f"doc-{i}-chunk-{j}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{**doc["metadata"], "chunk_index": j}]
            )
```

### Stage 2: Retrieval

When a user asks a question, the system converts the query into an embedding using the same model, then searches the vector database for the most similar chunks.

```python
def retrieve(query: str, n_results: int = 5) -> list[str]:
    """Retrieve the most relevant chunks for a query."""
    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0]  # List of chunk texts
```

Vector similarity search is fast -- most vector databases handle millions of vectors with sub-100ms query times.

### Stage 3: Generation

The retrieved chunks are injected into the LLM prompt as context. The model generates a response grounded in this context.

```python
def rag_query(user_question: str) -> str:
    """Full RAG pipeline: retrieve context, then generate answer."""
    # Retrieve relevant chunks
    chunks = retrieve(user_question, n_results=5)
    context = "\n\n---\n\n".join(chunks)

    # Generate answer with context
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the user's question based on the provided context. "
                    "If the context doesn't contain enough information, say so. "
                    "Cite which parts of the context support your answer."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {user_question}"
            }
        ]
    )

    return response.choices[0].message.content
```

## Embeddings: The Core Mechanism

An embedding model converts text into a fixed-length vector (typically 256 to 3,072 dimensions). The key property is that semantically similar texts produce vectors that are close together in vector space.

For example, the sentences "How do I reset my password?" and "I need to change my login credentials" would produce vectors with high cosine similarity (0.85+), even though they share few words.

### Choosing an Embedding Model

| Model | Dimensions | Performance (MTEB) | Cost per 1M Tokens |
|---|---|---|---|
| OpenAI text-embedding-3-small | 1536 | 62.3 | $0.02 |
| OpenAI text-embedding-3-large | 3072 | 64.6 | $0.13 |
| Cohere embed-v3 | 1024 | 64.5 | $0.10 |
| Voyage voyage-3 | 1024 | 67.1 | $0.06 |
| BGE-M3 (open source) | 1024 | 63.5 | Free (self-hosted) |

For most applications, `text-embedding-3-small` offers the best balance of quality and cost. If retrieval accuracy is critical, test Voyage or Cohere on your specific data.

## Chunking Strategies

How you split documents into chunks has a major impact on retrieval quality. Chunks that are too large dilute relevant information with noise. Chunks that are too small lose context.

### Fixed-Size Chunking

The simplest approach: split text every N tokens with some overlap.

```python
def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap  # overlap for context continuity

    return chunks
```

Good default: 400-600 tokens per chunk, 50-100 token overlap.

### Semantic Chunking

Split at natural boundaries (paragraphs, sections, sentence groups) rather than at arbitrary positions. This preserves the coherence of each chunk.

```python
import re

def semantic_chunk(text: str, max_tokens: int = 600) -> list[str]:
    """Split text at paragraph boundaries, merging small paragraphs."""
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len((current_chunk + para).split()) > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
```

### Hierarchical Chunking

For structured documents (documentation, legal texts, technical manuals), chunk by section and maintain parent-child relationships. When a specific chunk is retrieved, you can optionally include its parent section for broader context.

### Which Strategy to Use

| Document Type | Recommended Strategy | Chunk Size |
|---|---|---|
| Unstructured text (articles, transcripts) | Fixed-size with overlap | 400-600 tokens |
| Structured docs (manuals, docs sites) | Semantic (by section/heading) | 300-800 tokens |
| Code files | Semantic (by function/class) | Varies |
| Legal/regulatory | Hierarchical | 200-400 tokens |

## Vector Databases

A vector database stores embeddings and supports fast similarity search. Here are the main options:

### Managed Services

- **Pinecone**: Fully managed, serverless option available, strong ecosystem integrations.
- **Weaviate Cloud**: Hybrid search (vector + keyword), GraphQL API.
- **Qdrant Cloud**: High performance, filtering capabilities, open-source core.

### Self-Hosted

- **ChromaDB**: Simple, Python-native, good for prototypes and small to medium datasets.
- **Qdrant**: Production-grade, supports on-disk storage for large datasets.
- **pgvector**: PostgreSQL extension -- use your existing Postgres infrastructure.
- **Milvus**: Designed for billion-scale vector search.

For most teams starting out, ChromaDB (for prototyping) or pgvector (if you already use PostgreSQL) are the pragmatic choices.

```python
# pgvector example with SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, Text
from pgvector.sqlalchemy import Vector

engine = create_engine("postgresql://localhost/ragdb")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    embedding = Column(Vector(1536))  # matches embedding model dimensions

# Query with cosine similarity
from sqlalchemy import select, func

stmt = (
    select(Document)
    .order_by(Document.embedding.cosine_distance(query_embedding))
    .limit(5)
)
results = session.execute(stmt).scalars().all()
```

## Advanced RAG Techniques

### Hybrid Search

Combine vector similarity with keyword search (BM25) for better retrieval. Vector search catches semantic matches; keyword search catches exact terms that embeddings might miss.

```python
# Using Qdrant's built-in hybrid search
from qdrant_client import QdrantClient, models

client = QdrantClient("localhost", port=6333)

results = client.query_points(
    collection_name="documents",
    prefetch=[
        models.Prefetch(query=sparse_vector, using="bm25", limit=20),
        models.Prefetch(query=dense_vector, using="dense", limit=20),
    ],
    query=models.FusionQuery(fusion=models.Fusion.RRF),  # Reciprocal Rank Fusion
    limit=5
)
```

### Re-Ranking

After retrieving an initial set of candidates, use a cross-encoder model to re-rank them for higher precision.

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Initial retrieval: get 20 candidates
candidates = retrieve(query, n_results=20)

# Re-rank to find the best 5
pairs = [[query, doc] for doc in candidates]
scores = reranker.predict(pairs)

top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
reranked = [candidates[i] for i in top_indices]
```

Re-ranking typically improves answer relevance by 10-20% compared to vector search alone.

### Query Transformation

Rewrite the user's query before retrieval to improve match quality:

- **HyDE (Hypothetical Document Embedding):** Have the LLM generate a hypothetical answer, then embed that answer for retrieval. This can improve recall because the hypothetical answer is more semantically similar to the actual document than the question is.
- **Multi-query:** Generate multiple reformulations of the query and retrieve for each, then deduplicate results.

## RAG vs Fine-Tuning: When to Use Which

| Factor | RAG | Fine-Tuning |
|---|---|---|
| Knowledge updates | Instant (update documents) | Requires retraining |
| Source attribution | Built-in (retrieved chunks) | Not available |
| Setup complexity | Moderate (embedding + vector DB) | Low (API call) |
| Cost | Ongoing retrieval + larger prompts | One-time training cost |
| Domain adaptation | Good for factual knowledge | Better for style and format |
| Hallucination control | Strong (grounded in sources) | Moderate |

**Use RAG when:**
- Your knowledge base changes frequently.
- You need citations and source attribution.
- You need answers grounded in specific documents.
- You have a large corpus (thousands of documents).

**Use fine-tuning when:**
- You need the model to adopt a specific tone, format, or style.
- You want to teach the model a specific reasoning pattern.
- Your task is narrow and well-defined (classification, extraction).
- You need to reduce prompt size (baked-in knowledge, no retrieval needed).

**Use both when:**
- You need domain-specific behavior AND access to a changing knowledge base. Fine-tune for format and reasoning, RAG for factual grounding.

## Common RAG Pitfalls

**Retrieval misses.** The most relevant document is not in the top results. Fix: improve chunking, add hybrid search, or use query expansion.

**Context window overflow.** Too many retrieved chunks exceed the model's context limit. Fix: retrieve fewer chunks, summarize chunks before injection, or use a model with a larger context window.

**Irrelevant retrieval.** The vector search returns topically related but not actually useful documents. Fix: add metadata filtering (date ranges, categories), use re-ranking, or increase the similarity threshold.

**Chunk boundary problems.** Important information is split across two chunks. Fix: increase chunk overlap or use hierarchical chunking to include surrounding context.

## Getting Started

A minimal RAG system requires just three components: an embedding model (OpenAI's text-embedding-3-small), a vector store (ChromaDB), and an LLM (any chat model). You can have a working prototype in under 100 lines of Python using the code samples in this article.

Start simple, measure retrieval quality by testing with real queries, then add complexity (hybrid search, re-ranking, query transformation) only where measurements show gaps.
