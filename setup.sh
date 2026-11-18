#!/bin/bash
# Ek baar chalao: virtual environment + libraries + local model
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env

MODEL=$(grep -E '^OLLAMA_MODEL=' .env | cut -d= -f2)
MODEL=${MODEL:-llama3.2:3b}

if ! command -v ollama >/dev/null 2>&1; then
  echo ""
  echo "Ollama install nahi hai. Pehle install karo:"
  echo "  https://ollama.com/download  (Mac app download karke Applications me daalo)"
  echo "  ya: brew install ollama"
  echo "Phir dobara ./setup.sh chalao."
  exit 1
fi

# Ollama server chalu karo agar band hai
if ! curl -s http://localhost:11434 >/dev/null 2>&1; then
  (ollama serve >/dev/null 2>&1 &)
  sleep 4
fi

echo "Model download ho raha hai: $MODEL (pehli baar kuch GB, time lagega)"
ollama pull "$MODEL"

echo ""
echo "Setup ho gaya. Ab ./run.sh chalao."
