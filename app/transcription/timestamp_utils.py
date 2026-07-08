from datetime import datetime, timedelta


def seconds_to_hms(seconds: float) -> str:
    """Convert float seconds to HH:MM:SS.mmm string."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def hms_to_seconds(hms: str) -> float:
    """Parse HH:MM:SS.mmm or HH:MM:SS or MM:SS string to float seconds."""
    hms = hms.strip()
    parts = hms.split(":")
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = "0", parts[0], parts[1]
    else:
        return float(hms)
    return int(h) * 3600 + int(m) * 60 + float(s)


def format_frame_tag(timestamp_sec: float, frame_number: int | None = None) -> str:
    """Return a bracketed timestamp tag for embedding in notes."""
    base = f"[{seconds_to_hms(timestamp_sec)}]"
    if frame_number is not None:
        return f"[{seconds_to_hms(timestamp_sec)} | f#{frame_number}]"
    return base


def video_session_id() -> str:
    return datetime.now().strftime("session_%Y%m%d_%H%M%S")
