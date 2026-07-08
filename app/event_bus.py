from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """Central signal hub. All workers emit here; all UI connects here."""

    # Audio pipeline
    audio_chunk_ready = pyqtSignal(bytes, float)       # pcm_bytes, timestamp_sec
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    # Transcription
    transcript_chunk = pyqtSignal(str, float)           # text, start_time_sec
    transcript_final = pyqtSignal(str)                  # full session transcript

    # LLM
    notes_updated = pyqtSignal(str)                     # cleaned note text
    summary_ready = pyqtSignal(str)                     # AI summary text

    # OCR / Screen capture
    ocr_result_ready = pyqtSignal(str, str)             # text, source_image_path
    region_selected = pyqtSignal(int, int, int, int)    # x, y, w, h
    capture_taken = pyqtSignal(str, float)              # image_path, timestamp_sec

    # Document
    doc_saved = pyqtSignal(str)                         # saved file path
    doc_action_requested = pyqtSignal(str, object)      # action_name, payload

    # General
    error_occurred = pyqtSignal(str, str)               # module_name, message
    status_changed = pyqtSignal(str)                    # status bar text


# Singleton instance created once in main.py and passed by reference
