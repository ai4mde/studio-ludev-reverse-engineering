import os
import sys
import django
from django.conf import settings
from pathlib import Path

def configure_django_settings(extract_path):
    # Find the settings.py file
    settings_files = list(Path(extract_path).glob('**/settings.py'))
    if not settings_files:
        # Use sys exit instead of raise ... to facilitate the script being run as subproccess
        # and being able to do error handling this way
        sys.exit("No Django settings.py file found in the extracted directory")

    # Get the project root directory
    project_root = settings_files[0].parent

    project_name = project_root.name

    # Absolute path to the *parent* folder of `shop`
    project_root = '/home/luoluo/PycharmProjects/2025-10-Reverse-Engineering-ludev/test_prototype/generated_prototypes/eb846e17-a261-470a-abeb-09cd29980a46/shop'

    # Django setup
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

    # Remove 'admin' app from INSTALLED_APPS before setup
    if 'admin' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

    try:
        django.setup()
    except Exception as e:
        print("Error setting up Django environment:", str(e))
        raise


def configure_mock_django_settings():
    # Only configure if not already done
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='mock-secret-key',
            INSTALLED_APPS=[
                # Add mock apps or real Django apps you need for your test
                'django.contrib.contenttypes',
                'django.contrib.auth',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',  # In-memory DB for tests
                }
            },
            DEFAULT_AUTO_FIELD='django.db.models.AutoField',
        )

    try:
        django.setup()
        print("Mock Django environment configured.")
    except Exception as e:
        print("Error setting up mock Django environment:", str(e))
        raise
