import json
import sys
import os
import django
from django.apps import apps
from django.conf import settings

sys.path.append('../test_prototype/generated_prototypes/c79c758a-d2c5-4e2c-bf71-eadcaf769299/shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

# Remove duplicate 'admin' from INSTALLED_APPS dynamically
if 'admin' in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

# Now setup Django with the modified INSTALLED_APPS
django.setup()

def load_models_and_fields_to_json():
    """
    Load and output all models and their fields from 'shared_models' in project_b as JSON.
    """
    models_data = {}

    # Loop through all installed apps
    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':  # Only process 'Shared_Models' app
            print(f"Extracting models from: {app_config.verbose_name}")

            # Get all models in the app
            models = app_config.get_models()

            # Loop through models and capture their fields
            for model in models:
                model_data = {
                    "model_name": model.__name__,
                    "fields": []
                }

                print(f"  - {model.__name__}")
                # Get all fields of the model
                fields = model._meta.get_fields()

                for field in fields:
                    field_data = {
                        "field_name": field.name,
                        "field_type": field.get_internal_type()
                    }

                    print(f"  - {field.name}")
                    print(field.get_internal_type())

                    # If the field is a related model (ForeignKey, ManyToManyField), add related model info
                    if hasattr(field, 'related_model') and field.related_model:
                        field_data["related_model"] = field.related_model.__name__

                    model_data["fields"].append(field_data)

                models_data[model.__name__] = model_data

    # Return models data as JSON
    return json.dumps(models_data, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    print(load_models_and_fields_to_json())
