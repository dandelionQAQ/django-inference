from typing import Optional
from ..models import InferenceHistory


def update_history(
    history: InferenceHistory,
    *,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    message: Optional[str] = None,
):
    if status is not None:
        history.status = status
    if progress is not None:
        history.progress = max(0, min(100, int(progress)))
    if message is not None:
        history.message = message

    history.save(update_fields=["status", "progress", "message"])
