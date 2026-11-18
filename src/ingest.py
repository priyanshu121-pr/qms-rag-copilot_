"""Step 2-3: documents load -> chunks -> embeddings -> Chroma vector DB."""
from pathlib import Path

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from src import config

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBED_MODEL)
    return _model


def get_collection():
    client = chromadb.PersistentClient(path=str(config.DB_DIR))
    return client.get_or_create_collection(
        name=config.COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def load_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, size: int, overlap: int):
    """Text ko chhote tukdon me todta hai, jahan tak ho newline par."""
    text = text.strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            newline = text.rfind("\n", start + size // 2, end)
            if newline != -1:
                end = newline
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest(reset: bool = True) -> int:
    """data/ folder ke saare documents index karta hai. Chunks ki ginti return karta hai."""
    if reset:
        client = chromadb.PersistentClient(path=str(config.DB_DIR))
        try:
            client.delete_collection(config.COLLECTION)
        except Exception:
            pass
    collection = get_collection()
    model = get_model()

    ids, texts, metas = [], [], []
    files = sorted(
        p for p in config.DATA_DIR.iterdir()
        if p.suffix.lower() in {".txt", ".md", ".pdf"}
    )
    for path in files:
        text = load_document(path)
        if not text.strip():
            continue
        title = text.strip().splitlines()[0][:120]
        for i, chunk in enumerate(chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
            # title har chunk ke saath, taaki context na khoye
            body = chunk if chunk.startswith(title) else f"[{title}]\n{chunk}"
            ids.append(f"{path.name}-{i}")
            texts.append(body)
            metas.append({"source": path.name, "title": title, "chunk": i})

    if not texts:
        return 0
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metas)
    return len(texts)


def count_chunks() -> int:
    return get_collection().count()


if __name__ == "__main__":
    n = ingest()
    print(f"Done: {n} chunks index hue.")
