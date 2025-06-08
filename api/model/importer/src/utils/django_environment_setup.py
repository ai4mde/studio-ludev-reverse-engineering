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
        sys.exit("No Django settings.py file found in the extracted directory. Verify the integrity of your Django project or try to import another file/folder")

    if os.stat(settings_files[0]).st_size == 0:
        # Use sys exit instead of raise ... to facilitate the script being run as subproccess 
        # and being able to do error handling this way
        sys.exit("Django settings.py is empty. Verify the integrity of your Django project or try to import another file/folder")

    # Get the project root directory
    project_root = settings_files[0].parent

    project_name = project_root.name

    # Add the project path to sys.path
    sys.path.append(project_root.parent.as_posix())
    # Set the Django environment
    os.environ['DJANGO_SETTINGS_MODULE'] = f"{project_name}.settings"

    # Remove duplicate 'admin' from INSTALLED_APPS dynamically
    if settings.INSTALLED_APPS and 'admin' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

    try:
        django.setup()
    except Exception as e:
        sys.exit(f"Error setting up Django environment: {str(e)}")
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
    except Exception as e:
        sys.exit(f"Error setting up mock Django environment: {str(e)}")
        raise
