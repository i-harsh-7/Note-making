# NoteAI — Local AI Video Note-Taking Companion

A floating, always-on-top desktop widget that transcribes audio, runs OCR on screen regions, cleans notes with a local LLM, and writes everything into a live Word document. Runs **100% locally** — no subscriptions, no cloud APIs.

---

## Features

- Floating frameless widget (draggable, adjustable opacity, always on top)
- Live audio transcription via `faster-whisper` (WASAPI loopback on Windows, BlackHole on macOS)
- OCR on any screen region (PaddleOCR on Windows, Apple Vision on macOS)
- LLM note cleanup and AI summaries via Ollama (Llama 3 / Phi-3)
- Live `.docx` document with append, insert-at-line, insert-at-page, reformat, and AI summary
- Timestamped screenshot capture with automatic tagging

---

## Requirements

| Requirement | Windows | macOS |
|---|---|---|
| Python | 3.10 or higher | 3.10 or higher |
| Ollama | Required | Required |
| LLM model | `llama3` (default) | `llama3` (default) |
| Audio loopback | Built-in (WASAPI) | BlackHole virtual device |
| OCR | PaddleOCR (auto-installed) | Apple Vision (built-in) |

---

## Setup on Windows

### Step 1 — Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/).

During installation, check **"Add Python to PATH"**.

Verify:
```cmd
python --version
```

### Step 2 — Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com).

After installation, open a terminal and pull the default model:
```cmd
ollama pull llama3
```

This downloads ~4.7 GB. Leave Ollama running in the background — it starts automatically on login.

### Step 3 — Clone or download the project

```cmd
cd %USERPROFILE%\Desktop
git clone <your-repo-url> NotemakingAI
cd NotemakingAI
```

Or simply place the project folder on your Desktop as `NotemakingAI`.

### Step 4 — Install dependencies

Double-click `install.bat`, or run in a terminal:
```cmd
cd %USERPROFILE%\Desktop\NotemakingAI
install.bat
```

This installs PyQt6, faster-whisper, soundcard, PaddleOCR, mss, python-docx, and all other dependencies.

### Step 5 — (Optional) Install Tesseract for OCR fallback

If PaddleOCR fails to install, install the Tesseract binary from:
[https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

Add the Tesseract install directory (e.g. `C:\Program Files\Tesseract-OCR`) to your system PATH.

### Step 6 — Run the app

```cmd
cd %USERPROFILE%\Desktop\NotemakingAI
python main.py
```

The floating widget will appear in the top-right corner of your screen.

---

## Setup on macOS

### Step 1 — Install Python

Install via Homebrew (recommended):
```bash
brew install python@3.11
```

Or download from [python.org](https://www.python.org/downloads/).

Verify:
```bash
python3 --version
```

### Step 2 — Install Ollama

```bash
brew install ollama
```

Or download from [ollama.com](https://ollama.com).

Start Ollama and pull the default model:
```bash
ollama serve &
ollama pull llama3
```

### Step 3 — Install BlackHole for audio loopback

NoteAI captures desktop audio (what your speakers are playing) using a virtual audio device.

Install BlackHole 2ch:
```bash
brew install blackhole-2ch
```

Then set up an Aggregate Device so you can hear audio AND capture it simultaneously:

1. Open **Audio MIDI Setup** (search in Spotlight).
2. Click **+** at the bottom left → **Create Aggregate Device**.
3. Check both your **built-in output** (e.g. MacBook Pro Speakers) and **BlackHole 2ch**.
4. Name it `NoteAI Loopback`.
5. Open **System Settings → Sound → Output** and select `NoteAI Loopback`.

NoteAI will auto-detect BlackHole as the loopback source.

### Step 4 — Clone or download the project

```bash
cd ~/Desktop
git clone <your-repo-url> NotemakingAI
cd NotemakingAI
```

### Step 5 — Install dependencies

```bash
chmod +x install.sh
./install.sh
```

This installs PyQt6, faster-whisper, soundcard, pyobjc-framework-Vision, mss, python-docx, and all other dependencies.

On Apple Silicon (M1/M2/M3/M4), `faster-whisper` automatically uses the AMX/Accelerate framework via CTranslate2 for fast CPU inference. No additional configuration needed.

### Step 6 — Run the app

```bash
cd ~/Desktop/NotemakingAI
python3 main.py
```

The floating widget will appear in the top-right corner of your screen.

> **macOS note:** On first run, macOS may ask for permissions for Screen Recording and Microphone access. Grant both in **System Settings → Privacy & Security**.

---

## Using the Widget

| Control | Action |
|---|---|
| **Start Recording** | Begins audio loopback capture. Transcript appears in real time. |
| **Stop Recording** | Stops capture and sends the full transcript to the document. |
| **From / To fields** | Enter `HH:MM:SS` timestamps to tag a manual extraction segment. |
| **Select Region** | Draw a box on screen to capture a screenshot. |
| **OCR Region** | Draw a box to capture + immediately extract text via OCR. |
| **Capture Frame** | Screenshot the entire screen with a timestamp tag. |
| **Clean Notes** | Send the current transcript to Ollama for LLM cleanup into bullet points. |
| **AI Summary** | Generate a 3–5 sentence summary and insert it at the top of the document. |
| **Reformat** | Normalize fonts, remove duplicate blank lines, tidy paragraph styles. |
| **Save Doc** | Save the `.docx` file (also auto-saves every 60 seconds). |
| **Insert at line** | Insert current notes content before a specific paragraph number. |
| **Opacity slider** | Adjust widget transparency (40%–100%). |
| Drag title bar | Move the widget anywhere on screen. |
| **✕ button** | Saves the document and exits cleanly. |

---

## Output Files

All output is saved in the `output/` directory inside the project folder:

```
NotemakingAI/
└── output/
    ├── notes_session_YYYYMMDD_HHMMSS.docx   ← live Word document
    └── captures/
        └── session_*_frame_*.png            ← timestamped screenshots
```

---

## Switching the LLM Model

To use a smaller/faster model, edit [main.py](main.py) line where `OllamaClient` is created:

```python
ollama_client = OllamaClient(bus, model="phi3")   # lighter, faster
```

Pull the model first:
```bash
ollama pull phi3
```

---

## Switching the Whisper Model

To improve transcription accuracy, edit [app/transcription/transcriber.py](app/transcription/transcriber.py):

```python
DEFAULT_MODEL = "small.en"   # better accuracy, ~2x slower than base.en
```

Available sizes: `tiny.en`, `base.en`, `small.en`, `medium.en`. Models download automatically on first use.

---

## Troubleshooting

**Widget does not appear on top of other windows**
- On macOS: grant Screen Recording permission in System Settings → Privacy & Security.
- On Windows: run the terminal as Administrator if UAC blocks the overlay.

**No audio is captured**
- Windows: ensure no other app has exclusive WASAPI access (disable exclusive mode in Sound settings).
- macOS: confirm your system output is set to the Aggregate Device containing BlackHole.
- Linux: check that PipeWire is running (`pactl info | grep Server`).

**Ollama errors / LLM not responding**
- Ensure Ollama is running: `ollama serve` (or it auto-starts on login after install).
- Confirm the model is pulled: `ollama list`.

**PaddleOCR install fails on Windows**
- Install the Tesseract fallback instead (see Step 5 in Windows setup).
- Or try: `pip install paddlepaddle==2.6.0 paddleocr==2.8.0 --index-url https://pypi.org/simple/`

**PyQt6 import error**
- Run: `pip install PyQt6 --force-reinstall`
