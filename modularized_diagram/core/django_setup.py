import os
import sys
from django.conf import settings
import django

def setup_django(project_path: str, settings_module: str):
    sys.path.append(project_path)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    if 'admin' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

    django.setup()
