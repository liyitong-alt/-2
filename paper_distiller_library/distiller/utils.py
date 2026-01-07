import re
from datetime import datetime


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def simplify_title(filename: str) -> str:
    base = re.sub(r"\.[Pp][Dd][Ff]$", "", filename)
    base = re.sub(r"[_\-]+", " ", base)
    return base.strip()[:80] or "Untitled"
