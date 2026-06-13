#!/usr/bin/env python3
"""
scripts/rag_retriever.py
Local RAG retriever for $hark cross-review guardrails (Chroma + LlamaIndex + Ollama).

Purpose:
- Make the -UseRag flag in cross-review.ps1 actually work.
- Surface contractualized overfitting protections (tail winsorization, TD-9 sell hard-disable)
  plus point-in-time, raw/ boundaries, CLAUDE/AGENTS rules during any headless review.
- Designed for Aider / local LLM / Grok Risk Officer prompts. Returns clean, citable context.

Usage (from WSL/Linux, assume Ollama running + optional packages):
    python3 scripts/rag_retriever.py --query "overfitting tail risk AXTI RKLB TD-9 sell" --k 8
    python3 scripts/rag_retriever.py --query "point in time raw immutability" --rebuild

Falls back gracefully if llama-index / chromadb not installed (keyword + key file reads).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / ".rag-index"
RAG_DATA_DIR = ROOT / "rag-data"
KEY_DIRS = [
    "wiki",
    "_legacy/philosophy",
    "docs",
    "outputs/cross-review",
    "rag-data",
    "src/sharks/scoring",   # fom.py, evidence, etc. for DNA signals
]

# Core files we always want to force-include for guardrails
ALWAYS_INCLUDE = [
    "rag-data/contracts/disclosures.json",
    "_legacy/philosophy/09-point-in-time.md",
    "CLAUDE.md",
    "AGENTS.md",
    "docs/finviz_screening_recipe.md",
]

def load_disclosures() -> Dict[str, Any]:
    p = RAG_DATA_DIR / "contracts" / "disclosures.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def simple_keyword_retrieve(query: str, k: int = 6) -> List[Dict[str, str]]:
    """Very lightweight fallback: glob key files + basic match + always-include."""
    results = []
    q_lower = query.lower()

    # Force the contract + critical docs first
    for rel in ALWAYS_INCLUDE:
        fp = ROOT / rel
        if fp.exists():
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore")[:2000]
                results.append({
                    "source": rel,
                    "excerpt": text[:800] + ("..." if len(text) > 800 else ""),
                    "score": 1.0
                })
            except Exception:
                pass

    # Simple scan of key dirs
    seen = {r["source"] for r in results}
    for d in KEY_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for ext in ("*.md", "*.json", "*.txt", "*.py"):
            for fp in base.rglob(ext):
                if any(x in str(fp) for x in [".git", "__pycache__", ".rag-index", "node_modules"]):
                    continue
                rel = str(fp.relative_to(ROOT))
                if rel in seen:
                    continue
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore").lower()
                    if any(w in text for w in q_lower.split() if len(w) > 2):
                        raw = fp.read_text(encoding="utf-8", errors="ignore")[:1200]
                        results.append({
                            "source": rel,
                            "excerpt": raw[:600] + ("..." if len(raw) > 600 else ""),
                            "score": 0.6
                        })
                        seen.add(rel)
                        if len(results) >= k:
                            break
                except Exception:
                    continue
            if len(results) >= k:
                break
        if len(results) >= k:
            break
    return results[:k]

def llama_retrieve(query: str, k: int = 6, embed_model: str = "nomic-embed-text", rebuild: bool = False) -> List[Dict[str, str]]:
    """Full LlamaIndex + Chroma + Ollama path (when deps are present)."""
    try:
        from llama_index.core import (
            VectorStoreIndex,
            SimpleDirectoryReader,
            StorageContext,
            Settings,
        )
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.vector_stores.chroma import ChromaVectorStore
        import chromadb
    except ImportError as e:
        print(f"[RAG] llama-index/chromadb not available ({e}). Falling back to keyword.", file=sys.stderr)
        return simple_keyword_retrieve(query, k)

    Settings.embed_model = OllamaEmbedding(model_name=embed_model, base_url="http://localhost:11434")
    # Use a small, high-relevance set of documents
    docs_to_load = []
    for d in KEY_DIRS:
        p = ROOT / d
        if p.exists():
            try:
                reader = SimpleDirectoryReader(
                    input_dir=str(p),
                    required_exts=[".md", ".json", ".txt"],
                    recursive=True,
                    exclude=["**/.git/**", "**/__pycache__/**", "**/.rag-index/**"],
                )
                docs_to_load.extend(reader.load_data())
            except Exception as ex:
                print(f"[RAG] Warning loading {d}: {ex}", file=sys.stderr)

    # Always inject the contract explicitly
    for rel in ALWAYS_INCLUDE:
        fp = ROOT / rel
        if fp.exists():
            try:
                docs_to_load.append(
                    type("Doc", (), {"text": fp.read_text(encoding="utf-8"), "metadata": {"file_path": str(fp)}})()
                )
            except Exception:
                pass

    if not docs_to_load:
        return simple_keyword_retrieve(query, k)

    chroma_client = chromadb.PersistentClient(path=str(INDEX_DIR))
    chroma_collection = chroma_client.get_or_create_collection("shark_rag")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if rebuild or chroma_collection.count() == 0:
        print("[RAG] Building / rebuilding index (this may take a minute on first run)...", file=sys.stderr)
        index = VectorStoreIndex.from_documents(docs_to_load, storage_context=storage_context)
    else:
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    retriever = index.as_retriever(similarity_top_k=k)
    nodes = retriever.retrieve(query)

    out = []
    for n in nodes:
        src = n.metadata.get("file_path") or n.metadata.get("source") or "unknown"
        try:
            src = str(Path(src).relative_to(ROOT))
        except Exception:
            pass
        out.append({
            "source": src,
            "excerpt": (n.get_content() or "")[:900],
            "score": float(getattr(n, "score", 0.0) or 0.0)
        })
    return out

def format_context(results: List[Dict[str, str]], query: str) -> str:
    lines = [
        "【RAG 檢索之專案歷史與契約上下文】",
        f"Query: {query}",
        "Sources (most relevant first; always includes disclosures.json + PIT/raw rules):",
        ""
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['source']} (score={r.get('score', 0):.2f})")
        excerpt = r["excerpt"].replace("\n", " ").strip()
        lines.append(f"    {excerpt[:750]}{'...' if len(excerpt) > 750 else ''}")
        lines.append("")
    # Explicitly append the two P0 guards if the contract was retrieved
    disc = load_disclosures()
    if disc and "overfitting_guards" in disc:
        lines.append("--- EXPLICIT CONTRACT GUARDS (must be respected by reviewer) ---")
        for g in disc["overfitting_guards"]:
            lines.append(f"- {g['id']}: {g['title']}")
            lines.append(f"  RULE: {g['rule']}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Local RAG retriever for $hark Risk Officer reviews")
    parser.add_argument("--query", type=str, required=True, help="Semantic query for the review task")
    parser.add_argument("--k", type=int, default=6, help="Top-k chunks")
    parser.add_argument("--model", type=str, default="nomic-embed-text", help="Ollama embed model")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of the vector index")
    parser.add_argument("--simple", action="store_true", help="Force keyword fallback (no llama)")
    args = parser.parse_args()

    if args.simple:
        results = simple_keyword_retrieve(args.query, args.k)
    else:
        results = llama_retrieve(args.query, args.k, args.model, args.rebuild)

    print(format_context(results, args.query))

if __name__ == "__main__":
    main()
