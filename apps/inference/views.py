from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .models import InferenceHistory
from .serializers import (
    InferenceRunSerializer,
    InferenceHistorySerializer,
    InferenceHistoryListSerializer,
)
from .services import start_inference
from .utils.query import history_qs_for_user
from .utils.io import collect_paths, safe_delete_paths


class InferenceRunView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        multi = request.FILES.getlist("files")
        single = request.FILES.get("file")
        if multi:
            uploaded_files = multi
        elif single:
            uploaded_files = [single]
        else:
            raise ValidationError({"file": "请上传 file(单文件) 或 files(多文件)"})


        ser = InferenceRunSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        history_id = start_inference(
            user=request.user,
            uploaded_files=uploaded_files,
            params=ser.validated_data.get("params") or {},
            enqueue=True,
        )
        return Response({"history_id": history_id}, status=status.HTTP_201_CREATED)


class InferenceHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        obj = history_qs_for_user(user=request.user, pk=pk).first()
        if not obj:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(InferenceHistorySerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        obj = history_qs_for_user(user=request.user, pk=pk).first()
        if not obj:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)

        file_paths = collect_paths(obj.input_files, obj.output_files)

        obj.delete()
        safe_delete_paths(file_paths)

        return Response(status=status.HTTP_204_NO_CONTENT)


class InferenceHistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InferenceHistoryListSerializer

    def get_queryset(self):
        qs = InferenceHistory.objects.all().order_by("-created_at")
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs


class AdminInferenceHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """管理员：查看/删除全部推理历史"""
    permission_classes = [IsAdminUser]
    queryset = InferenceHistory.objects.all().order_by("-id")
    serializer_class = InferenceHistorySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return InferenceHistoryListSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        file_paths = collect_paths(instance.input_files, instance.output_files)
        self.perform_destroy(instance)
        safe_delete_paths(file_paths)
        return Response(status=status.HTTP_204_NO_CONTENT)
