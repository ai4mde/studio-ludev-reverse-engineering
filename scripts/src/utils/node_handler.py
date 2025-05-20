import uuid
from django.db import models

from scripts.src.utils.helper import is_enum_field, get_custom_methods


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