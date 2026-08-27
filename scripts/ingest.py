#!/usr/bin/env python3
"""CLI for manual Qdrant RAG document ingestion.

Usage:
    python scripts/ingest.py --file docs/guide.md
    python scripts/ingest.py --dir config/documents
    python scripts/ingest.py --watch
    python scripts/ingest.py --query "how do I configure providers?"
    python scripts/ingest.py --collections
    python scripts/ingest.py --delete-collection freeai_docs
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.qdrant_sidecar import QdrantSidecar, load_rag_config, DEFAULT_DOCS_DIR


def cmd_ingest_file(sc: QdrantSidecar, args):
    count = sc.ingest_file(args.file)
    print(f"ingested {count} chunk(s) from {args.file}")


def cmd_ingest_dir(sc: QdrantSidecar, args):
    count = sc.ingest_directory(args.dir, recursive=args.recursive)
    print(f"ingested {count} chunk(s) from {args.dir}")


def cmd_query(sc: QdrantSidecar, args):
    results = sc.search(args.query, top_k=args.top_k)
    for r in results:
        print(f"[{r['score']:.4f}] {r['path']}#{r['chunk_index']}")
        print(f"  {r['text'][:200]}")
    print(f"\n{len(results)} results")


def cmd_collections(sc: QdrantSidecar, args):
    cols = sc.list_collections()
    if not cols:
        print("no collections")
        return
    for c in cols:
        print(f"  {c['name']:30s}  points={c['points_count']}")


def cmd_delete(sc: QdrantSidecar, args):
    sc.delete_collection(args.name)
    print(f"deleted collection '{args.name}'")


def cmd_watch(sc: QdrantSidecar, args):
    docs_dir = args.dir or str(DEFAULT_DOCS_DIR)
    print(f"[ingest] watching {docs_dir} (interval={args.interval}s)")
    sc.start_watcher(docs_dir)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[ingest] stopped")
        sc.stop_watcher()


def main():
    parser = argparse.ArgumentParser(description="Qdrant RAG ingestion CLI")
    parser.add_argument("--config", default=None, help="path to rag.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_file = sub.add_parser("file", help="ingest a single file")
    p_file.add_argument("--file", required=True, help="file path")

    p_dir = sub.add_parser("dir", help="ingest a directory")
    p_dir.add_argument("--dir", required=True, help="directory path")
    p_dir.add_argument("--no-recursive", action="store_true", default=False)

    p_query = sub.add_parser("query", help="run a search query")
    p_query.add_argument("query")
    p_query.add_argument("--top-k", type=int, default=10)

    p_coll = sub.add_parser("collections", help="list collections")

    p_del = sub.add_parser("delete-collection", help="delete a collection")
    p_del.add_argument("name")

    p_watch = sub.add_parser("watch", help="watch a directory for changes")
    p_watch.add_argument("--dir", default=None)
    p_watch.add_argument("--interval", type=int, default=30)

    args = parser.parse_args()
    cfg = load_rag_config(Path(args.config) if args.config else None)
    sc = QdrantSidecar(cfg)

    cmds = {
        "file": cmd_ingest_file,
        "dir": cmd_ingest_dir,
        "query": cmd_query,
        "collections": cmd_collections,
        "delete-collection": cmd_delete,
        "watch": cmd_watch,
    }
    cmds[args.cmd](sc, args)


if __name__ == "__main__":
    main()
