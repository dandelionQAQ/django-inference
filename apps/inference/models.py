from django.conf import settings
from django.db import models


class InferenceHistory(models.Model):
    request_params = models.JSONField(default=dict, blank=True)  # 请求参数
    input_files = models.JSONField(default=list, blank=True)  # 输入文件列表
    output_files = models.JSONField(default=list, blank=True)  # 输出文件列表
    output_data = models.JSONField(default=dict, blank=True)  # 输出结果

    status = models.CharField(max_length=20, default="pending")  # 任务状态
    progress = models.PositiveSmallIntegerField(default=0)  # 进度
    message = models.CharField(max_length=200, blank=True, default="")  # 提示信息

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inference_histories",
    )  # 创建用户

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inference_history"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"InferenceHistory(id={self.pk}, status={self.status}, progress={self.progress})"
