# QMS Copilot (GenAI + RAG)

Quality Management System assistant: apne SOP, NCR, CAPA aur audit documents se sawaal poochho,
NCR/CAPA ka draft banwao, aur root cause analysis (5-Why / Fishbone) karwao.

## Mac par chalane ke steps (100% free, local model)

1. Python 3.10+ chahiye. Check: `python3 --version`
2. **Ollama install karo** (ye local AI model chalata hai): https://ollama.com/download
   Download karke Applications me daalo aur ek baar kholo. Ya terminal me: `brew install ollama`
3. Terminal me is folder me jao:
   `cd ~/Downloads/qms-rag`
4. Setup (ek baar, libraries + model download):
   `chmod +x setup.sh run.sh`
   `./setup.sh`
5. App chalao:
   `./run.sh`
   Browser me http://localhost:8501 khulega.

Koi API key ya paisa nahi chahiye.

## Model kaunsa? (RAM ke hisaab se)

`.env` file me `OLLAMA_MODEL=` badlo, phir `ollama pull <naam>` chalao.

| Mac RAM | Model | Size |
|---|---|---|
| 8 GB | `llama3.2:3b` (default) | ~2 GB |
| 16 GB | `qwen2.5:7b` ya `llama3.1:8b` | ~5 GB |
| 32 GB+ | `qwen2.5:14b` | ~9 GB |

Bada model = behtar jawab, par slow. Small model me Hinglish jawab thode kamzor ho sakte hain,
aur sources wala hissa hamesha dekhna.

## Troubleshooting

- "Ollama chal nahi raha": Ollama app kholo ya terminal me `ollama serve`.
- "Model download nahi hua": `ollama pull llama3.2:3b`
- Jawab bahut slow: chhota model lo.

## Folder structure

```
data/          <- tumhare documents (.txt, .md, .pdf). Yahan aur daalo.
src/config.py  <- settings (chunk size, model, top-k)
src/ingest.py  <- Step 2-3: load -> chunk -> embed -> Chroma DB
src/rag.py     <- Step 4-6: retrieve, answer, NCR draft, root cause
app.py         <- Step 7: Streamlit UI
tests/         <- Step 8: retrieval evaluation
```

## Pipeline

```
Documents -> Chunks -> Embeddings -> Chroma (vector DB)
Question -> Embedding -> top-k similar chunks -> Claude -> Answer + sources
```

## Try these questions

- Weld me crack mile to kya karna hai?
- Batch B-4471 me porosity ka root cause kya tha?
- Torque wrench ka calibration kitne time me hota hai?
- Supplier audit me kya findings aaye?
- Line 2 me is hafte porosity kyun badhi?

NCR tab me try karo: "Line 3 par 12 brackets me crack mila, batch B-5120, final inspection me."

## Retrieval test (API key ke bina)

```
source venv/bin/activate
python -m src.ingest
python -m tests.eval_retrieval
```

## Apne documents add karna

`data/` me file daalo (ya app ke sidebar se upload karo), phir "Re-index documents" dabao.

## Aage ke modules

Ye Smart Factory Copilot ka Module 1 hai. Agle: equipment RUL prediction aur digital twin.
