"""Step 4-6: retrieval + Claude se answer, NCR/CAPA draft, root cause analysis."""
import os

import requests

from src import config
from src.ingest import get_collection, get_model


def retrieve(query: str, k: int = config.TOP_K):
    """Question se milte-julte chunks dhundta hai."""
    collection = get_collection()
    if collection.count() == 0:
        return []
    emb = get_model().encode([query], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=emb, n_results=min(k, collection.count()))
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": doc, "source": meta["source"], "score": round(1 - dist, 3)})
    return hits


def _context(hits):
    return "\n\n".join(f"[Source: {h['source']}]\n{h['text']}" for h in hits)


def _call_ollama(system: str, user: str, max_tokens: int) -> str:
    try:
        r = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json={
                "model": config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 4096, "num_predict": max_tokens},
            },
            timeout=600,
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Ollama chal nahi raha. Ollama app kholo (ya terminal me: ollama serve).")
    if r.status_code == 404:
        raise RuntimeError(
            f"Model '{config.OLLAMA_MODEL}' download nahi hua. Terminal me chalao: "
            f"ollama pull {config.OLLAMA_MODEL}"
        )
    r.raise_for_status()
    return r.json()["message"]["content"]


def _call_claude(system: str, user: str, max_tokens: int) -> str:
    import anthropic  # sirf tab chahiye jab LLM_BACKEND=claude ho

    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(".env me ANTHROPIC_API_KEY daalo.")
    resp = anthropic.Anthropic(api_key=key).messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def _call(system: str, user: str, max_tokens: int = 1200) -> str:
    if config.LLM_BACKEND == "claude":
        return _call_claude(system, user, max_tokens)
    return _call_ollama(system, user, max_tokens)


QA_SYSTEM = (
    "You are a Quality Management System assistant for a manufacturing company. "
    "Answer ONLY using the provided context documents. "
    "Cite the source file name in square brackets after each claim, e.g. [sop_welding.txt]. "
    "If the context does not contain the answer, say clearly that the documents do not cover it. "
    "Keep answers short and practical. Reply in the same language style the user writes in "
    "(Hinglish if the user writes Hinglish)."
)


def ask(question: str, k: int = config.TOP_K):
    hits = retrieve(question, k)
    if not hits:
        return "Koi document index nahi hai. Pehle documents index karo.", []
    prompt = f"Context:\n{_context(hits)}\n\nQuestion: {question}"
    return _call(QA_SYSTEM, prompt), hits


NCR_SYSTEM = (
    "You are a quality engineer. Draft a formal Non-Conformance Report (NCR) followed by a "
    "proposed CAPA (Corrective and Preventive Action) plan, based on the incident description. "
    "Use the past NCR/CAPA/SOP context for format, terminology and relevant procedures. "
    "Do not invent facts that are not in the description; mark unknown fields as 'TBD'. "
    "Sections: NCR (ID placeholder, date, product, issue, detection point, immediate action, "
    "suspected cause) then CAPA (root cause, corrective action, preventive action, owner, "
    "due date, effectiveness check)."
)


def draft_ncr(description: str):
    hits = retrieve(description, k=5)
    prompt = f"Past documents:\n{_context(hits)}\n\nNew incident:\n{description}"
    return _call(NCR_SYSTEM, prompt, max_tokens=1500), hits


RCA_SYSTEM = (
    "You are a quality engineer doing root cause analysis. Using the problem statement and "
    "the historical documents as context, produce the analysis in the requested method. "
    "Clearly separate what is supported by the documents from what is only a hypothesis to verify. "
    "End with 3 concrete verification checks."
)


def root_cause(problem: str, method: str = "5-Why"):
    hits = retrieve(problem, k=5)
    prompt = (
        f"Method: {method}\n\nHistorical documents:\n{_context(hits)}\n\n"
        f"Problem:\n{problem}"
    )
    return _call(RCA_SYSTEM, prompt, max_tokens=1500), hits
