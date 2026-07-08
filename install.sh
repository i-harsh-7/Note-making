#!/usr/bin/env bash
set -e

OS=$(uname -s)
echo "[NoteAI] Installing dependencies for $OS..."

python3 -m pip install --upgrade pip

if [ "$OS" = "Darwin" ]; then
    pip3 install -r requirements-macos.txt
    echo ""
    echo "[NoteAI] macOS: For loopback audio, install BlackHole:"
    echo "  brew install blackhole-2ch"
    echo "  Then set up an Aggregate Device in Audio MIDI Setup."
elif [ "$OS" = "Linux" ]; then
    pip3 install -r requirements-linux.txt
    echo ""
    echo "[NoteAI] Linux: For loopback audio, PipeWire monitor sources are used automatically."
    echo "  sudo apt install tesseract-ocr  # optional fallback OCR"
fi

echo ""
echo "[NoteAI] Also ensure Ollama is installed and running:"
echo "  https://ollama.com"
echo "  ollama pull llama3"
echo ""
echo "Run the app with: python3 main.py"
