import os
import sys
import uuid
import django
import inspect
from django.conf import settings
from django.apps import apps
from django.db import models
from django.db.models import ForeignKey, OneToOneField
from scripts.src.diagram_template import diagram_template_obj

# Django setup
sys.path.append('../../test_prototype/generated_prototypes/eb846e17-a261-470a-abeb-09cd29980a46/shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')


# Remove 'admin' app from INSTALLED_APPS before setup
if 'admin' in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']


DJANGO_GENERATED_METHODS = {
    'check', 'clean', 'clean_fields', 'delete', 'full_clean', 'save',
    'save_base', 'validate_unique'
}

django.setup()


# Fix: Add 2 blank lines before top-level function
def extract_model_dependencies(model, all_models, data):
    try:
        source_ptr = data['model_ptr_map'].get(model)
        if not source_ptr:
            return

        methods = _get_model_methods(model)
        if methods is None:
            return

        model_names = {m.__name__: m for m in all_models}
        _add_dependency_edges(model, methods, model_names, data, source_ptr)

    except Exception as outer_e:
        print(f"Unexpected error '{getattr(model, '__name__', str(model))}': {outer_e}")


def _get_model_methods(model):
    try:
        return {
            name: inspect.getsource(func)
            for name, func in inspect.getmembers(model, predicate=inspect.isfunction)
        }
    except Exception as e:
        print(f"Error retrieving source for model '{model.__name__}': {e}")
        return None


def _add_dependency_edges(model, source_code_map, model_names, data, source_ptr):
    added_targets = set()
    for method_name, code in source_code_map.items():
        for other_model_name, other_model in model_names.items():
            if other_model == model or other_model_name in added_targets:
                continue
            try:
                if other_model_name in code:
                    target_ptr = data['model_ptr_map'].get(other_model)
                    if target_ptr:
                        data['edges'].append(create_edge(
                            "dependency",
                            f"calls {method_name}",
                            {"source": "1", "target": "1"},
                            source_ptr,
                            target_ptr
                        ))
                        added_targets.add(other_model_name)
            except Exception as inner_e:
                print(f"Error processing dependency from '{model.__name__}' to '{other_model_name}': {inner_e}")


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
    print("Processing model:", source_ptr, model)

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
        print("parent_class:  ", parent_class)
        if (parent_class.__name__.startswith('django.') or
                parent_class.__name__ == 'Model' or
                parent_class.__name__ == 'object'):
            continue

        target_ptr = model_ptr_map[parent_class]
        print("target_ptr:  ", target_ptr)
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
        'system_id': "eb846e17-a261-470a-abeb-09cd29980a46",
        'project_id': "99fc3c09-07bc-43d2-bf59-429f99a35839",
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


def process_model(model, data, app_config, is_show_method_dependency):
    """Process a single model"""
    cls_ptr = data['model_ptr_map'][model]  # Use existing UUID

    # Only create a node if it hasn't been processed yet
    if not any(node['id'] == cls_ptr for node in data['nodes']):
        if is_show_method_dependency:
            extract_model_dependencies(model, app_config.get_models(), data)

        attributes = []
        for field in model._meta.get_fields():
            if not field.is_relation:
                enum_ref = None
                if is_enum_field(field):
                    enum_node, enum_ref = process_enum_field_node(field, data['enum_ptr_map'])
                    if enum_node:
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
            if hasattr(parent, '_meta') and not parent.__name__.startswith('django.') and parent.__name__ != 'Model':
                models.add(parent)
    return models


def initialize_model_ptr_map(models):
    """Initialize model_ptr_map for all models"""
    return {model: str(uuid.uuid4()) for model in models}


def generate_diagram_json(show_method_dependency):
    """Main function to generate diagram JSON"""
    data = initialize_diagram_data()

    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            print(f"Extracting models from: {app_config.verbose_name}")

            # First, collect all models (including parent classes)
            all_models = collect_all_models(app_config)

            # Initialize model_ptr_map for all models
            data['model_ptr_map'] = initialize_model_ptr_map(all_models)

            # Process all models
            for model in app_config.get_models():
                process_model(model, data, app_config, show_method_dependency)

    rendered = diagram_template_obj.render(
        diagram_id=data['diagram_id'],
        project_id=data['project_id'],
        system_id=data['system_id'],
        nodes=data['nodes'],
        edges=data['edges']
    )

    return rendered


if __name__ == "__main__":
    to_show_method_dependency = False
    generate_diagram_json(to_show_method_dependency)
