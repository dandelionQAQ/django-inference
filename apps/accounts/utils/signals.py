from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .io import safe_delete_file

User = get_user_model()

@receiver(pre_save, sender=User)
def delete_old_avatar_when_changed(sender, instance, **kwargs):
    """换头像时清理旧头像文件"""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_avatar = old.avatar
    new_avatar = instance.avatar

    # 头像字段变更（换新文件 or 清空）才删旧文件
    if old_avatar and old_avatar.name != (new_avatar.name if new_avatar else ""):
        safe_delete_file(old_avatar)

@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """删除用户时删头像文件"""
    safe_delete_file(instance.avatar)
