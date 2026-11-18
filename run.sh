#!/bin/bash
source venv/bin/activate
# Ollama server chalu na ho to start kar do
if command -v ollama >/dev/null 2>&1 && ! curl -s http://localhost:11434 >/dev/null 2>&1; then
  (ollama serve >/dev/null 2>&1 &)
  sleep 4
fi
streamlit run app.py
