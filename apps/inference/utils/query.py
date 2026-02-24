from ..models import InferenceHistory


def history_qs_for_user(*, user, pk: int):
    qs = InferenceHistory.objects.filter(id=pk)
    if not user.is_staff:
        qs = qs.filter(user=user)
    return qs
