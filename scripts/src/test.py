import json
import os
import sys
import django
from django.conf import settings
from django.apps import apps
from django.db import models


def is_not_subclass(field, model):
    related_model = field.related_model
    if related_model is None:
        return True
    if issubclass(model, related_model):
        return False
    return True


def is_composition(field, model):
    if not isinstance(field, (models.ForeignKey, models.OneToOneField)):
        return False

    if field.remote_field.on_delete != models.CASCADE:
        return False

    related_model = field.related_model
    if issubclass(model, related_model):
        return False
    return True


def is_association(field, model):
    if isinstance(field, models.ManyToManyField):
        return True

    if isinstance(field, (models.ForeignKey, models.OneToOneField)):
        related_model = field.related_model
        if issubclass(model, related_model):
            return False

        return field.remote_field.on_delete != models.CASCADE

    return False


def parse_edge(models_list, model_ptr_map):
    edges = []
    enums = []


    seen_enums = set()

    for model in models_list:
        model_data = {
            "name": model.__name__,
            "relationships": [],
            "generalization": [],
            "composition": [],
            "dependencies": []
        }

        parent_classes = [base for base in model.__bases__ if hasattr(base, '__name__') and base != object]

        inherited_fields = set()
        for parent_class in parent_classes:
            if issubclass(parent_class, models.Model) and parent_class != models.Model:
                inherited_fields.update(f.name for f in parent_class._meta.get_fields() if hasattr(f, 'name'))

        source_ptr = model_ptr_map[model]

        for field in model._meta.get_fields():
            if not hasattr(field, 'get_internal_type'):
                continue

            if field.name in inherited_fields:
                continue

            target_model = field.related_model
            target_ptr = model_ptr_map.get(target_model)

            if isinstance(field, models.ManyToManyField):
                edges.append({
                    "id": f"{model.__name__}_many_to_many_{field.related_model.__name__}",
                    "rel": {
                        "type": "association",
                        "label": f"{model.__name__} to {field.related_model.__name__}",
                        "multiplicity": {
                            "source": "many",
                            "target": "many"
                        }
                    },
                    "data": {},
                    "rel_ptr": f"{model.__name__}_many_to_many_{field.related_model.__name__}",
                    "source_ptr": source_ptr,
                    "target_ptr": target_ptr
                })

            elif isinstance(field, models.OneToOneField):
                if is_composition(field, model):
                    edges.append({
                        "id": f"{model.__name__}_composition_{field.related_model.__name__}",
                        "rel": {
                            "type": "composition",
                            "label": f"{model.__name__} to {field.related_model.__name__}",
                            "multiplicity": {
                                "source": "1",
                                "target": "1"
                            }
                        },
                        "data": {},
                        "rel_ptr": f"{model.__name__}_composition_{field.related_model.__name__}",
                        "source_ptr": source_ptr,
                        "target_ptr": target_ptr
                    })
                elif is_association(field, model):
                    edges.append({
                        "id": f"{model.__name__}_one_to_one_{field.related_model.__name__}",
                        "rel": {
                            "type": "association",
                            "label": f"{model.__name__} to {field.related_model.__name__}",
                            "multiplicity": {
                                "source": "1",
                                "target": "1"
                            }
                        },
                        "data": {},
                        "rel_ptr": f"{model.__name__}_one_to_one_{field.related_model.__name__}",
                        "source_ptr": model.__name__,
                        "target_ptr": target_ptr
                    })

            elif isinstance(field, models.ForeignKey):
                if is_composition(field, model):
                    edges.append({
                        "id": f"{model.__name__}_composition_{field.related_model.__name__}",
                        "rel": {
                            "type": "composition",
                            "label": f"{model.__name__} to {field.related_model.__name__}",
                            "multiplicity": {
                                "source": "many",
                                "target": "1"
                            }
                        },
                        "data": {},
                        "rel_ptr": f"{model.__name__}_composition_{field.related_model.__name__}",
                        "source_ptr": source_ptr,
                        "target_ptr": target_ptr
                    })
                elif is_association(field, model):
                    edges.append({
                        "id": f"{model.__name__}_many_to_one_{field.related_model.__name__}",
                        "rel": {
                            "type": "association",
                            "label": f"{model.__name__} to {field.related_model.__name__}",
                            "multiplicity": {
                                "source": "many",
                                "target": "1"
                            }
                        },
                        "data": {},
                        "rel_ptr": f"{model.__name__}_many_to_one_{field.related_model.__name__}",
                        "source_ptr": source_ptr,
                        "target_ptr": target_ptr
                    })

            if isinstance(field, models.CharField) and hasattr(field, 'choices') and field.choices:
                enum_class = None
                default = getattr(field, 'default', None)
                if default and hasattr(default, '__class__'):
                    default_class = default.__class__
                    if issubclass(default_class, models.TextChoices):
                        enum_class = default_class

                if enum_class:
                    if enum_class.__name__ not in seen_enums:
                        seen_enums.add(enum_class.__name__)
                        enums.append({
                            "type": "enum",
                            "name": enum_class.__name__,
                            "literals": [member.name for member in enum_class]
                        })

                    if is_not_subclass(field, model):
                        edges.append({
                            "id": f"{model.__name__}_dependency_{enum_class.__name__}",
                            "rel": {
                                "type": "dependency",
                                "label": f"{model.__name__} depends on {enum_class.__name__}",
                                "multiplicity": {
                                    "source": "1",
                                    "target": "1"
                                }
                            },
                            "data": {},
                            "rel_ptr": f"{model.__name__}_dependency_{enum_class.__name__}",
                            "source_ptr": source_ptr,
                            "target_ptr": target_ptr
                        })

    return edges



# if __name__ == "__main__":
#     sys.path.append('../../test_prototype/generated_prototypes/eb846e17-a261-470a-abeb-09cd29980a46/shop')
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
#
#     if 'admin' in settings.INSTALLED_APPS:
#         settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']
#
#     django.setup()
#
#     models_list = []
#     for app_config in apps.get_app_configs():
#         if app_config.name == 'shared_models':
#             print(f"Extracting models from: {app_config.verbose_name}")
#             for model in app_config.get_models():
#                 models_list.append(model)
#
#     model_ptr_map = {}
#     json_data = parse_edge(model_ptr_map)
#     print(json_data)
