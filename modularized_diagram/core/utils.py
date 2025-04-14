import inspect
from django.db import models

DJANGO_GENERATED_METHODS = {'check', 'clean', 'clean_fields', 'delete', 'full_clean', 'save', 'save_base', 'validate_unique'}

def is_method_without_args(func):
    if not inspect.isfunction(func) and not inspect.ismethod(func):
        return False
    sig = inspect.signature(func)
    return len(sig.parameters) == 1 and 'self' in sig.parameters

def get_custom_methods(model):
    custom = []
    standard = set(dir(models.Model))
    for m in dir(model):
        if m.startswith('_') or m in standard or m in DJANGO_GENERATED_METHODS:
            continue
        if is_method_without_args(getattr(model, m, None)):
            custom.append(m)
    return custom
