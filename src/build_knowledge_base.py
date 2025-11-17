"""Builds the agricultural knowledge base by ingesting PDFs and persisting a ChromaDB vector store."""  # Module docstring describing purpose
from __future__ import annotations  # forward-compatible annotations

import logging  # standard logging module
import os  # os utilities for environment and paths
import sys  # system utilities (exit)
import time  # timing operations
from dataclasses import dataclass  # dataclass decorator for simple classes
from pathlib import Path  # Path for filesystem paths
from typing import Dict, List, Sequence, Tuple  # type hints

import chromadb  # chroma vector DB client
from chromadb.api.models.Collection import Collection  # Collection typing
from dotenv import load_dotenv  # load environment variables from .env
from langchain.text_splitter import RecursiveCharacterTextSplitter  # text splitter helper
from PyPDF2 import PdfReader  # PDF reader
from sentence_transformers import SentenceTransformer  # embedding model
from tqdm import tqdm  # progress bars

load_dotenv()  # load environment variables from .env into os.environ

# Configuration variables with sensible defaults from environment
DATA_DIR = Path(os.getenv("PDF_DIRECTORY", "Data"))  # where PDF files live
VECTOR_STORE_DIR = Path(os.getenv("VECTOR_STORE_DIRECTORY", "models/vectorstore"))  # where to persist ChromaDB
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "agricultural_knowledge_base")  # chroma collection name
LOG_PATH = Path(os.getenv("BUILD_LOG_PATH", "knowledge_base_build.log"))  # path for build logs
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))  # target characters per chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))  # overlap between chunks
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")  # embedding model name
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))  # batch size for embeddings
RETRIEVAL_QUERY = os.getenv("TEST_QUERY", "What fertilizer should be used for maize?")  # test query for smoke test


@dataclass
class DocumentSegment:  # simple container for text and metadata
    content: str  # the text content for a page or chunk
    metadata: Dict[str, object]  # metadata such as source filename and page


def setup_logging(log_path: Path) -> logging.Logger:  # configure and return logger
    log_path.parent.mkdir(parents=True, exist_ok=True)  # ensure log directory exists
    logger = logging.getLogger("knowledge_base_builder")  # get named logger
    logger.setLevel(logging.INFO)  # set info level
    logger.handlers.clear()  # remove existing handlers to avoid duplicates
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # log format
    file_handler = logging.FileHandler(log_path, encoding="utf-8")  # file handler for logs
    file_handler.setFormatter(formatter)  # set formatter on file handler
    stream_handler = logging.StreamHandler(sys.stdout)  # stream handler to stdout
    stream_handler.setFormatter(formatter)  # set formatter on stream handler
    logger.addHandler(file_handler)  # attach file handler
    logger.addHandler(stream_handler)  # attach stream handler
    return logger  # return logger instance


def print_section(title: str) -> None:  # print a nicely formatted section header
    border = "=" * 70  # visual border
    print(f"\n{border}\n{title.upper()}\n{border}")  # print header with border


def ensure_directories(logger: logging.Logger) -> None:  # create data/vector dirs if missing
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # ensure data dir exists
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)  # ensure vector store dir exists
    logger.info("PDF directory: %s", DATA_DIR.resolve())  # log data dir path
    logger.info("Vector store directory: %s", VECTOR_STORE_DIR.resolve())  # log vector store path


def load_pdf_documents(logger: logging.Logger) -> Tuple[List[DocumentSegment], Dict[str, int]]:  # load PDFs and return segments + stats
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))  # list all pdf files in DATA_DIR
    if not pdf_files:  # if none found
        logger.error("No PDF files found in %s", DATA_DIR.resolve())  # log error
        raise FileNotFoundError(f"No PDF files found in {DATA_DIR.resolve()}")  # raise explicit error

    segments: List[DocumentSegment] = []  # collect page-level segments
    stats = {"pdf_count": 0, "page_count": 0}  # simple processing stats

    for pdf_path in tqdm(pdf_files, desc="Loading PDFs", unit="pdf"):  # iterate with progress
        try:
            reader = PdfReader(str(pdf_path))  # open pdf
        except Exception as err:
            logger.exception("Failed to read %s: %s", pdf_path.name, err)  # log exception and continue
            continue

        stats["pdf_count"] += 1  # increment pdf counter
        total_pages = len(reader.pages)  # number of pages in current pdf

        for page_idx, page in enumerate(reader.pages, start=1):  # iterate pages 1..N
            try:
                raw_text = page.extract_text() or ""  # extract text safely
            except Exception as err:
                logger.warning("Failed to extract text from %s (page %s): %s", pdf_path.name, page_idx, err)  # warn and skip
                continue

            stats["page_count"] += 1  # increment page counter
            metadata = {
                "source": pdf_path.name,  # filename
                "page": page_idx,  # page number
                "total_pages": total_pages,  # total pages in file
            }
            segments.append(DocumentSegment(content=raw_text, metadata=metadata))  # append segment for this page

    logger.info("Loaded %s PDFs (%s pages)", stats["pdf_count"], stats["page_count"])  # log load summary
    return segments, stats  # return collected segments and stats


def clean_text(text: str) -> str:  # normalize and clean extracted text
    cleaned = text.replace("\u00A0", " ")  # replace non-breaking spaces
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())  # strip each line
    cleaned = "\n".join(line for line in cleaned.splitlines() if line)  # remove empty lines
    cleaned = " ".join(cleaned.split())  # collapse whitespace into single spaces
    return cleaned.strip()  # final strip and return


def preprocess_segments(segments: List[DocumentSegment], logger: logging.Logger) -> List[DocumentSegment]:  # filter and clean page segments
    cleaned_segments: List[DocumentSegment] = []  # will hold cleaned pages
    for segment in tqdm(segments, desc="Cleaning text", unit="page"):  # iterate with progress
        text = clean_text(segment.content)  # clean page text
        if len(text) < 50:  # skip very short pages
            continue
        cleaned_segments.append(DocumentSegment(content=text, metadata=segment.metadata))  # keep cleaned page
    logger.info("Retained %s pages after preprocessing", len(cleaned_segments))  # log retention count
    return cleaned_segments  # return cleaned list


def chunk_segments(segments: Sequence[DocumentSegment], logger: logging.Logger) -> List[DocumentSegment]:  # split pages into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,  # target chunk size
        chunk_overlap=CHUNK_OVERLAP,  # overlap between chunks
        separators=["\n\n", "\n", ". ", " ", ""],  # splitting priorities
    )

    chunks: List[DocumentSegment] = []  # container for resulting chunks
    for segment in tqdm(segments, desc="Chunking documents", unit="page"):  # iterate pages
        for chunk_idx, chunk_text in enumerate(splitter.split_text(segment.content)):  # split into chunk texts
            if len(chunk_text) < 100:  # skip tiny chunks
                continue
            metadata = dict(segment.metadata)  # copy metadata from page
            metadata.update({
                "chunk_index": chunk_idx,  # index of chunk within page
                "chunk_char_count": len(chunk_text),  # character count of chunk
            })
            chunks.append(DocumentSegment(content=chunk_text, metadata=metadata))  # append chunk

    logger.info("Created %s chunks", len(chunks))  # log number of chunks created
    return chunks  # return chunks


def embed_chunks(
    chunks: Sequence[DocumentSegment],
    logger: logging.Logger,
) -> Tuple[List[str], List[str], List[Dict[str, object]], List[List[float]], SentenceTransformer]:  # embed text chunks
    if not chunks:  # ensure there is content to embed
        raise ValueError("No chunks available for embedding")  # raise helpful error

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)  # load embedding model
    logger.info("Loaded embedding model: %s", EMBEDDING_MODEL_NAME)  # log model used

    ids: List[str] = []  # ids for chroma
    documents: List[str] = []  # raw chunk texts
    metadatas: List[Dict[str, object]] = []  # metadata per chunk
    embeddings: List[List[float]] = []  # numeric embeddings

    for batch_start in tqdm(range(0, len(chunks), EMBEDDING_BATCH_SIZE), desc="Generating embeddings", unit="batch"):  # generate in batches
        batch = chunks[batch_start: batch_start + EMBEDDING_BATCH_SIZE]  # select batch
        batch_texts = [chunk.content for chunk in batch]  # texts for model
        vectors = model.encode(batch_texts, batch_size=EMBEDDING_BATCH_SIZE, show_progress_bar=False, normalize_embeddings=True)  # encode

        for chunk, vector in zip(batch, vectors):  # attach ids/metadatas
            source = str(chunk.metadata.get("source", "unknown"))  # filename source
            page = int(chunk.metadata.get("page", 0))  # page number
            chunk_index = int(chunk.metadata.get("chunk_index", 0))  # chunk index
            chunk_id = f"{source}::p{page:03d}::c{chunk_index:03d}"  # deterministic id
            ids.append(chunk_id)  # push id
            documents.append(chunk.content)  # push document text
            metadatas.append(chunk.metadata)  # push metadata
            embeddings.append(vector.tolist())  # push embedding vector

    logger.info("Generated %s embeddings", len(embeddings))  # log number of embeddings generated
    return ids, documents, metadatas, embeddings, model  # return all pieces + model for testing


def persist_collection(ids: Sequence[str], documents: Sequence[str], metadatas: Sequence[Dict[str, object]], embeddings: Sequence[Sequence[float]], logger: logging.Logger) -> Collection:  # save data to chroma
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))  # persistent chroma client
    collection = client.get_or_create_collection(name=COLLECTION_NAME)  # get or create collection
    if collection.count() > 0:  # if existing entries present
        collection.delete(where={})  # clear them to ensure fresh build
        logger.info("Cleared existing collection entries")  # log clearing

    collection.add(ids=list(ids), documents=list(documents), metadatas=list(metadatas), embeddings=list(embeddings))  # add data to chroma
    logger.info("Persisted %s vectors to collection '%s'", len(documents), COLLECTION_NAME)  # log persistence
    return collection  # return the collection object


def test_retrieval(collection: Collection, model: SentenceTransformer, logger: logging.Logger, top_k: int = 3) -> List[Tuple[Dict[str, object], str, float]]:  # smoke-test retrieval
    query_embedding = model.encode([RETRIEVAL_QUERY], normalize_embeddings=True)[0].tolist()  # embed test query
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)  # query chroma

    retrieved: List[Tuple[Dict[str, object], str, float]] = []  # prepare results list
    for metadata, document, distance in zip(results.get("metadatas", [[]])[0], results.get("documents", [[]])[0], results.get("distances", [[]])[0]):  # zip returned lists
        score = 1 - distance if distance is not None else float("nan")  # convert distance to similarity-like score
        retrieved.append((metadata, document, score))  # append triple

    logger.info("Test query: %s", RETRIEVAL_QUERY)  # log the test query used
    return retrieved  # return retrieved items


def summarize(stats: Dict[str, int], chunks: Sequence[DocumentSegment], build_time: float) -> None:  # print final summary to console
    total_chars = sum(len(chunk.content) for chunk in chunks)  # sum characters across chunks
    avg_chunk_length = int(total_chars / len(chunks)) if chunks else 0  # compute average chunk length

    print_section("Final Summary")  # print header
    print(f"PDFs processed        : {stats.get('pdf_count', 0)}")  # number of pdfs
    print(f"Pages processed       : {stats.get('page_count', 0)}")  # number of pages
    print(f"Total chunks created  : {len(chunks)}")  # chunks count
    print(f"Average chunk length  : {avg_chunk_length} characters")  # avg length
    print(f"Vector store path     : {VECTOR_STORE_DIR.resolve()}")  # vector store location
    print(f"Collection name       : {COLLECTION_NAME}")  # collection name
    print(f"Embedding model       : {EMBEDDING_MODEL_NAME}")  # model used
    print(f"Total build time      : {build_time:.2f} seconds")  # build duration


def main() -> None:  # main orchestration function
    start_time = time.time()  # record start time
    logger = setup_logging(LOG_PATH)  # initialize logger

    print_section("Step 1: Environment Setup")  # step header
    ensure_directories(logger)  # ensure directories exist

    print_section("Step 2: Loading and Parsing PDFs")  # next step header
    segments, stats = load_pdf_documents(logger)  # load pdf pages

    print_section("Step 3: Text Preprocessing")  # preprocessing header
    cleaned_segments = preprocess_segments(segments, logger)  # clean and filter pages

    print_section("Step 4: Document Chunking")  # chunking header
    chunks = chunk_segments(cleaned_segments, logger)  # split pages into chunks
    if not chunks:  # validate there are chunks
        logger.error("No chunks were created; aborting build")  # log error
        raise ValueError("Chunking produced no data")  # raise error to stop

    print_section("Step 5: Generating Embeddings")  # embedding header
    ids, documents, metadatas, embeddings, model = embed_chunks(chunks, logger)  # generate embeddings

    print_section("Step 6: Persisting Vector Store")  # persistence header
    collection = persist_collection(ids, documents, metadatas, embeddings, logger)  # save to chroma

    print_section("Step 7: Testing Retrieval System")  # retrieval test header
    retrievals = test_retrieval(collection, model, logger)  # run smoke query
    for rank, (metadata, document, score) in enumerate(retrievals, start=1):  # display results
        source = metadata.get("source", "unknown")  # get source file
        page = metadata.get("page", "?")  # get page number
        print(f"Result {rank}")  # print rank
        print(f"  Source : {source}")  # print source
        print(f"  Page   : {page}")  # print page
        print(f"  Score  : {score:.4f}")  # print similarity score
        preview = document.replace("\n", " ")[:200]  # short preview
        print(f"  Preview: {preview}...")  # print preview

    build_time = time.time() - start_time  # compute elapsed time
    summarize(stats, chunks, build_time)  # print final summary


if __name__ == "__main__":  # entrypoint
    try:
        main()  # run main
    except KeyboardInterrupt:
        print("Build interrupted by user")  # handle user interrupt
        sys.exit(130)  # exit code 130 for interrupt
    except Exception as exc:
        print("Build failed:", exc)  # print failure
        sys.exit(1)  # general failure exit
