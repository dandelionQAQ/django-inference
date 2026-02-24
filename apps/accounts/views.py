from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    MeSerializer,
    AdminSerializer,
    RegisterSerializer,
    CaptchaTokenObtainPairSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


class MeView(generics.RetrieveUpdateAPIView):
    """获取/修改“当前登录用户”的资料"""
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "密码已更新"}, status=status.HTTP_200_OK)


class AdminViewSet(viewsets.ModelViewSet):
    """管理员管理用户"""
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-id")
    serializer_class = AdminSerializer


class RegisterView(generics.CreateAPIView):
    """注册"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class CaptchaTokenObtainPairView(TokenObtainPairView):
    """登录获取 JWT"""
    serializer_class = CaptchaTokenObtainPairSerializer
