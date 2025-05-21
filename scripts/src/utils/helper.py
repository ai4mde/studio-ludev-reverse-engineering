import inspect
import uuid
from django.db import models


DJANGO_GENERATED_METHODS = {
    'check', 'clean', 'clean_fields', 'delete', 'full_clean', 'save',
    'save_base', 'validate_unique'
}


def is_enum_field(field):
    """
    Check if the field is an enum field (based on models.Choices).
    """
    if not hasattr(field, 'choices') or not isinstance(field.choices, list):
        return False

    if not field.choices:  # Check if list is empty
        return False

    try:
        # Check if all choices are binary tuples and first element is string or integer
        return all(
            isinstance(choice, tuple) and
            len(choice) == 2 and
            isinstance(choice[0], (str, str))
            for choice in field.choices
        )
    except (IndexError, TypeError):
        return False


def collect_all_valid_models(app_config):
    """Collect all models, including parent classes"""
    models = set()
    for model in app_config.get_models():
        models.add(model)
        # Add all parent classes
        for parent in model.__bases__:
            if hasattr(parent, '_meta') and not parent.__name__.startswith('django.') and parent.__name__ != 'Model' and not parent.__name__.startswith('Abstract'):
                models.add(parent)
    return models


def get_model_all_methods(model):
    try:
        return {
            name: inspect.getsource(func)
            for name, func in inspect.getmembers(model, predicate=inspect.isfunction)
        }
    except Exception as e:
        print(f"Error retrieving source for model '{model.__name__}': {e}")
        return None


def initialize_model_ptr_map(models):
    """Initialize model_ptr_map for all models"""
    return {model: str(uuid.uuid4()) for model in models}


def verify_data_integrity(data):
    print("Verifying data integrity...")
    for edge in data['edges']:
        source = edge['source_ptr']
        target = edge['target_ptr']
        if not any(node['id'] == source for node in data['nodes']):
            print(f"Warning: Source node not found {source}")
        if not any(node['id'] == target for node in data['nodes']):
            print(f"Warning: Target node not found {target}")


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
