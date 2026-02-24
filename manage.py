import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django。请确认已安装 Django，且它在当前环境（虚拟环境）中可用。"
            "也请检查 PYTHONPATH / 虚拟环境是否已正确激活。"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
