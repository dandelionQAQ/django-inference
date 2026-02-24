from rest_framework import serializers
from .models import InferenceHistory
from .utils.io import parse_jsonish


class InferenceRunSerializer(serializers.Serializer):
    """推理任务的请求体解析"""
    params = serializers.JSONField(required=False, default=dict)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        ret["params"] = parse_jsonish(data.get("params", None), field_name="params", default={})
        return ret


class InferenceHistorySerializer(serializers.ModelSerializer):
    """返回任务历史记录"""
    user_id = serializers.IntegerField(source="user_id", read_only=True)

    class Meta:
        model = InferenceHistory
        fields = (
            "id",
            "status",
            "progress",
            "message",
            "request_params",
            "input_files",
            "output_files",
            "output_data",
            "created_at",
            "user_id",
        )
        read_only_fields = fields


class InferenceHistoryListSerializer(serializers.ModelSerializer):
    """返回任务历史记录列表"""
    user_id = serializers.IntegerField(source="user_id", read_only=True)

    class Meta:
        model = InferenceHistory
        fields = (
            "id",
            "status",
            "progress",
            "message",
            "created_at",
            "user_id",
        )
        read_only_fields = fields
