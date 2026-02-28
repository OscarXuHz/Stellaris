"""
RAG Retriever for EduLoop DSE.

Provides a clean interface for storing document chunks in ChromaDB
and retrieving the most relevant ones for a given query.  This is the
object the Teaching Agent and Assessment Agent call at runtime.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class DSERetriever:
    """
    Vector-database backed retriever for DSE Mathematics content.

    Uses ChromaDB as the local vector store.  Supports:
      - Ingesting pre-chunked documents (from DSEPDFParser)
      - Semantic similarity retrieval
      - Metadata filtering (by syllabus, topic, document type, year, etc.)
    """

    DEFAULT_COLLECTION = "dse_math"

    def __init__(
        self,
        persist_directory: str = "./data/vector_db",
        collection_name: str = DEFAULT_COLLECTION,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialise the retriever.

        Args:
            persist_directory: Where ChromaDB stores its data on disk.
            collection_name:   Name of the ChromaDB collection.
            embedding_model:   SentenceTransformer model used to create embeddings.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model

        # Lazy imports – only fail if the user actually calls the retriever
        self._chroma_client = None
        self._collection = None
        self._embedding_fn = None

    # ------------------------------------------------------------------
    # Lazy initialisation
    # ------------------------------------------------------------------

    def _ensure_initialised(self):
        """Create ChromaDB client and collection on first use."""
        if self._collection is not None:
            return

        import chromadb
        from chromadb.utils import embedding_functions

        os.makedirs(self.persist_directory, exist_ok=True)

        self._chroma_client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        # Use SentenceTransformer for embeddings (runs locally, no API key)
        self._embedding_fn = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )
        )

        self._collection = self._chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

        print(
            f"✅ ChromaDB collection '{self.collection_name}' ready "
            f"({self._collection.count()} documents)"
        )

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """
        Add parsed document chunks into the vector store.

        Args:
            chunks: List of chunk dicts produced by DSEPDFParser.
                    Each must have 'id', 'text', and 'metadata'.
            batch_size: Number of chunks to upsert per batch.

        Returns:
            Number of chunks ingested.
        """
        self._ensure_initialised()

        if not chunks:
            print("⚠️  No chunks to ingest.")
            return 0

        total = len(chunks)
        ingested = 0

        for start in range(0, total, batch_size):
            batch = chunks[start : start + batch_size]

            ids = [c["id"] for c in batch]
            documents = [c["text"] for c in batch]

            # ChromaDB metadata values must be str, int, float, or bool.
            metadatas = [self._sanitise_metadata(c["metadata"]) for c in batch]

            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            ingested += len(batch)
            print(f"   📥 Ingested {ingested}/{total} chunks …")

        print(f"✅ Ingestion complete — {ingested} chunks in collection.")
        return ingested

    # ------------------------------------------------------------------
    # Retrieval  (this is the method the agents call)
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the k most relevant chunks for a query.

        This method signature is deliberately compatible with the existing
        `TeachingAgent.rag_vectordb.retrieve(topic, k=5)` interface.

        Args:
            query:          Natural language query or topic name.
            k:              Number of results to return.
            where:          Optional metadata filter dict for ChromaDB.
                            Example: {"document_type": "curriculum"}
            where_document: Optional full-text filter dict for ChromaDB.

        Returns:
            List of dicts, each containing:
              - text (str): the chunk content
              - source (str): source filename
              - score (float): distance / relevance score
              - metadata (dict): all stored metadata
        """
        self._ensure_initialised()

        query_params: Dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(k, self._collection.count() or k),
        }
        if where:
            query_params["where"] = where
        if where_document:
            query_params["where_document"] = where_document

        # Guard against empty collection
        if self._collection.count() == 0:
            print("⚠️  Collection is empty — run ingestion first.")
            return []

        results = self._collection.query(**query_params)

        # Unpack ChromaDB's nested list format
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        output: List[Dict[str, Any]] = []
        for doc, meta, dist, doc_id in zip(documents, metadatas, distances, ids):
            output.append(
                {
                    "id": doc_id,
                    "text": doc,
                    "source": meta.get("source_file", "unknown"),
                    "score": round(1 - dist, 4),  # cosine distance → similarity
                    "metadata": meta,
                }
            )

        return output

    # ------------------------------------------------------------------
    # Filtered convenience methods
    # ------------------------------------------------------------------

    def retrieve_curriculum(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve only from curriculum / syllabus documents."""
        return self.retrieve(query, k=k, where={"document_type": "curriculum"})

    def retrieve_past_paper(
        self, query: str, year: Optional[str] = None, k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve from past papers, optionally filtered by year."""
        where: Dict[str, Any] = {"document_type": "paper"}
        if year:
            where = {"$and": [{"document_type": "paper"}, {"year": year}]}
        return self.retrieve(query, k=k, where=where)

    def retrieve_marking_scheme(
        self, query: str, year: Optional[str] = None, k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve from marking schemes, optionally filtered by year."""
        where: Dict[str, Any] = {"document_type": "marking_scheme"}
        if year:
            where = {"$and": [{"document_type": "marking_scheme"}, {"year": year}]}
        return self.retrieve(query, k=k, where=where)

    # ------------------------------------------------------------------
    # Admin / inspection helpers
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the number of documents in the collection."""
        self._ensure_initialised()
        return self._collection.count()

    def list_sources(self) -> List[str]:
        """Return a deduplicated list of source filenames in the DB."""
        self._ensure_initialised()
        all_meta = self._collection.get(include=["metadatas"])
        sources = {m.get("source_file", "unknown") for m in all_meta["metadatas"]}
        return sorted(sources)

    def reset(self):
        """⚠️  Delete the entire collection and start fresh."""
        self._ensure_initialised()
        self._chroma_client.delete_collection(self.collection_name)
        self._collection = None
        print(f"🗑️  Collection '{self.collection_name}' deleted.")
        # Recreate empty collection
        self._ensure_initialised()

    def get_stats(self) -> Dict[str, Any]:
        """Return summary statistics about the current collection."""
        self._ensure_initialised()
        all_data = self._collection.get(include=["metadatas"])
        metas = all_data["metadatas"]

        doc_types: Dict[str, int] = {}
        years: Dict[str, int] = {}
        topics_seen: Dict[str, int] = {}

        for m in metas:
            dt = m.get("document_type", "unknown")
            doc_types[dt] = doc_types.get(dt, 0) + 1

            yr = m.get("year")
            if yr:
                years[yr] = years.get(yr, 0) + 1

            for t in (m.get("detected_topics") or "").split(", "):
                if t:
                    topics_seen[t] = topics_seen.get(t, 0) + 1

        return {
            "total_chunks": len(metas),
            "document_types": doc_types,
            "years": years,
            "topics_coverage": topics_seen,
            "sources": self.list_sources(),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitise_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        ChromaDB only accepts str/int/float/bool metadata values.
        Convert lists to comma-separated strings and drop None values.
        """
        clean: Dict[str, Any] = {}
        for key, value in meta.items():
            if value is None:
                continue
            if isinstance(value, list):
                clean[key] = ", ".join(str(v) for v in value)
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            else:
                clean[key] = str(value)
        return clean
