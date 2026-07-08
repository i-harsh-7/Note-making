import queue
from PyQt6.QtCore import QThread

from app.event_bus import EventBus

CLEAN_NOTES_PROMPT = """\
You are a precise note-taking assistant. Given the raw transcript below, produce clean, \
structured bullet-point notes. Remove filler words (uh, um, like), fix grammar, preserve \
all technical terms and proper nouns exactly. Use markdown bullets (•).

Transcript:
{transcript}

Clean Notes:"""

SUMMARY_PROMPT = """\
Summarize the following transcript in 3-5 sentences. Focus on the key concepts, decisions, \
and action items. Be concise and professional.

Transcript:
{transcript}

Summary:"""


class OllamaClient(QThread):
    """Background worker for all Ollama LLM calls.

    Runs a persistent event loop consuming tasks off a queue so the UI never blocks.
    """

    def __init__(self, event_bus: EventBus, model: str = "llama3"):
        super().__init__()
        self._bus = event_bus
        self.model = model
        self._queue: queue.Queue = queue.Queue()

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def request_clean_notes(self, transcript: str) -> None:
        self._queue.put(("clean", transcript))

    def request_summary(self, transcript: str) -> None:
        self._queue.put(("summarize", transcript))

    # -----------------------------------------------------------------
    # QThread worker
    # -----------------------------------------------------------------

    def run(self) -> None:
        while True:
            task = self._queue.get()
            if task is None:
                break
            action, transcript = task
            if action == "clean":
                self._clean(transcript)
            elif action == "summarize":
                self._summarize(transcript)

    def _clean(self, transcript: str) -> None:
        result = self._call_ollama(CLEAN_NOTES_PROMPT.format(transcript=transcript))
        if result:
            self._bus.notes_updated.emit(result)

    def _summarize(self, transcript: str) -> None:
        result = self._call_ollama(SUMMARY_PROMPT.format(transcript=transcript))
        if result:
            self._bus.summary_ready.emit(result)

    def _call_ollama(self, prompt: str) -> str | None:
        try:
            import ollama
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response["message"]["content"].strip()
        except Exception as exc:
            self._bus.error_occurred.emit("llm", f"Ollama error: {exc}")
            return None
