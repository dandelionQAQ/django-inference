import os
import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import InferenceHistory
from .utils.history import update_history


def infer_video_or_image(*, input_abs_path: str, params: dict, out_dir_rel: str, index: int) -> dict:
    """
    ✅ infer 自己决定输出文件有哪些、路径叫什么（runner 不再“定死” out_rel）
    返回：
      {
        "out_files": ["...相对路径...", "...相对路径..."],
        "result": {...小结果...}
      }
    """
    result = {
        "ok": True,
        "input": os.path.basename(input_abs_path),
        "params": params or {},
    }

    # 这里先示例：只输出 1 个 json（你以后想输出多个文件，就在 out_files 里加更多路径）
    out_files: list[str] = []

    json_rel = f"{out_dir_rel}/result_{index}.json"
    content = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
    default_storage.save(json_rel, ContentFile(content))
    out_files.append(json_rel)

    return {"out_files": out_files, "result": result}


def run_inference_impl(*, history_id: int) -> None:
    history = InferenceHistory.objects.get(id=history_id)

    if history.status in ("succeeded", "failed"):
        return

    try:
        update_history(history, status="running", progress=10, message="preparing")

        input_files = history.input_files or []
        if not input_files:
            raise ValueError("input_files is empty")

        out_dir_rel = f"inference/history/{history.id}"

        out_files: list[str] = []
        results: list[dict] = []

        n = len(input_files)

        for i, input_rel in enumerate(input_files, start=1):
            input_abs = os.path.join(settings.MEDIA_ROOT, input_rel)

            progress = 10 + int(70 * i / n)
            update_history(history, progress=progress, message=f"inferencing {i}/{n}")

            ret = infer_video_or_image(
                input_abs_path=input_abs,
                params=history.request_params,
                out_dir_rel=out_dir_rel,
                index=i,
            )

            one_out_files = ret.get("out_files") or []
            one_result = ret.get("result") or {}

            # ✅ 不再 append “固定 out_rel”，而是收集 infer 返回的所有输出路径
            out_files.extend([p for p in one_out_files if isinstance(p, str) and p])

            results.append(
                {
                    "index": i,
                    "input_file": input_rel,
                    "out_files": one_out_files,
                    "result": one_result,
                }
            )

        update_history(history, progress=90, message="writing output")

        history.output_files = out_files
        history.output_data = {"count": n, "items": results}
        history.save(update_fields=["output_files", "output_data"])

        update_history(history, status="succeeded", progress=100, message="done")

    except Exception as e:
        history.output_data = {"error": f"{e.__class__.__name__}: {e}"}
        history.save(update_fields=["output_data"])
        update_history(history, status="failed", message=f"failed: {e.__class__.__name__}")
        raise
