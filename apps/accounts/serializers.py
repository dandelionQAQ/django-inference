from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils.captcha import validate_and_consume_captcha


class PasswordChangeSerializer(serializers.Serializer):
    """修改密码"""
    old_password = serializers.CharField(write_only=True, required=True, allow_blank=False)
    new_password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class MeSerializer(serializers.ModelSerializer):
    """修改个人资料"""
    avatar = serializers.ImageField(required=False, allow_null=True, )
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'bio', 'email', 'is_staff', 'is_active')
        read_only_fields = ('id', 'is_staff', 'is_active')


class AdminSerializer(serializers.ModelSerializer):
    """管理员修改用户资料"""
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'avatar', 'bio', 'email', 'is_staff', 'is_active')
        read_only_fields = ('id',)

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        if not password:
            raise serializers.ValidationError({"password": "创建用户必须提供密码"})

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """注册"""
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    captcha_hashkey = serializers.CharField(write_only=True, required=True)
    captcha_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'captcha_hashkey', 'captcha_code')
        read_only_fields = ('id',)

    def create(self, validated_data):
        hashkey = validated_data.pop("captcha_hashkey")
        code = validated_data.pop("captcha_code")
        password = validated_data.pop("password")

        validate_and_consume_captcha(hashkey=hashkey, code=code)

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CaptchaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """登录"""
    captcha_hashkey = serializers.CharField(write_only=True, required=True)
    captcha_code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        hashkey = attrs.pop("captcha_hashkey")
        code = attrs.pop("captcha_code")

        validate_and_consume_captcha(hashkey=hashkey, code=code)

        return super().validate(attrs)
