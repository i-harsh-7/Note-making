from app.platform_registry import PlatformInfo
from app.audio.base_capture import AudioCapture


_BACKEND_MAP = {
    "wasapi":    "app.audio.wasapi_capture.WasapiCapture",
    "coreaudio": "app.audio.coreaudio_capture.CoreAudioCapture",
    "pipewire":  "app.audio.pipewire_capture.PipeWireCapture",
    "alsa":      "app.audio.pipewire_capture.PipeWireCapture",  # same impl, different device probe
}


class AudioFactory:
    @staticmethod
    def create(platform_info: PlatformInfo, event_bus) -> AudioCapture:
        backend = platform_info.audio_backend
        dotted = _BACKEND_MAP.get(backend)
        if not dotted:
            raise RuntimeError(f"Unknown audio backend: {backend}")

        module_path, class_name = dotted.rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(event_bus)
