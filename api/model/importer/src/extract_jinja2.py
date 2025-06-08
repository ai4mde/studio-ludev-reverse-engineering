import inspect
import uuid
import os
import sys
import django
import pathlib
import zipfile
import argparse
from django.conf import settings
from jinja2 import Template
from django.apps import apps
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

projects_folder = "../projects"


# @pre model, Django model
# @post custom_methods array with all functions of method
def get_custom_methods(model):
    custom_methods = []
    standard_methods = set(dir(models.Model))
    for m in dir(model):
        if m.startswith('_') or m in standard_methods:
            continue
        if m in DJANGO_GENERATED_METHODS:
            continue
        if is_method_without_args(getattr(model, m)):
            custom_methods.append(m)
    return custom_methods


# @pre  func, Django method of model
# @post boolean where true, method has no arguments and false,
#       method has at least one argument
def is_method_without_args(func):
    """Check if func is a method callable with only one param (self)"""
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return False
    sig = inspect.signature(func)
    params = sig.parameters

    # Check if there is exactly one parameter and that has the name 'self'
    return len(params) == 1 and 'self' in params


# @pre -
# @post AI4MDE json string
def generate_diagram_json():
    # diagrams = []
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


# @pre -
# @post <argparse.Namespace> list of all arguments
def get_arguments():
    # Add argparse instance to parse arguments
    parser = argparse.ArgumentParser(
        prog='Django to AI4MDE JSON',
        description='Convert Django project to AI4MDE JSON structure'
    )

    # Add argument for zipfile
    parser.add_argument('-z', '--zip_file', help='specify the zip file to convert', required=True)

    # Parse argument
    args = parser.parse_args()

    # Validate args.zip_file contains a valid zip filename structure
    # If args.zip_file exists is checked in extract_zip()
    if len(args.zip_file) < 4 or args.zip_file[-4:] != '.zip' or len(args.zip_file) > 256:
        raise Exception('Please input a valid zip file')
    return args


# @pre filename is possible zipfile name
# @post extracted zip file
def extract_zip(filename):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        # check if directory already has been extracted before
        if not any([os.path.isdir(projects_folder + s[2:]) for s in zip_ref.namelist()]):
            zip_ref.extractall(projects_folder)


# @pre filename is a valid zip file name
# @post project root folder
def get_project_root(filename):
    # Because Django projects have the following structure
    # my_project/
    # ├── manage.py
    # ├── my_project/
    # │   ├── __init__.py
    # │   ├─ settings.py

    folder_name = pathlib.Path(filename).stem

    # We can get the project settings file by locating the settings file in the project
    settings_file = ''

    try:
        settings_file = sorted(pathlib.Path('../projects/' + folder_name).glob('**/settings.py'))[0]
    except IndexError:
        raise Exception('settings.py was not found in project.')

    # and from the settings file location it is possible to get the project root
    return settings_file.parents[1]


if __name__ == "__main__":
    # Get arguments for user
    args = get_arguments()

    # Extract zip
    extract_zip(args.zip_file)

    project_root = get_project_root(args.zip_file)

    sys.path.append(project_root.as_posix())

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', project_root.name + '.settings')

    # If settings.py is empty or broken
    # if not settings.configured:
    #     raise Exception('Django Project was not configured right.')

    # Remove duplicate 'admin' from INSTALLED_APPS dynamically
    if settings.INSTALLED_APPS and 'admin' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

    # Now setup Django with the modified INSTALLED_APPS
    try:
        django.setup()
    except ImportError:
        raise Exception('test')
    diagram_json = generate_diagram_json()
    print(diagram_json)
# Django view to return the generated diagram as JSON
