# RAG (Qdrant)

`--profile rag` starts `qdrant:6333` + an ingest watcher that chunks `docs/` + `README.md` (800 chars, 120 overlap), embeds via MiniLM (hash fallback in CI), and upserts to collection `tokugawa_docs`. Query: `python rag/ingest.py --query "how to add a provider?"` or `GET /query` on the ingest API. Router can augment prompts via a RAG pre-step in workflow templates.
