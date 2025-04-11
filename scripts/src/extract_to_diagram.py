import uuid
import os
import sys
import django
from django.apps import apps
from django.conf import settings
import inspect  # To inspect methods of the class

sys.path.append('../test_prototype/generated_prototypes/c79c758a-d2c5-4e2c-bf71-eadcaf769299/shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

# Remove duplicate 'admin' from INSTALLED_APPS dynamically
if 'admin' in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

# Now setup Django with the modified INSTALLED_APPS
django.setup()

def generate_diagram_json():
    diagrams = []

    # Define the base diagram structure
    diagram_data = {
        "id": str(uuid.uuid4()),  # Unique ID for the diagram
        "name": "Diagram",
        "type": "classes",
        "edges": [],
        "nodes": [],
        "system": "c79c758a-d2c5-4e2c-bf71-eadcaf769299",  # System ID
        "project": "99fc3c09-07bc-43d2-bf59-429f99a35839",  # Project ID
        "description": ""
    }

    # Loop through all installed apps and process 'Shared_Models'
    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':  # Only process 'Shared_Models'
            print(f"Extracting models from: {app_config.verbose_name}")

            # Get all models in the 'Shared_Models' app
            models = app_config.get_models()

            # Process each model
            for model in models:
                # Create a node for each model
                model_node = {
                    "id": str(uuid.uuid4()),  # Unique ID for the node
                    "cls": {
                        "leaf": False,
                        "name": model.__name__,
                        "type": "class",
                        "methods": [],
                        "abstract": False,
                        "namespace": "",
                        "attributes": []
                    },
                    "data": {
                        "position": {"x": 0, "y": 0}  # Placeholder position
                    },
                    "cls_ptr": str(uuid.uuid4())  # Pointer ID for the class
                }

                # Extract methods using inspect
                for name, func in inspect.getmembers(model, predicate=inspect.isfunction):
                    model_node["cls"]["methods"].append({
                        "body": "",
                        "name": name,
                        "type": "function",  # Adjust type if needed
                        "description": ""
                    })

                # Extract attributes (fields)
                for field in model._meta.get_fields():
                    model_node["cls"]["attributes"].append({
                        "body": None,
                        "enum": None,
                        "name": field.name,
                        "type": field.get_internal_type().lower(),
                        "derived": False,
                        "description": None
                    })

                # Add the node to the diagram
                diagram_data["nodes"].append(model_node)

    diagrams.append(diagram_data)

    return {"diagrams": diagrams}

if __name__ == "__main__":
    print(generate_diagram_json())
