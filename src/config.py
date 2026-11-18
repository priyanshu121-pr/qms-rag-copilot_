import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION = "qms_docs"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500      # ek chunk me kitne characters
CHUNK_OVERLAP = 80    # chunks ke beech overlap, taaki baat beech me kat na jaye
TOP_K = 4             # kitne chunks retrieve karne hain

# LLM backend: "ollama" (free, local, default) ya "claude" (paid API)
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
