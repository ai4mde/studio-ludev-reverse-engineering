import os
from pathlib import Path
import sys
import uuid
import django
import inspect
import argparse
from django.conf import settings
from django.apps import apps
from django.db import models
from django.db.models import ForeignKey, OneToOneField
from jinja2 import Template

diagram_template = """
{
    "id": "{{ diagram_id }}",
    "name": "Diagram",
    "type": "classes",
    "nodes": [
        {% for node in nodes %}
        {
          "id": "{{ node.id }}",
          "cls": {
            {% if node.cls.type == 'enum' %}
            "name": "{{ node.cls.name }}",
            "type": "enum",
            "literals": {{ node.cls.literals | tojson }},
            "namespace": "{{ node.cls.namespace }}"
            {% else %}
            "leaf": {{ node.cls.leaf | lower }},
            "name": "{{ node.cls.name }}",
            "type": "class",
            "methods": [
              {% for method in node.cls.methods %}
              {
                "body": "{{ method.body }}",
                "name": "{{ method.name }}",
                "type": "{{ method.type }}",
                "description": "{{ method.description }}"
              }
              {% if not loop.last %},{% endif %}
              {% endfor %}
            ],
            "abstract": {{ node.cls.abstract | lower}},
            "namespace": "{{ node.cls.namespace }}",
            "attributes": [
              {% for attribute in node.cls.attributes %}
              {
                "body": "{{ attribute.body }}",
                "enum": "{{ attribute.enum }}",
                "name": "{{ attribute.name }}",
                "type": "{{ attribute.type }}",
                "derived": "{{ attribute.derived | lower }}",
                "description": "{{ attribute.description }}"
              }
              {% if not loop.last %},{% endif %}
              {% endfor %}
            ]
            {% endif %}
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
    "system": "{{ system_id }}",
    "project": "{{ project_id }}",
    "description": ""
}
"""

DJANGO_GENERATED_METHODS = {
    'check', 'clean', 'clean_fields', 'delete', 'full_clean', 'save',
    'save_base', 'validate_unique'
}

# Constants
def extract_model_dependencies(model, all_the_models):
    dependencies = []

    # Loop through each method in the model
    for method_name, method in inspect.getmembers(model, predicate=inspect.isfunction):
        # Get the source code of the method
        try:
            code = inspect.getsource(method)
        except TypeError:  # This handles edge cases like non-methods
            continue

        # print(f"Checking method: {method_name}")

        for other_model in all_the_models:
            # Ensure we are checking other models, not the current model
            if other_model.__name__ != model.__name__:
                # Check if the model's class name appears in the method code
                if other_model.__name__ in code:
                    # Additional logic to check if it's an actual dependency (not just name occurrence)
                    dependencies.append({
                        'model': model.__name__,
                        'dependency': other_model.__name__,
                        'method': method_name,
                    })

    return dependencies


def get_relationship_type(field, model):
    related_model = field.related_model
    if issubclass(model, related_model):
        return 'unknown'

    if isinstance(field, (ForeignKey, OneToOneField)):
        if field.remote_field.on_delete == models.CASCADE:
            if not field.null:
                return 'composition'
            else:
                return 'association'
        else:
            return 'association'
    return 'unknown'


def is_enum_field(field):
    """
    Check if the field is an enum field (choices are based on models.Choices).
    """
    return hasattr(field, 'choices') and isinstance(field.choices, list) and isinstance(field.choices[0][0], (str, int))


def map_field_type(field):
    """
    Map Django field types to the expected types for the diagram.
    """
    if is_enum_field(field):
        return "enum"
    if isinstance(field, models.CharField):
        return "str"
    elif isinstance(field, models.TextField):
        return "str"
    elif isinstance(field, models.IntegerField):
        return "int"
    elif isinstance(field, models.BooleanField):
        return "bool"
    elif isinstance(field, models.DateTimeField):
        return "datetime"
    elif isinstance(field, models.DateField):
        return "datetime"
    else:
        return "str"


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


# @pre func, Django method of model
# @post boolean where true, method has no arguments and false, method has at least one argument
def is_method_without_args(func):
    """Check if func is a method callable with only one param (self)"""
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return False
    sig = inspect.signature(func)
    params = sig.parameters

    # Check if there is exactly one parameter and that has the name 'self'
    return len(params) == 1 and 'self' in params


def process_model_relationships(model, model_ptr_map, enum_ptr_map, edges):
    """Process relationships between models and generate corresponding edges."""
    source_ptr = model_ptr_map[model]
    # print("Processing model:", source_ptr, model)

    # Step 1: Process inheritance relationships
    process_inheritance_relationships(model, model_ptr_map, edges, source_ptr)

    # Step 2: Process other types of relationships
    process_field_relationships(model, model_ptr_map, enum_ptr_map, edges, source_ptr)


def process_inheritance_relationships(model, model_ptr_map, edges, source_ptr):
    """Process model inheritance relationships."""
    parent_classes = [base for base in model.__bases__ if hasattr(base, '__name__') and base != object]

    # Collect fields from parent classes (inherited fields)
    inherited_fields = set()
    for parent_class in parent_classes:
        if issubclass(parent_class, models.Model) and parent_class != models.Model:
            inherited_fields.update(f.name for f in parent_class._meta.get_fields() if hasattr(f, 'name'))

    for parent_class in parent_classes:
        # print("parent_class:  ", parent_class)
        if (parent_class.__name__.startswith('django.') or
                parent_class.__name__ == 'Model' or
                parent_class.__name__ == 'object'):
            continue

        target_ptr = model_ptr_map[parent_class]
        # print("target_ptr:  ", target_ptr)
        edges.append(create_edge("generalization", "inherits", {"source": "1", "target": "1"},
                                 source_ptr, target_ptr))

    return inherited_fields


def process_field_relationships(model, model_ptr_map, enum_ptr_map, edges, source_ptr):
    """Process model field relationships."""
    inherited_fields = process_inheritance_relationships(model, model_ptr_map, edges, source_ptr)

    for field in model._meta.get_fields():
        if not hasattr(field, 'get_internal_type'):
            continue

        if field.name in inherited_fields:
            continue

        if field.is_relation and hasattr(field, 'related_model') and field.related_model:
            target_model = field.related_model
            target_ptr = model_ptr_map.get(target_model)
            if not target_ptr:
                continue

            process_relationship_field(field, model, edges, source_ptr, target_ptr)

        elif is_enum_field(field):
            process_enum_field(field, enum_ptr_map, edges, source_ptr)


def process_relationship_field(field, model, edges, source_ptr, target_ptr):
    """Process relationship fields."""
    if isinstance(field, models.ManyToManyField):
        process_many_to_many_field(field, edges, source_ptr, target_ptr)
    elif isinstance(field, models.OneToOneField):
        process_one_to_one_field(field, model, edges, source_ptr, target_ptr)
    elif isinstance(field, models.ForeignKey):
        process_foreign_key_field(field, model, edges, source_ptr, target_ptr)


def process_many_to_many_field(field, edges, source_ptr, target_ptr):
    """Process many-to-many fields."""
    multiplicity = {
        "source": "*",
        "target": "1..*" if not field.null else "*"
    }
    edges.append(create_edge("association", "connects", multiplicity, source_ptr, target_ptr))


def process_one_to_one_field(field, model, edges, source_ptr, target_ptr):
    """Process one-to-one fields."""
    if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
        return

    multiplicity = {
        "source": "1",
        "target": "1" if not field.null else "0..1"
    }

    rel_type = get_relationship_type(field, model)
    if rel_type in ["composition", "association"]:
        edges.append(create_edge(rel_type, "connects", multiplicity, target_ptr, source_ptr))


def process_foreign_key_field(field, model, edges, source_ptr, target_ptr):
    """Process foreign key fields."""
    if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
        return

    rel_type = get_relationship_type(field, model)

    if rel_type in ["composition", "association"]:
        if rel_type == "composition":
            multiplicity = {
                "target": "1..*" if not field.null else "*",
                "source": "1"
            }
            edges.append(create_edge(rel_type, "connects", multiplicity, target_ptr, source_ptr))
        else:
            multiplicity = {
                "source": "1..*" if not field.null else "*",
                "target": "1"
            }
            edges.append(create_edge(rel_type, "connects", multiplicity, source_ptr, target_ptr))


def process_enum_field(field, enum_ptr_map, edges, source_ptr):
    """Process enum fields."""
    enum_ptr = enum_ptr_map.get(field.name)
    if enum_ptr:
        edges.append(create_edge("dependency", "depends",
                                 {"source": "1", "target": "1"}, source_ptr, enum_ptr))


def create_edge(rel_type, label, multiplicity, source_ptr, target_ptr):
    """Create an edge object."""
    return {
        "id": str(uuid.uuid4()),
        "rel": {
            "type": rel_type,
            "label": label,
            "derived": False,
            "multiplicity": multiplicity
        },
        "data": {},
        "rel_ptr": str(uuid.uuid4()),
        "source_ptr": source_ptr,
        "target_ptr": target_ptr
    }


# Functions related to diagram initialization
def initialize_diagram_data():
    """Initialize the basic data needed for the diagram"""
    return {
        'diagram_id': str(uuid.uuid4()),
        'system_id': "28e89254-6b6f-4f83-91ff-8b3611f47d48",
        'project_id': "0ae9498f-3535-40d1-bf9f-33e250c21519",
        'nodes': [],
        'edges': [],
        'model_ptr_map': {},
        'enum_ptr_map': {}
    }


def process_enum_field_node(field, enum_ptr_map):
    """Process enum field node"""
    choices = field.choices
    literals = [choice[0] for choice in choices]
    enum_ref = enum_ptr_map.get(field.name)

    if enum_ref is None:
        enum_id = str(uuid.uuid4())
        enum_ptr_map[field.name] = enum_id

        enum_node = {
            "id": enum_id,
            "cls": {
                "name": field.name,
                "type": "enum",
                "literals": literals,
                "namespace": ""
            },
            "data": {
                "position": {"x": -960, "y": -30}
            },
            "cls_ptr": str(uuid.uuid4())
        }
        return enum_node, enum_id
    return None, enum_ref


def create_attribute(field, enum_ref):
    """Create attribute object"""
    return {
        "body": None,
        "enum": enum_ref,
        "name": field.name,
        "type": map_field_type(field),
        "derived": False,
        "description": None
    }


def create_model_node(model, cls_ptr, attributes):
    """Create model node"""
    return {
        "id": cls_ptr,
        "cls": {
            "leaf": False,
            "name": model.__name__,
            "type": "class",
            "methods": [
                {
                    "body": "",
                    "name": method,
                    "type": "str",
                    "description": ""
                }
                for method in get_custom_methods(model)
            ],
            "abstract": False,
            "namespace": "",
            "attributes": attributes
        },
        "data": {
            "position": {"x": 0, "y": 0}
        },
        "cls_ptr": str(uuid.uuid4())
    }


def process_model(model, data, app_config):
    """Process a single model"""
    cls_ptr = data['model_ptr_map'][model]  # Use existing UUID

    # Only create a node if it hasn't been processed yet
    if not any(node['id'] == cls_ptr for node in data['nodes']):
        # print("model: ", model)
        # print("dependencies", extract_model_dependencies(model, app_config.get_models()))
        # print("models: ", app_config.get_models())

        attributes = []
        for field in model._meta.get_fields():
            if not field.is_relation:
                enum_ref = None
                if is_enum_field(field):
                    enum_node, enum_ref = process_enum_field_node(field, data['enum_ptr_map'])
                    if enum_node:
                        # print(enum_node)
                        data['nodes'].append(enum_node)

                attributes.append(create_attribute(field, enum_ref))

        node = create_model_node(model, cls_ptr, attributes)
        data['nodes'].append(node)

    process_model_relationships(model, data['model_ptr_map'], data['enum_ptr_map'], data['edges'])


def collect_all_models(app_config):
    """Collect all models, including parent classes"""
    models = set()
    for model in app_config.get_models():
        models.add(model)
        # Add all parent classes
        for parent in model.__bases__:
            if (hasattr(parent, '_meta') and not parent.__name__.startswith('django.') and parent.__name__ != 'Model'):
                models.add(parent)
    return models


def initialize_model_ptr_map(models):
    """Initialize model_ptr_map for all models"""
    return {model: str(uuid.uuid4()) for model in models}


def generate_diagram_json(extract_path):
    # Find the settings.py file
    settings_files = list(Path(extract_path).glob('**/settings.py'))
    if not settings_files:
        return {
            "success": False,
            "message": "No Django settings.py file found in the extracted directory"
        }


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

    django.setup()

    """Main function to generate diagram JSON"""
    data = initialize_diagram_data()

    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':  # Only process 'Shared_Models'
            # print(f"Extracting models from: {app_config.path}")

            # First, collect all models (including parent classes)
            all_models = collect_all_models(app_config)

            # Initialize model_ptr_map for all models
            data['model_ptr_map'] = initialize_model_ptr_map(all_models)

            # Process all models
            for model in app_config.get_models():
                process_model(model, data, app_config)

    # create the template object
    diagram_template_obj = Template(diagram_template)
    rendered = diagram_template_obj.render(
        diagram_id=data['diagram_id'],
        project_id=data['project_id'],
        system_id=data['system_id'],
        nodes=data['nodes'],
        edges=data['edges']
    )

    return rendered

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", "-p", default=".", help="starting path")
    args = parser.parse_args()

    diagram = generate_diagram_json(args.path)

    print(diagram)

if __name__ == "__main__":
    main()
