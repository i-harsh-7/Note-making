@echo off
echo [NoteAI] Installing dependencies for Windows...
python -m pip install --upgrade pip
pip install -r requirements-windows.txt
echo.
echo [NoteAI] Done. Also ensure:
echo   1. Ollama is installed and running: https://ollama.com
echo      ollama pull llama3
echo   2. (Optional) Tesseract OCR binary for fallback:
echo      https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo Run the app with: python main.py
pause
