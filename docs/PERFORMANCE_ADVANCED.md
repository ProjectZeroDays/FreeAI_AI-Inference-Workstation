# Performance -- Advanced Tuning (ROADMAP 7)

These are llama.cpp flags / techniques, enabled via env. The stack exposes them; you opt in.

| Technique | Flag | When to use |
|---|---|---|
| CUDA graphs | `LLAMA_CUDA_GRAPHS=1` | small batch, low latency |
| Quantized KV cache | `--cache-type-k q4_0 --cache-type-v q4_0` via `LLAMA_EXTRA_ARGS` | 32K+ ctx on 24GB |
| Speculative decoding | `--spec-type draft-mtp --spec-draft-n-max 6` + `DOWNLOAD_MTP=1` | Qwythos v2 MTP |
| Tensor parallelism | `LLAMA_TP=2` (requires 2 GPUs, `--profile llama2` + `CUDA_VISIBLE_DEVICES`) | 70B on 2×4090 |
| Micro-batching | `LLAMA_BATCH=512` | high concurrency |
| Prompt compression | `LLAMA_EXTRA_ARGS="--rope-freq-base 500000"` + repo-map summarizer | 64K ctx |
| Response streaming | already: SSE `/route?stream=1` and `ws://:8011/ws/route` end-to-end | -- |

vLLM prefix caching is on by default (`--enable-prefix-caching`).
