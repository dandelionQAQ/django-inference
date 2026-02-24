from rest_framework import serializers
from captcha.models import CaptchaStore


def validate_and_consume_captcha(*, hashkey: str, code: str) -> None:
    """校验验证码"""
    ok = CaptchaStore.objects.filter(hashkey=hashkey, response=code).exists()
    if not ok:
        raise serializers.ValidationError({"captcha": "验证码错误或已过期"})

    # 验证码一次性使用
    CaptchaStore.objects.filter(hashkey=hashkey).delete()
