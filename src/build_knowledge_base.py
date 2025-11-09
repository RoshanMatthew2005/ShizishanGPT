"""Builds the agricultural knowledge base by ingesting PDFs and persisting a ChromaDB vector store."""
from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import chromadb
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

load_dotenv()

DATA_DIR = Path(os.getenv("PDF_DIRECTORY", "Data"))
VECTOR_STORE_DIR = Path(os.getenv("VECTOR_STORE_DIRECTORY", "models/vectorstore"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "agricultural_knowledge_base")
LOG_PATH = Path(os.getenv("BUILD_LOG_PATH", "knowledge_base_build.log"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))
RETRIEVAL_QUERY = os.getenv("TEST_QUERY", "What fertilizer should be used for maize?")


@dataclass
class DocumentSegment:
    content: str
    metadata: Dict[str, object]


def setup_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("knowledge_base_builder")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def print_section(title: str) -> None:
    border = "=" * 70
    print(f"\n{border}\n{title.upper()}\n{border}")


def ensure_directories(logger: logging.Logger) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("PDF directory: %s", DATA_DIR.resolve())
    logger.info("Vector store directory: %s", VECTOR_STORE_DIR.resolve())


def load_pdf_documents(logger: logging.Logger) -> Tuple[List[DocumentSegment], Dict[str, int]]:
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.error("No PDF files found in %s", DATA_DIR.resolve())
        raise FileNotFoundError(f"No PDF files found in {DATA_DIR.resolve()}")

    segments: List[DocumentSegment] = []
    stats = {"pdf_count": 0, "page_count": 0}

    for pdf_path in tqdm(pdf_files, desc="Loading PDFs", unit="pdf"):
        try:
            reader = PdfReader(str(pdf_path))
        except Exception as err:
            logger.exception("Failed to read %s: %s", pdf_path.name, err)
            continue

        stats["pdf_count"] += 1
        total_pages = len(reader.pages)

        for page_idx, page in enumerate(reader.pages, start=1):
            try:
                raw_text = page.extract_text() or ""
            except Exception as err:
                logger.warning("Failed to extract text from %s (page %s): %s", pdf_path.name, page_idx, err)
                continue

            stats["page_count"] += 1
            metadata = {
                "source": pdf_path.name,
                "page": page_idx,
                "total_pages": total_pages,
            }
            segments.append(DocumentSegment(content=raw_text, metadata=metadata))

    logger.info("Loaded %s PDFs (%s pages)", stats["pdf_count"], stats["page_count"])
    return segments, stats


def clean_text(text: str) -> str:
    cleaned = text.replace("\u00A0", " ")
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    cleaned = "\n".join(line for line in cleaned.splitlines() if line)
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def preprocess_segments(segments: List[DocumentSegment], logger: logging.Logger) -> List[DocumentSegment]:
    cleaned_segments: List[DocumentSegment] = []
    for segment in tqdm(segments, desc="Cleaning text", unit="page"):
        text = clean_text(segment.content)
        if len(text) < 50:
            continue
        cleaned_segments.append(DocumentSegment(content=text, metadata=segment.metadata))
    logger.info("Retained %s pages after preprocessing", len(cleaned_segments))
    return cleaned_segments


def chunk_segments(segments: Sequence[DocumentSegment], logger: logging.Logger) -> List[DocumentSegment]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: List[DocumentSegment] = []
    for segment in tqdm(segments, desc="Chunking documents", unit="page"):
        for chunk_idx, chunk_text in enumerate(splitter.split_text(segment.content)):
            if len(chunk_text) < 100:
                continue
            metadata = dict(segment.metadata)
            metadata.update({
                "chunk_index": chunk_idx,
                "chunk_char_count": len(chunk_text),
            })
            chunks.append(DocumentSegment(content=chunk_text, metadata=metadata))

    logger.info("Created %s chunks", len(chunks))
    return chunks


def embed_chunks(
    chunks: Sequence[DocumentSegment],
    logger: logging.Logger,
) -> Tuple[List[str], List[str], List[Dict[str, object]], List[List[float]], SentenceTransformer]:
    if not chunks:
        raise ValueError("No chunks available for embedding")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("Loaded embedding model: %s", EMBEDDING_MODEL_NAME)

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, object]] = []
    embeddings: List[List[float]] = []

    for batch_start in tqdm(range(0, len(chunks), EMBEDDING_BATCH_SIZE), desc="Generating embeddings", unit="batch"):
        batch = chunks[batch_start: batch_start + EMBEDDING_BATCH_SIZE]
        batch_texts = [chunk.content for chunk in batch]
        vectors = model.encode(batch_texts, batch_size=EMBEDDING_BATCH_SIZE, show_progress_bar=False, normalize_embeddings=True)

        for chunk, vector in zip(batch, vectors):
            source = str(chunk.metadata.get("source", "unknown"))
            page = int(chunk.metadata.get("page", 0))
            chunk_index = int(chunk.metadata.get("chunk_index", 0))
            chunk_id = f"{source}::p{page:03d}::c{chunk_index:03d}"
            ids.append(chunk_id)
            documents.append(chunk.content)
            metadatas.append(chunk.metadata)
            embeddings.append(vector.tolist())

    logger.info("Generated %s embeddings", len(embeddings))
    return ids, documents, metadatas, embeddings, model


def persist_collection(ids: Sequence[str], documents: Sequence[str], metadatas: Sequence[Dict[str, object]], embeddings: Sequence[Sequence[float]], logger: logging.Logger) -> Collection:
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    if collection.count() > 0:
        collection.delete(where={})
        logger.info("Cleared existing collection entries")

    collection.add(ids=list(ids), documents=list(documents), metadatas=list(metadatas), embeddings=list(embeddings))
    logger.info("Persisted %s vectors to collection '%s'", len(documents), COLLECTION_NAME)
    return collection


def test_retrieval(collection: Collection, model: SentenceTransformer, logger: logging.Logger, top_k: int = 3) -> List[Tuple[Dict[str, object], str, float]]:
    query_embedding = model.encode([RETRIEVAL_QUERY], normalize_embeddings=True)[0].tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    retrieved: List[Tuple[Dict[str, object], str, float]] = []
    for metadata, document, distance in zip(results.get("metadatas", [[]])[0], results.get("documents", [[]])[0], results.get("distances", [[]])[0]):
        score = 1 - distance if distance is not None else float("nan")
        retrieved.append((metadata, document, score))

    logger.info("Test query: %s", RETRIEVAL_QUERY)
    return retrieved


def summarize(stats: Dict[str, int], chunks: Sequence[DocumentSegment], build_time: float) -> None:
    total_chars = sum(len(chunk.content) for chunk in chunks)
    avg_chunk_length = int(total_chars / len(chunks)) if chunks else 0

    print_section("Final Summary")
    print(f"PDFs processed        : {stats.get('pdf_count', 0)}")
    print(f"Pages processed       : {stats.get('page_count', 0)}")
    print(f"Total chunks created  : {len(chunks)}")
    print(f"Average chunk length  : {avg_chunk_length} characters")
    print(f"Vector store path     : {VECTOR_STORE_DIR.resolve()}")
    print(f"Collection name       : {COLLECTION_NAME}")
    print(f"Embedding model       : {EMBEDDING_MODEL_NAME}")
    print(f"Total build time      : {build_time:.2f} seconds")


def main() -> None:
    start_time = time.time()
    logger = setup_logging(LOG_PATH)

    print_section("Step 1: Environment Setup")
    ensure_directories(logger)

    print_section("Step 2: Loading and Parsing PDFs")
    segments, stats = load_pdf_documents(logger)

    print_section("Step 3: Text Preprocessing")
    cleaned_segments = preprocess_segments(segments, logger)

    print_section("Step 4: Document Chunking")
    chunks = chunk_segments(cleaned_segments, logger)
    if not chunks:
        logger.error("No chunks were created; aborting build")
        raise ValueError("Chunking produced no data")

    print_section("Step 5: Generating Embeddings")
    ids, documents, metadatas, embeddings, model = embed_chunks(chunks, logger)

    print_section("Step 6: Persisting Vector Store")
    collection = persist_collection(ids, documents, metadatas, embeddings, logger)

    print_section("Step 7: Testing Retrieval System")
    retrievals = test_retrieval(collection, model, logger)
    for rank, (metadata, document, score) in enumerate(retrievals, start=1):
        source = metadata.get("source", "unknown")
        page = metadata.get("page", "?")
        print(f"Result {rank}")
        print(f"  Source : {source}")
        print(f"  Page   : {page}")
        print(f"  Score  : {score:.4f}")
        preview = document.replace("\n", " ")[:200]
        print(f"  Preview: {preview}...")

    build_time = time.time() - start_time
    summarize(stats, chunks, build_time)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Build interrupted by user")
        sys.exit(130)
    except Exception as exc:
        print("Build failed:", exc)
        sys.exit(1)
