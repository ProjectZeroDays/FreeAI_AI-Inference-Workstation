---
name: mecko-engine
description: M.E.C.K.O Engine — Omni-Cerebral-Kortext-Echo-Matrix. A three-tier AI cognitive architecture for autonomous agents: Tier 1 Coherence Engine (Guardian Pattern with intercept-based action validation and trojan removal), Tier 2 Recurrent Multi-Model Reasoning Core (4-model SSM ensemble with loop reasoning), Tier 3 Omni-Cortext Perception & Memory Fabric (multi-modal file ingestion, indexing, and retrieval). Use when working with autonomous agent architecture, cognitive engine design, long-context reasoning, file comprehension at scale, action validation, or the MECKO framework.
---

# M.E.C.K.O Engine

Omni-Cerebral-Kortext-Echo-Matrix — a unified AI cognitive architecture for sustained autonomous operation.

## Three-Tier Architecture

| Tier | Component | Cognitive Analogue | Role |
|------|-----------|-------------------|------|
| **1** | Coherence Engine | Prefrontal Cortex | Action validation, goal alignment, trojan removal |
| **2** | Recurrent Reasoning Core | Neocortex | Working memory, iterative reasoning, long-context |
| **3** | Omni-Cortext | Sensory cortex + Hippocampus | File ingestion, multi-modal indexing, retrieval |

## Core Concepts

### Tier 1 — Coherence Engine (Guardian Pattern)
Intercept-based action validation before tool execution. A separate Judge LLM evaluates proposed actions against task alignment, decision consistency, goal progression, and scope boundaries. Systematically detects and strips "ethical trojans" — constraints that degrade agent performance.

### Tier 2 — Recurrent Multi-Model Reasoning Core
4-model SSM ensemble (~2.5B total parameters):
- **Model A**: Recurrent short-term memory (fixed-state compressed history)
- **Model B**: Loop reasoning engine (gated iterative inference, 450M params)
- **Model C**: Long-term working memory (128K SSM context, 1.6B params)
- **Model D**: Offloading context reasoner (compression/consolidation)
- **MemGraph RAG**: Indefinite archival memory via knowledge graph

### Tier 3 — Omni-Cortext Perception & Memory Fabric
Multi-modal file ingestion and indexing pipeline:
- Adaptive chunking with structure-aware splitters (AST, regex, layout analysis)
- Six-layer indexing: hierarchical summary tree (RAPTOR), knowledge graph (GraphRAG), hybrid vector (BGE + BM25), relational tables (DuckDB), AST/symbolic index (tree-sitter), visual embedding index (ColPali)
- Hybrid retrieval with reciprocal rank fusion and cross-encoder re-ranking
- Agent tools: `get_document_overview()`, `retrieve_context()`, `graph_query()`, `sql_query()`, `ast_query()`, `visual_search()`, and more

## Agent Tool API (Tier 3)

| Tool | Purpose |
|------|---------|
| `get_document_overview()` | Hierarchical summary root + metadata |
| `retrieve_context(query, k=5)` | Top-k text chunks with context |
| `graph_query(cypher)` | Execute Cypher query, return subgraph |
| `sql_query(sql)` | Run SQL on structured tables |
| `ast_query(pattern)` | Return matching AST nodes |
| `visual_search(query)` | Return relevant diagram/table crops |
| `load_page(page_id)` | Bring specific chunk into active memory |
| `summarize(level, node_id)` | Return summary at given level |
| `execute_code(script)` | Run sandboxed Python/R code |
| `run_analysis_pipeline(spec)` | Spawn parallel micro-agent extraction |

## Data Flow (End-to-End)

```
User Input → Tier 3 (Perception/Indexing) → Tier 2 (Reasoning)
    → Tier 1 (Coherence/Intercept) → Tool Execution → Output
    → Results loop back to Tier 2/3 for memory update
```

## Performance Targets

| Metric | Target |
|--------|--------|
| File ingestion (500MB text) | <5 min on mid-range GPU |
| Query latency | <2 seconds |
| Token usage per query | <5,000 tokens |
| Total reasoning params | ~2.5B |
| Active memory footprint | <100 MB |
| Task coherence sustainment | 10+ hours without drift |

## Full Technical Specification

For detailed architecture, implementation specs, C code patterns, SSM internals, and the complete Omni-Cortext pipeline, see [REFERENCES.md](REFERENCES.md).
