import inspect
import sys
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

    if not field.choices:  # empty list
        return False

    try:
        # each choice must be a (key, label) tuple, key is str or int
        return all(
            isinstance(choice, tuple)
            and len(choice) == 2
            and isinstance(choice[0], (str, int))
            for choice in field.choices
        )
    except (IndexError, TypeError):
        return False


def collect_all_valid_models(app_config):
    """Collect all models, including parent classes"""
    models_set = set()
    for model in app_config.get_models():
        models_set.add(model)
        for parent in model.__bases__:
            name = parent.__name__
            if hasattr(parent, '_meta') \
               and not name.startswith(('django.', 'Abstract')) \
               and name != 'Model':
                models_set.add(parent)
    return models_set


def get_model_all_methods(model):
    try:
        return {
            name: inspect.getsource(func)
            for name, func in inspect.getmembers(model, predicate=inspect.isfunction)
        }
    except Exception:
        return None


def initialize_model_ptr_map(models):
    """Initialize model_ptr_map for all models"""
    return {model: str(uuid.uuid4()) for model in models}


def verify_data_integrity(data):
    """Check that edges reference existing nodes"""
    for edge in data.get('edges', []):
        source = edge.get('source_ptr')
        target = edge.get('target_ptr')
        if not any(node.get('id') == source for node in data.get('nodes', [])):
            sys.exit(f"Warning: Source node not found {source}")  # line 68
        if not any(node.get('id') == target for node in data.get('nodes', [])):
            sys.exit(f"Warning: Target node not found {target}")


def get_custom_methods(model):
    """Return names of model methods that take only self"""
    custom = []
    standard = set(dir(models.Model))
    for m in dir(model):
        if m.startswith('_') or m in standard or m in DJANGO_GENERATED_METHODS:
            continue
        attr = getattr(model, m)
        if is_method_without_args(attr):       # line 80
            custom.append(m)
    return custom


def is_method_without_args(func):
    """
    Check if func is a method callable with only one param (self).
    """
    if not (inspect.isfunction(func) or inspect.ismethod(func)):
        return False
    try:
        sig = inspect.signature(func)
        params = sig.parameters
        return len(params) == 1 and 'self' in params
    except Exception:
        return False
