# coding: utf-8
# 為了 Django Syncdb 等指令

import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queue_inline.settings")
    sys.path.append(os.path.join(os.path.dirname(__file__), "venv\\Lib\\site-packages"))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
