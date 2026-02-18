from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from app.schemas.models import Citation


class RAGRetriever:
    def __init__(self, chroma_db_path: str = "./vector_store"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=chroma_db_path,
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(settings)
        self.collection = self.client.get_or_create_collection(
            name="ng12_guidelines",
            metadata={"hnsw:space": "cosine"}
        )

    def retrieve(self, query: str, top_k: int = 5) -> Tuple[List[str], List[Citation]]:
        """
        Retrieve relevant chunks from vector store.
        Returns: (texts, citations)
        """
        # Generate embedding for query
        query_embedding = self.model.encode(query, convert_to_list=True)

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        texts = []
        citations = []

        if results['documents'] and len(results['documents']) > 0:
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )
            ):
                # Distance is 1 - cosine similarity in ChromaDB
                similarity = 1 - distance

                texts.append(doc)

                citation = Citation(
                    source="NG12 PDF",
                    page=metadata.get("page", 0),
                    chunk_id=metadata.get("chunk_id", "unknown"),
                    excerpt=doc[:200] + "..." if len(doc) > 200 else doc
                )
                citations.append(citation)

        return texts, citations

    def retrieve_with_query_expansion(
        self, query: str, top_k: int = 5
    ) -> Tuple[List[str], List[Citation]]:
        """
        Retrieve with simple query expansion.
        This can be enhanced later.
        """
        # For now, just use basic retrieval
        return self.retrieve(query, top_k)
