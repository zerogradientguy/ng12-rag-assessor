import os
import re
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class PDFIngester:
    def __init__(self, chroma_db_path: str = "./vector_store"):
        self.chroma_db_path = chroma_db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize Chroma client with persistence
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

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks by word count."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text and structure from PDF."""
        pages_data = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue

                # Split by paragraphs (double newlines)
                paragraphs = re.split(r'\n\n+', text)

                page_data = {
                    'page': page_num + 1,
                    'paragraphs': [p.strip() for p in paragraphs if p.strip()]
                }
                pages_data.append(page_data)

        return pages_data

    def ingest_pdf(self, pdf_path: str):
        """Ingest PDF into ChromaDB with embeddings."""
        print(f"Extracting text from {pdf_path}...")
        pages_data = self.extract_text_from_pdf(pdf_path)

        chunk_id_counter = 0
        all_docs = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []

        for page_data in pages_data:
            page_num = page_data['page']
            chunk_idx = 0

            for paragraph in page_data['paragraphs']:
                # Create chunks from paragraphs
                chunks = self.chunk_text(paragraph, chunk_size=500, overlap=50)

                for chunk in chunks:
                    chunk_id = f"ng12_{page_num:04d}_{chunk_idx:02d}"

                    all_docs.append(chunk)
                    all_metadatas.append({
                        "page": page_num,
                        "chunk_id": chunk_id,
                        "section": "NG12 Cancer Guidelines",
                    })
                    all_ids.append(chunk_id)
                    chunk_idx += 1

        # Generate embeddings in batches
        print(f"Generating embeddings for {len(all_docs)} chunks...")
        batch_size = 32
        for i in range(0, len(all_docs), batch_size):
            batch_docs = all_docs[i:i+batch_size]
            batch_embeddings = self.model.encode(batch_docs, convert_to_list=True)
            batch_metadatas = all_metadatas[i:i+batch_size]
            batch_ids = all_ids[i:i+batch_size]

            # Add to collection
            self.collection.upsert(
                documents=batch_docs,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f"Added batch {i//batch_size + 1}...")

        print(f"Successfully ingested PDF. Total chunks: {len(all_docs)}")


def ingest_ng12_pdf(pdf_path: str, chroma_db_path: str = "./vector_store"):
    """Main function to ingest NG12 PDF."""
    ingester = PDFIngester(chroma_db_path)
    ingester.ingest_pdf(pdf_path)
    print("PDF ingestion complete!")
