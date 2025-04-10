import inspect
import uuid
import os
import sys
import django
import pathlib
from django.conf import settings
from jinja2 import Template
from django.apps import apps
from django.http import JsonResponse
from django.db import models

# Jinja2 template for generating the diagram JSON structure
json_template = """
{
    "diagrams": [
        {
            "id": "{{ diagram_id }}",
            "name": "Diagram",
            "type": "classes",
            "edges": [
                {% for edge in edges %}
                {
                    "id": "{{ edge.id }}",
                    "rel": {
                        "type": "{{ edge.rel.type }}",
                        "label": "{{ edge.rel.label }}",
                        "multiplicity": {
                            "source": "{{ edge.rel.multiplicity.source }}",
                            "target": "{{ edge.rel.multiplicity.target }}"
                        }
                    },
                    "data": {},
                    "rel_ptr": "{{ edge.rel_ptr }}",
                    "source_ptr": "{{ edge.source_ptr }}",
                    "target_ptr": "{{ edge.target_ptr }}"
                }
                {% if not loop.last %},{% endif %}
                {% endfor %}
            ],
            "nodes": [
                {% for node in nodes %}
                {
                    "id": "{{ node.id }}",
                    "cls": {
                        "leaf": false,
                        "name": "{{ node.cls.name }}",
                        "type": "class",
                        "methods": [
                            {% for method in node.cls.methods %}
                            {
                                "body": "",
                                "name": "{{ method.name }}",
                                "type": "{{ method.type }}",
                                "description": ""
                            }
                            {% if not loop.last %},{% endif %}
                            {% endfor %}
                        ],
                        "abstract": false,
                        "namespace": "",
                        "attributes": [
                            {% for attribute in node.cls.attributes %}
                            {
                                "body": null,
                                "enum": null,
                                "name": "{{ attribute.name }}",
                                "type": "{{ attribute.type }}",
                                "derived": false,
                                "description": null
                            }
                            {% if not loop.last %},{% endif %}
                            {% endfor %}
                        ]
                    },
                    "data": {
                        "position": {
                            "x": {{ node.data.position.x }},
                            "y": {{ node.data.position.y }}
                        }
                    },
                    "cls_ptr": "{{ node.cls_ptr }}"
                }
                {% if not loop.last %},{% endif %}
                {% endfor %}
            ],
            "system": "{{ system_id }}",
            "project": "{{ project_id }}",
            "description": ""
        }
    ]
}
"""

DJANGO_GENERATED_METHODS = set([
    'check',
    'clean',
    'clean_fields',
    'delete',
    'full_clean',
    'save',
    'save_base',
    'validate_unique'
])

def get_custom_methods(model):
    custom_methods = []
    standard_methods = set(dir(models.Model))
    for m in dir(model):
        if m.startswith('_') or m in standard_methods:
            continue
        if m in DJANGO_GENERATED_METHODS:
            continue
        if is_method_without_args(getattr(model, m, None)):
            custom_methods.append(m)
    return custom_methods

def is_method_without_args(func):
    """Check if func is a method callable with only one param (self)"""
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return False
    sig = inspect.signature(func)
    params = sig.parameters

    # Check if there is exactly one parameter and that has the name 'self'
    return len(params) == 1 and 'self' in params


def generate_diagram_json():
    diagrams = []
    edges = []
    nodes = []

    # Define diagram IDs, system, project IDs (hardcoded for now)
    diagram_id = str(uuid.uuid4())
    system_id = "c79c758a-d2c5-4e2c-bf71-eadcaf769299"
    project_id = "99fc3c09-07bc-43d2-bf59-429f99a35839"

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
                for name in get_custom_methods(model):
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
                nodes.append(model_node)

                # Check relationships (e.g., ForeignKeys, ManyToMany)
                for field in model._meta.get_fields():
                    if field.is_relation:
                        # For ForeignKey or OneToMany or ManyToMany
                        if field.many_to_one:
                            edge = {
                                "id": str(uuid.uuid4()),
                                "rel": {
                                    "type": "association",
                                    "label": "in",  # Adjust the label as needed
                                    "multiplicity": {
                                        "source": "0..1",  # Example, adjust based on your data
                                        "target": "1"
                                    }
                                },
                                "rel_ptr": str(uuid.uuid4()),  # Unique pointer for the relation
                                "source_ptr": model_node["cls_ptr"],  # Source model pointer
                                "target_ptr": str(uuid.uuid4())  # Placeholder for target model pointer
                            }
                            edges.append(edge)

                        if field.one_to_many:
                            edge = {
                                "id": str(uuid.uuid4()),
                                "rel": {
                                    "type": "association",
                                    "label": "has",  # Adjust the label as needed
                                    "multiplicity": {
                                        "source": "1",  # Example, adjust based on your data
                                        "target": "1"
                                    }
                                },
                                "rel_ptr": str(uuid.uuid4()),
                                "source_ptr": model_node["cls_ptr"],
                                "target_ptr": str(uuid.uuid4())
                            }
                            edges.append(edge)

                        if field.many_to_many:
                            edge = {
                                "id": str(uuid.uuid4()),
                                "rel": {
                                    "type": "association",
                                    "label": "has",  # Adjust the label as needed
                                    "multiplicity": {
                                        "source": "1",
                                        "target": "0..n"
                                    }
                                },
                                "rel_ptr": str(uuid.uuid4()),
                                "source_ptr": model_node["cls_ptr"],
                                "target_ptr": str(uuid.uuid4())
                            }
                            edges.append(edge)

    # Create the final JSON structure
    template = Template(json_template)
    rendered_json = template.render(
        diagram_id=diagram_id,
        edges=edges,
        nodes=nodes,
        system_id=system_id,
        project_id=project_id
    )

    return rendered_json

if __name__ == "__main__":
    # Because Django projects have the following structure
    # my_project/
    # ├── manage.py
    # ├── my_project/
    # │   ├── __init__.py
    # │   ├─ settings.py
    # we can get the project settings file by locating the settings file in the project
    settings_file = sorted(pathlib.Path('../test_prototype').glob('**/settings.py'))[0]
    # and from the settings file location it is possible to get the project root
    project_root = settings_file.parents[1]

    sys.path.append(project_root.as_posix())

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', project_root.name + '.settings')

    # Remove duplicate 'admin' from INSTALLED_APPS dynamically
    if 'admin' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

    # # Now setup Django with the modified INSTALLED_APPS
    django.setup()
    diagram_json = generate_diagram_json()
    print(diagram_json)
# Django view to return the generated diagram as JSON
