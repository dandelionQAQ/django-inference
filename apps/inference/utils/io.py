# apps/inference/utils/io.py
import json
import os
from typing import Any, Iterable, List, Optional

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers


# =========================
# JSON / params helpers
# =========================
def parse_jsonish(value: Any, *, field_name: str = "params", default: Optional[Any] = None):
    """
    兼容 multipart/form-data 下 JSON 字段的多种形态：
    - None / "" -> default
    - str -> json.loads
    - dict/list -> 原样返回
    其它类型 -> ValidationError
    """
    if default is None:
        default = {}

    if value is None or value == "":
        return default

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise serializers.ValidationError({field_name: f"{field_name} must be valid JSON"})

    if isinstance(value, (dict, list)):
        return value

    raise serializers.ValidationError({field_name: f"{field_name} must be a JSON string or object"})


# =========================
# Storage path helpers
# =========================
def collect_paths(*paths_lists: Iterable[Any]) -> List[str]:
    """把多个列表里的字符串路径收集成扁平 list（过滤 None/空/非 str）。"""
    out: List[str] = []
    for lst in paths_lists:
        for p in (lst or []):
            if isinstance(p, str) and p:
                out.append(p)
    return out


def safe_delete_paths(paths: Iterable[str]) -> None:
    """尽力删除一组 storage 路径，失败忽略（避免影响主流程）。"""
    for p in paths or []:
        try:
            default_storage.delete(p)
        except Exception:
            pass


# =========================
# Save files / outputs
# =========================
def save_input_file(*, history_id: int, uploaded_file, index: int = 1) -> str:
    """
    保存到：media/inference/history/<id>/input_file_1.<ext>
    返回相对路径（存到 input_files）
    """
    ext = os.path.splitext(getattr(uploaded_file, "name", ""))[1].lower() or ""
    rel_path = f"inference/history/{history_id}/input_file_{index}{ext}"
    return default_storage.save(rel_path, uploaded_file)


def save_input_files(*, history_id: int, uploaded_files) -> List[str]:
    paths = []
    for i, f in enumerate(uploaded_files, start=1):
        paths.append(save_input_file(history_id=history_id, uploaded_file=f, index=i))
    return paths


def save_output_json(*, history_id: int, data: dict, index: int = 1) -> str:
    """
    保存到：media/inference/history/<id>/output_file_1.json
    返回相对路径（存到 output_files）
    """
    rel_path = f"inference/history/{history_id}/output_file_{index}.json"
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    return default_storage.save(rel_path, ContentFile(content))
