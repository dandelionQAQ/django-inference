from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MeView,
    PasswordChangeView,
    AdminViewSet,
    RegisterView,
    CaptchaTokenObtainPairView,
)

router = DefaultRouter()
router.register(r"admin/users", AdminViewSet, basename="admin-users")

urlpatterns = [
    path("captcha/", include("captcha.urls")),
    path("token/", CaptchaTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("me/", MeView.as_view(), name="me"),
    path("me/password/", PasswordChangeView.as_view(), name="password_change"),
    path("register/", RegisterView.as_view(), name="register"),
    path("", include(router.urls)),
]
