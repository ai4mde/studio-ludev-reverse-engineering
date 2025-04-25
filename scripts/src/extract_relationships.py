import os
import sys
import django
from django.conf import settings
from jinja2 import Template
from django.apps import apps
from django.db import models
from django.db.models import ForeignKey, OneToOneField
import inspect
import uuid

# Constants
DJANGO_GENERATED_METHODS = {
    'check', 'clean', 'clean_fields', 'delete', 'full_clean', 'save',
    'save_base', 'validate_unique'
}

def is_not_subclass(field, model):
    related_model = field.related_model
    if related_model is None:
        return True
    if issubclass(model, related_model):
        return False
    return True


def extract_model_dependencies(model, all_the_models):
    dependencies = []

    # Loop through each method in the model
    for method_name, method in inspect.getmembers(model, predicate=inspect.isfunction):
        # Get the source code of the method
        try:
            code = inspect.getsource(method)
        except TypeError:  # This handles edge cases like non-methods
            continue

        print(f"Checking method: {method_name}")

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
        m not in DJANGO_GENERATED_METHODS
        # is_method_without_args(getattr(model, m, None))
    ]

def generate_diagram_json():
    diagram_id = str(uuid.uuid4())
    system_id = "eb846e17-a261-470a-abeb-09cd29980a46"
    project_id = "99fc3c09-07bc-43d2-bf59-429f99a35839"

    nodes = []
    edges = []
    model_ptr_map = {}
    enum_ptr_map = {}
  # Debug line

    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            print(f"Extracting models from: {app_config.verbose_name}")
            print(app_config.get_models())
            for model in app_config.get_models():
                cls_ptr = str(uuid.uuid4())
                model_ptr_map[model] = cls_ptr
                print("model: " , model)
                print("dependencies", extract_model_dependencies(model, app_config.get_models()))
                print("modrls: ", app_config.get_models())

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

        # Step 1: Check if the model is a child class (subclass of another model)
        parent_classes = [base for base in model.__bases__ if hasattr(base, '__name__') and base != object]

        # Step 2: Collect fields of parent classes (inherited fields)
        inherited_fields = set()
        for parent_class in parent_classes:
            if issubclass(parent_class, models.Model) and parent_class != models.Model:
                inherited_fields.update(f.name for f in parent_class._meta.get_fields() if hasattr(f, 'name'))

        for parent_class in parent_classes:
            print("parent_class:  ", parent_class)
            # Exclude internal Django and Python base classes
            if (
                    parent_class.__name__.startswith('django.') or
                    parent_class.__name__ == 'Model' or
                    parent_class.__name__ == 'object'
            ):
                continue

            target_ptr = model_ptr_map[parent_class]
            print("target_ptr:  ", target_ptr)
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
            if not hasattr(field, 'get_internal_type'):
                continue

                # Skip inherited fields (those from parent classes)
            if field.name in inherited_fields:
                continue

            if field.is_relation and hasattr(field, 'related_model') and field.related_model:
                target_model = field.related_model
                target_ptr = model_ptr_map.get(target_model)
                if not target_ptr:
                    continue

            if isinstance(field, models.ManyToManyField):

                if not field.null:
                    multiplicity = {
                        "source": "*",
                        "target": "1..*"
                    }
                else:
                    multiplicity = {
                        "source": "*",
                        "target": "*"
                    }


                edges.append({
                    "id": str(uuid.uuid4()),
                    "rel": {
                        "type": "association",
                        "label": "connects",
                        "derived": False,
                        "multiplicity": multiplicity
                    },
                    "data": {},
                    "rel_ptr": str(uuid.uuid4()),
                    "source_ptr": source_ptr,
                    "target_ptr": target_ptr
                })

            # OneToOne relationships
            elif isinstance(field, models.OneToOneField):
                if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
                    continue

                if not field.null:
                    multiplicity = {
                        "source": "1",
                        "target": "1"
                    }
                else:
                    multiplicity = {
                        "source": "1",
                        "target": "0..1"
                    }


                if get_relationship_type(field, model) == "composition":
                    edges.append({
                        "id": str(uuid.uuid4()),
                        "rel": {
                            "type": "composition",
                            "label": "connects",
                            "derived": False,
                            "multiplicity": multiplicity
                        },
                        "data": {},
                        "rel_ptr": str(uuid.uuid4()),
                        "source_ptr": source_ptr,
                        "target_ptr": target_ptr
                    })
                elif get_relationship_type(field, model) == "association":
                    edges.append({
                        "id": str(uuid.uuid4()),
                        "rel": {
                            "type": "association",
                            "label": "connects",
                            "derived": False,
                            "multiplicity": multiplicity
                        },
                        "data": {},
                        "rel_ptr": str(uuid.uuid4()),
                        "source_ptr": source_ptr,
                        "target_ptr": target_ptr
                    })

            # ForeignKey relationships
            elif isinstance(field, models.ForeignKey):
                if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
                    continue

                if not field.null:
                    multiplicity = {
                        "source": "1",
                        "target": "1..*"
                    }
                else:
                    multiplicity = {
                        "source": "1",
                        "target": "*"
                    }

                if get_relationship_type(field, model) == "composition":
                    edges.append({
                        "id": str(uuid.uuid4()),
                        "rel": {
                            "type": "composition",
                            "label": "connects",
                            "derived": False,
                            "multiplicity": multiplicity
                        },
                        "data": {},
                        "rel_ptr": str(uuid.uuid4()),
                        "source_ptr": source_ptr,
                        "target_ptr": target_ptr
                    })
                elif get_relationship_type(field, model) == "association":
                    edges.append({
                        "id": str(uuid.uuid4()),
                        "rel": {
                            "type": "association",
                            "label": "connects",
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
