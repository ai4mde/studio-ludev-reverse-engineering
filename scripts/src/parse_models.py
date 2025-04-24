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


def parse_models():
    models_data = {
        "relationships": [],
        "nodes": [],
        "notes": []
    }

    seen_enums = set()

    for model in models_list:
        model_data = {
            "name": model.__name__,
            "relationships": [],
            "generalization": [],
            "composition": [],
            "dependencies": []
        }

        # Step 1: Check if the model is a child class (subclass of another model)
        parent_classes = [base for base in model.__bases__ if hasattr(base, '__name__') and base != object]

        # Step 2: Collect fields of parent classes (inherited fields)
        inherited_fields = set()
        for parent_class in parent_classes:
            if issubclass(parent_class, models.Model) and parent_class != models.Model:
                inherited_fields.update(f.name for f in parent_class._meta.get_fields() if hasattr(f, 'name'))

        for field in model._meta.get_fields():
            if not hasattr(field, 'get_internal_type'):
                continue

            # Skip inherited fields (those from parent classes)
            if field.name in inherited_fields:
                continue

            # ManyToMany relationships
            if isinstance(field, models.ManyToManyField):
                model_data["relationships"].append({
                    "type": "association",
                    "source": model.__name__,
                    "target": field.related_model.__name__,
                    "description": f"{model.__name__} has many-to-many association with {field.related_model.__name__}",
                    "multiplicity": "many-to-many",
                    "arrow_direction": f"{model.__name__} to {field.related_model.__name__}"
                })

            # OneToOne relationships
            elif isinstance(field, models.OneToOneField):
                if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
                    continue
                if is_composition(field, model):
                    model_data["composition"].append({
                        "type": "composition",
                        "source": model.__name__,
                        "target": field.related_model.__name__,
                        "description": f"{model.__name__} owns exactly one {field.related_model.__name__} (composition)",
                        "multiplicity": "1-to-1",
                        "arrow_direction": f"{model.__name__} to {field.related_model.__name__}"
                    })
                elif is_association(field, model):
                    model_data["relationships"].append({
                        "type": "association",
                        "source": model.__name__,
                        "target": field.related_model.__name__,
                        "description": f"{model.__name__} has one-to-one association with {field.related_model.__name__}",
                        "multiplicity": "1-to-1",
                        "arrow_direction": f"{model.__name__} to {field.related_model.__name__}"
                    })


            # ForeignKey relationships
            elif isinstance(field, models.ForeignKey):
                if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
                    continue

                if is_composition(field, model):
                    model_data["composition"].append({
                        "type": "composition",
                        "source": model.__name__,
                        "target": field.related_model.__name__,
                        "description": f"{model.__name__} owns many {field.related_model.__name__} (composition)",
                        "multiplicity": "many-to-1",
                        "arrow_direction": f"{model.__name__} to {field.related_model.__name__}"
                    })
                elif is_association(field, model):
                    model_data["relationships"].append({
                        "type": "association",
                        "source": model.__name__,
                        "target": field.related_model.__name__,
                        "description": f"{model.__name__} has many-to-one association with {field.related_model.__name__}",
                        "multiplicity": "many-to-1",
                        "arrow_direction": f"{model.__name__} to {field.related_model.__name__}"
                    })

            # Enum dependency detection
            if isinstance(field, models.CharField) and hasattr(field, 'choices') and field.choices:
                enum_class = None
                default = getattr(field, 'default', None)
                if default and hasattr(default, '__class__'):
                    default_class = default.__class__
                    if issubclass(default_class, models.TextChoices):
                        enum_class = default_class

                if enum_class:
                    # Add enum only once
                    enum_names = [e["name"] for e in models_data.get("enums", [])]
                    if enum_class.__name__ not in enum_names:
                        models_data.setdefault("enums", []).append({
                            "type": "enum",
                            "name": enum_class.__name__,
                            "literals": [member.name for member in enum_class]
                        })

                    if is_not_subclass(field, model):
                        model_data.setdefault("dependencies", []).append({
                            "type": "dependency",
                            "source": model.__name__,
                            "target": enum_class.__name__,
                            "description": f"{model.__name__} depends on {enum_class.__name__} (Enum)",
                            "arrow_direction": f"{model.__name__} to {enum_class.__name__}"
                        })

        for parent_class in parent_classes:
            # Exclude internal Django and Python base classes
            if (
                    parent_class.__name__.startswith('django.') or
                    parent_class.__name__ == 'Model' or
                    parent_class.__name__ == 'object'
            ):
                continue

            model_data["generalization"].append({
                "type": "generalization",
                "source": model.__name__,
                "target": parent_class.__name__,
                "description": f"{model.__name__} inherits from {parent_class}",
                "arrow_direction": f"{model.__name__} to {parent_class}"
            })

        # Add relationships to global structure
        models_data["relationships"].extend(model_data["relationships"])
        models_data["relationships"].extend(model_data["composition"])
        models_data["relationships"].extend(model_data["generalization"])
        models_data["relationships"].extend(model_data["dependencies"])

    # Notes
    models_data["notes"] = [
        "Composition relationships are identified by OneToOneField or ForeignKey with on_delete=CASCADE",
        "Associations include ForeignKey, OneToOneField, and ManyToManyField relationships",
        "Generalization represents inheritance between models",
        "Enum dependencies are inferred from CharField/IntegerField with choices defined as subclasses of models.Choices"
    ]

    return json.dumps(models_data, indent=4)


if __name__ == "__main__":
    # Django setup
    sys.path.append('../../test_prototype/generated_prototypes/eb846e17-a261-470a-abeb-09cd29980a46/shop')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

    # Clean INSTALLED_APPS before setup
    if 'admin' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'admin']

    django.setup()

    models_list = []
    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            print(f"Extracting models from: {app_config.verbose_name}")
            for model in app_config.get_models():
                models_list.append(model)
    json_data = parse_models()
    print(json_data)