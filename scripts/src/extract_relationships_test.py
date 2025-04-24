import inspect
import uuid
import os
import sys
import django
from django.conf import settings
from jinja2 import Template
from django.apps import apps
from django.db import models

# Constants
DJANGO_GENERATED_METHODS = {
    'check', 'clean', 'clean_fields', 'delete', 'full_clean', 'save',
    'save_base', 'validate_unique'
}

# Jinja2 JSON template
json_template = """
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
    "system": "{{ system_id }}",
    "project": "{{ project_id }}",
    "description": ""
}
"""

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

# Django setup
sys.path.append('../../test_prototype/generated_prototypes/eb846e17-a261-470a-abeb-09cd29980a46/shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

# Clean INSTALLED_APPS before setup
if 'admin' in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

django.setup()

def is_method_without_args(func):
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return False
    sig = inspect.signature(func)
    return len(sig.parameters) == 1 and 'self' in sig.parameters

def get_custom_methods(model):
    standard_methods = set(dir(models.Model))
    return [
        m for m in dir(model)
        if not m.startswith('_') and
        m not in standard_methods and
        m not in DJANGO_GENERATED_METHODS and
        is_method_without_args(getattr(model, m, None))
    ]

def generate_diagram_json():
    diagram_id = str(uuid.uuid4())
    system_id = "eb846e17-a261-470a-abeb-09cd29980a46"
    project_id = "99fc3c09-07bc-43d2-bf59-429f99a35839"

    nodes = []
    edges = []
    model_ptr_map = {}
    enum_ptr_map = {}

    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            print(f"Extracting models from: {app_config.verbose_name}")
            for model in app_config.get_models():
                cls_ptr = str(uuid.uuid4())
                model_ptr_map[model] = cls_ptr

                attributes = []
                for field in model._meta.get_fields():
                    if not field.is_relation:
                        enum_ref = None
                        # Check if the field has 'choices' and if it is an enum type (instance of models.Choices)
                        if is_enum_field(field):
                            choices = field.choices
                            literals = [choice[0] for choice in choices]  # Extract the values from the tuple pairs
                            enum_ref = enum_ptr_map.get(field.name)

                            # Check if this enum has been added already, and if not, add it
                            if enum_ref is None:
                                enum_id = str(uuid.uuid4())
                                enum_ptr_map[field.name] = enum_id

                                enum_node = {
                                    "id": enum_id,
                                    "cls": {
                                        "name": field.name,  # Use the name of the field as the enum name
                                        "type": "enum",
                                        "literals": literals,
                                        "namespace": ""
                                    },
                                    "data": {
                                        "position": {"x": -960, "y": -30}  # Example position for layout
                                    },
                                    "cls_ptr": str(uuid.uuid4())
                                }

                                print(enum_node)
                                nodes.append(enum_node)

                        # Set the enum reference for the attribute if it exists
                        attributes.append({
                            "body": None,
                            "enum": enum_ref,
                            "name": field.name,
                            "type": map_field_type(field),
                            "derived": False,
                            "description": None
                        })

                node = {
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
                    "cls_ptr": cls_ptr
                }

                nodes.append(node)

    # Add edges *after* all nodes are created
    for model in model_ptr_map:
        source_ptr = model_ptr_map[model]
        print("Processing model:", source_ptr , model)

        # 1. Generalization (model inheritance)
        for base in model.__bases__:
            print("base:  " , base)
            if base in model_ptr_map:
                target_ptr = model_ptr_map[base]
                edges.append({
                    "id": str(uuid.uuid4()),
                    "rel": {
                        "type": "generalization",
                        "label": "inherits",
                        "derived": False,
                        "multiplicity": {
                            "source": "1",
                            "target": "1"
                        }
                    },
                    "data": {},
                    "rel_ptr": str(uuid.uuid4()),
                    "source_ptr": source_ptr,
                    "target_ptr": target_ptr
                })

        # 2. Associations, compositions, and dependencies
        for field in model._meta.get_fields():
            # Handle model relationships
            if field.is_relation and hasattr(field, 'related_model') and field.related_model:
                target_model = field.related_model
                target_ptr = model_ptr_map.get(target_model)
                if not target_ptr:
                    continue

                is_composition = getattr(field, 'on_delete', None) == models.CASCADE and not getattr(field, 'null',
                                                                                                     False)
                rel_type = "composition" if is_composition else "association"
                label = "composes" if is_composition else (
                    "has" if field.one_to_many or field.many_to_many else "uses"
                )
                multiplicity = {
                    "source": "1" if field.one_to_many or field.one_to_one else "*",
                    "target": "*" if field.many_to_many or field.many_to_one else "1"
                }

                edges.append({
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
                })

            # Handle enum-based dependencies
            elif is_enum_field(field):
                enum_ptr = enum_ptr_map.get(field.name)
                if enum_ptr:
                    edges.append({
                        "id": str(uuid.uuid4()),
                        "rel": {
                            "type": "dependency",
                            "label": "depends",
                            "derived": False,
                            "multiplicity": {
                                "source": "1",
                                "target": "1"
                            }
                        },
                        "data": {},
                        "rel_ptr": str(uuid.uuid4()),
                        "source_ptr": source_ptr,
                        "target_ptr": enum_ptr
                    })

    template = Template(json_template)
    return template.render(
        diagram_id=diagram_id,
        edges=edges,
        nodes=nodes,
        system_id=system_id,
        project_id=project_id
    )

if __name__ == "__main__":
    diagram_json = generate_diagram_json()
    print(diagram_json)
