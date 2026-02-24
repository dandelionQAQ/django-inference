from django.db import transaction

from .models import InferenceHistory
from .utils.history import update_history
from .utils.io import save_input_files


def enqueue_inference(history_id: int) -> None:
    from .tasks import inference_task
    inference_task.delay(history_id)


@transaction.atomic
def start_inference(*, user, uploaded_files, params: dict, enqueue: bool = True) -> int:
    history = InferenceHistory.objects.create(
        user=user,
        request_params=params or {},
        input_files=[],
        output_files=[],
        output_data={},
        status="queued",
        progress=0,
        message="queued",
    )

    update_history(history, progress=1, message="creating record")

    input_path = save_input_files(history_id=history.id, uploaded_files=uploaded_files)
    history.input_files = input_path
    history.save(update_fields=["input_files"])

    update_history(history, progress=5, message="input saved")

    if enqueue:
        history_id = history.id
        transaction.on_commit(lambda hid=history_id: enqueue_inference(hid))

    return history.id
