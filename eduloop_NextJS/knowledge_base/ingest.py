#!/usr/bin/env python3
"""
EduLoop DSE — Knowledge Base Ingestion Script
==============================================

Run this script to:
  1. Parse all PDFs (and .txt / .md files) in the knowledge_base/ directory.
  2. Chunk them into semantically meaningful pieces.
  3. Embed and store them in a local ChromaDB vector database.

Usage:
    # From the eduloop/ project root:
    python -m knowledge_base.ingest

    # Or directly:
    python knowledge_base/ingest.py

    # With custom paths:
    python knowledge_base/ingest.py --data-dir ./knowledge_base --db-dir ./data/vector_db

    # Reset the database before ingesting:
    python knowledge_base/ingest.py --reset
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure the project root is on the Python path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from knowledge_base.pdf_parser import DSEPDFParser
from knowledge_base.rag_retriever import DSERetriever


def main():
    parser = argparse.ArgumentParser(
        description="Ingest DSE Math documents into the ChromaDB vector database."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.path.join(PROJECT_ROOT, "knowledge_base"),
        help="Root directory containing dse_curriculum/ and sample_papers/ folders.",
    )
    parser.add_argument(
        "--db-dir",
        type=str,
        default=os.path.join(PROJECT_ROOT, "data", "vector_db"),
        help="Directory where ChromaDB will persist its data.",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="dse_math",
        help="ChromaDB collection name.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing collection before ingesting.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  EduLoop DSE — Knowledge Base Ingestion")
    print("=" * 60)
    print(f"  Data directory : {args.data_dir}")
    print(f"  DB directory   : {args.db_dir}")
    print(f"  Collection     : {args.collection}")
    print(f"  Reset first    : {args.reset}")
    print("=" * 60)

    # --- Step 1: Initialise Retriever (ChromaDB) ---
    print("\n🔧 Step 1 — Initialising ChromaDB retriever …")
    retriever = DSERetriever(
        persist_directory=args.db_dir,
        collection_name=args.collection,
    )

    if args.reset:
        print("🗑️  Resetting existing collection …")
        retriever.reset()

    # --- Step 2: Parse Documents ---
    print("\n📄 Step 2 — Parsing documents …\n")
    pdf_parser = DSEPDFParser()
    all_chunks = []

    # Parse curriculum folder
    curriculum_dir = os.path.join(args.data_dir, "dse_curriculum")
    if os.path.isdir(curriculum_dir):
        print(f"--- Scanning: {curriculum_dir} ---")
        curriculum_chunks = pdf_parser.parse_directory(curriculum_dir)
        all_chunks.extend(curriculum_chunks)
    else:
        print(f"⚠️  Curriculum directory not found: {curriculum_dir}")

    # Parse sample papers folder
    papers_dir = os.path.join(args.data_dir, "sample_papers")
    if os.path.isdir(papers_dir):
        print(f"\n--- Scanning: {papers_dir} ---")
        paper_chunks = pdf_parser.parse_directory(papers_dir)
        all_chunks.extend(paper_chunks)
    else:
        print(f"⚠️  Sample papers directory not found: {papers_dir}")

    # Parse any loose files at the root of knowledge_base/
    loose_files = [
        f
        for f in Path(args.data_dir).iterdir()
        if f.is_file() and f.suffix.lower() in (".pdf", ".txt", ".md")
        and f.name != "README.md"
    ]
    if loose_files:
        print(f"\n--- Scanning loose files in: {args.data_dir} ---")
        for f in loose_files:
            try:
                chunks = pdf_parser.parse_file(str(f))
                all_chunks.extend(chunks)
                print(f"📄 {f.name}: {len(chunks)} chunks")
            except Exception as e:
                print(f"❌ {f.name}: {e}")

    if not all_chunks:
        print("\n❌ No chunks were extracted. Make sure your files are in the right folders.")
        print("   Expected structure:")
        print("     knowledge_base/")
        print("       dse_curriculum/   ← curriculum PDFs, .md, .txt")
        print("       sample_papers/    ← past paper PDFs, marking schemes")
        sys.exit(1)

    # --- Step 3: Ingest into ChromaDB ---
    print(f"\n📥 Step 3 — Ingesting {len(all_chunks)} chunks into ChromaDB …\n")
    num_ingested = retriever.ingest(all_chunks)

    # --- Step 4: Print Summary ---
    print("\n" + "=" * 60)
    print("  📊 Ingestion Summary")
    print("=" * 60)

    stats = retriever.get_stats()
    print(f"  Total chunks in DB   : {stats['total_chunks']}")
    print(f"  Document types       : {stats['document_types']}")
    print(f"  Years covered        : {stats['years']}")
    print(f"  Source files          : {stats['sources']}")
    print(f"  Topic coverage       :")
    for topic, count in sorted(stats["topics_coverage"].items(), key=lambda x: -x[1]):
        print(f"    • {topic}: {count} chunks")

    # --- Step 5: Quick sanity test ---
    print("\n" + "=" * 60)
    print("  🧪 Quick Retrieval Test")
    print("=" * 60)

    test_queries = [
        "quadratic equations formula",
        "trigonometry sine cosine",
        "probability binomial distribution",
    ]
    for q in test_queries:
        results = retriever.retrieve(q, k=2)
        print(f"\n  Query: \"{q}\"")
        if results:
            for r in results:
                preview = r["text"][:120].replace("\n", " ")
                print(f"    → [{r['source']}] (score {r['score']}) {preview}…")
        else:
            print("    → No results found")

    print("\n✅ Ingestion pipeline complete! The RAG database is ready.")
    print(f"   DB location: {args.db_dir}")
    print(f"   Collection : {args.collection}")
    print(f"   Total docs  : {num_ingested}\n")


if __name__ == "__main__":
    main()
