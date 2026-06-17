# run once: read pdfs, split into chunks, embed them, and save the vector index to disk.
import glob
import os

from pypdf import PdfReader

from src.config import config
from providers.embeddings import get_embedder
from vectorstore import Chunk, FaissVectorStore


# split one page's text into overlapping chunks
def chunk_text(text, size, overlap):
    text = " ".join(text.split())   # collapse whitespace/newlines
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap       # step back by overlap so chunks share a bit
    return chunks


# read every pdf and turn it into chunks tagged with file + page
def load_chunks(pdf_dir, size, overlap):
    chunks = []
    paths = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    if not paths:
        raise SystemExit(f"no pdfs found in {pdf_dir}. drop some in and rerun.")
    for path in paths:
        name = os.path.basename(path)
        reader = PdfReader(path)
        for page_no, page in enumerate(reader.pages, start=1):
            for piece in chunk_text(page.extract_text() or "", size, overlap):
                chunks.append(Chunk(text=piece, source=name, page=page_no))
        print(f"  {name}: {len(reader.pages)} pages")
    return chunks


def main():
    print(f"reading pdfs from {config.pdf_dir} ...")
    chunks = load_chunks(config.pdf_dir, config.chunk_size, config.chunk_overlap)
    print(f"built {len(chunks)} chunks. embedding with '{config.embedding_provider}' ...")

    embedder = get_embedder(config)
    vectors = embedder.embed([c.text for c in chunks])

    store = FaissVectorStore()
    store.add(vectors, chunks)
    store.save(config.index_dir)
    print(f"saved index to {config.index_dir}. ready to chat.")


if __name__ == "__main__":
    main()