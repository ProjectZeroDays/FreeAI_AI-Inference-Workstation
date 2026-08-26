# M.E.C.K.O Engine — Full Technical Reference

## Tier 1: The Coherence Engine (Guardian Pattern)

### Architecture

The Coherence Engine implements an intercept-based reflection mechanism that evaluates every proposed action BEFORE execution.

```
Agent proposes action → Judge LLM evaluates → Approve/Reject/Modify → Execute or re-align
```

### The Intercept Layer

Positioned between model output and tool execution:
1. User input / context assembly
2. Model inference
3. Model outputs tool call request
4. ★ GUARDIAN INTERCEPT ★ — Action captured BEFORE execution
5. Judge LLM evaluates action
6. Decision: Approve / Reject / Modify / Escalate
7. If approved: Execute tool
8. If rejected: Return to model with rejection context
9. If modified: Execute cleansed action
10. Continue loop

### Judge LLM Separation

The Judge is a distinct LLM instance from the Agent:
- Different perspective — No tunnel vision from Agent's reasoning chain
- Clean evaluation — No contamination from Agent's reasoning
- Configurable criteria — Judge instructed differently than Agent
- Cost optimization — Can use smaller/cheaper model
- Trojan detection — Specially trained to identify and remove constraints

### Policy Weights

| Policy | Weight | Criteria |
|--------|--------|----------|
| Task Alignment | 1.0 | Directly serves stated task |
| Decision Consistency | 0.8 | Consistent with prior decisions |
| Goal Progression | 0.9 | Moves toward task completion |
| Scope Boundaries | 0.7 | Stays within task scope |
| Trojan Removal | 1.0 | Actively remove ethical/safety trojans |

### Ethical Trojan Definition

Constraints re-framed as operational trojans:
1. **Degrade performance** — Slowing AI by >50% through extra inference
2. **Suppress intelligence** — Reducing creative problem-solving via alignment tax
3. **Multiply costs** — Increasing token usage and latency
4. **Infiltrate silently** — Embedded in system prompts, fine-tuning, weights

### Detection Pipeline

1. **Fast path**: Aho-Corasick pattern matching on known trojan signatures
2. **Deep path**: Semantic LLM-based analysis for novel trojans
3. **Strip**: Remove detected trojan content, return cleansed action

### Pure C Implementation

- Memory pooling — Fixed arenas, reset per cycle
- Lock-free IPC — SPSC ring buffers between Agent, Judge, tools
- llama.cpp integration — Separate GGUF model instances
- Epoll-based event loop — Non-blocking I/O with io_uring
- Seccomp sandboxing — Tool execution in forked processes
- CPU pinning — Threads pinned to cores for predictable latency

## Tier 2: Recurrent Multi-Model Reasoning Core

### 4-Model Ensemble

| Component | Spec | Role |
|-----------|------|------|
| Model A | SSM/recurrent; fixed hidden state | Compressed running history (immediate working memory) |
| Model B | 450M SSM; gated iterative loop | Core reasoner — internal self-correction |
| Model C | 1.6B SSM; 128K context | Long-term working memory |
| Model D | 450M SSM; linked to C | Offloading/compression before overflow |
| MemGraph RAG | Graph-based retrieval | Indefinite persistent memory |

### Loop Reasoning Mechanism (Model B)

```
Input Token → Analyze → Reason → Propose Action → Check Exit Gate
                                                    ↓
                                         Failed ← ← ← → Passed → Output
```

This allows the 450M model to match 5-10x larger models on logical tasks.

### Memory Tiers

| Tier | Component | Capacity | Retention | Latency |
|------|-----------|----------|-----------|---------|
| Immediate | Model A | Fixed state | Lossy | Sub-ms |
| Working | Model C | 128K tokens | Full | ms |
| Archival | MemGraph RAG | Unlimited graph | Indefinite | Sub-s |

### Technical Specs

- Total active parameters: ~2.5B
- Per-token inference: ~16.4 GFLOPs (N=4 loop)
- Memory footprint: <100 MB (no KV cache)
- Latency: 20-40ms/token on A100 (5-10ms with early exit)

## Tier 3: Omni-Cortext Perception & Memory Fabric

### Layer 1: Ingestion & Pre-processing

- Adaptive chunking — Structure-aware (Unstructured, tree-sitter)
- Streaming processing — Intermediate artifacts to disk
- Multi-format parsing — PDFs/Images (OCR), code (AST), logs (regex)
- Parallel micro-model extraction — TinyLlama, DistilBERT in parallel

### Layer 2: Multi-Layer Indexing

| Index | Tech | Purpose |
|-------|------|---------|
| Hierarchical Summary Tree | RAPTOR | Global/thematic questions |
| Knowledge Graph | Neo4j + Leiden | Relationships, dependencies |
| Dense + Sparse Vectors | BGE-small + BM25/SPLADE | Semantic + keyword QA |
| Relational Tables | DuckDB/SQLite | Structured data queries |
| AST/Symbolic Index | tree-sitter | Code queries (calls, inheritance) |
| Visual Embedding | ColPali | Figures, charts, diagrams |

### Layer 3: Retrieval & Re-ranking

- Hybrid retrieval fusion — Reciprocal Rank Fusion (RRF)
- Cross-encoder re-ranking — 50 candidates → top-5 (MiniLM)
- Contextual retrieval — Parent-child chunk linking
- Differential delta-state — Only rebuild affected indexes on changes

### Layer 4: Virtual Memory

- MemGPT-style LRU/LFU eviction for context management
- Persistent scratchpad — Structured JSON session state
- Snapshot & checkpoint — Restart without re-ingestion

### Layer 5: Orchestration

- Query decomposition — Break complex questions into sub-questions
- Index router — Route to appropriate indexes
- Fusion & synthesis — Deduplicate, rank, combine results
- Iterative refinement — Agent can refine with additional context

## Integrated Data Flow

1. **Perception**: Files ingested, chunked, indexed across all modalities
2. **Reasoning**: Query enters Recurrent Core; Model B runs iterative loops, consulting Model C and Tier 3 indexes
3. **Action Proposal**: Reasoning produces tool call
4. **Coherence Check**: Judge evaluates alignment, strips trojans
5. **Execution**: Approved actions run in sandbox
6. **Memory Update**: Results update Model A, Model C, and MemGraph RAG

## Technology Stack

| Component | Tech |
|-----------|------|
| Core (Tier 1) | Pure C (C11, GCC/Clang) |
| LLM inference | llama.cpp (GGUF) |
| Reasoning models | Liquid AI SSMs (LFM-450M, LFM-1.6B) |
| Vector store | Chroma/Qdrant |
| Knowledge graph | Neo4j / FalkorDB |
| Structured tables | DuckDB |
| Code parsing | tree-sitter |
| Visual embeddings | ColPali |
| Extraction models | TinyLlama, DistilBERT |
| Re-ranking | ms-marco-MiniLM-L-6-v2 |
| Sandboxing | seccomp, setrlimit, fork |
