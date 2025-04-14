import uuid
from core.utils import get_custom_methods

def build_diagram_models(models):
    nodes = []
    edges = []

    for model in models:
        node_id = str(uuid.uuid4())
        cls_ptr = str(uuid.uuid4())
        node = {
            "id": node_id,
            "cls": {
                "leaf": False,
                "name": model.__name__,
                "type": "class",
                "methods": [{"body": "", "name": name, "type": "function", "description": ""} for name in get_custom_methods(model)],
                "abstract": False,
                "namespace": "",
                "attributes": [{
                    "body": None,
                    "enum": None,
                    "name": field.name,
                    "type": field.get_internal_type().lower(),
                    "derived": False,
                    "description": None
                } for field in model._meta.get_fields()]
            },
            "data": {"position": {"x": 0, "y": 0}},
            "cls_ptr": cls_ptr
        }
        nodes.append(node)

        for field in model._meta.get_fields():
            if field.is_relation:
                edge = {
                    "id": str(uuid.uuid4()),
                    "rel": {
                        "type": "association",
                        "label": "has" if field.one_to_many or field.many_to_many else "in",
                        "multiplicity": {
                            "source": "1" if field.one_to_many else "0..1",
                            "target": "0..n" if field.many_to_many else "1"
                        }
                    },
                    "rel_ptr": str(uuid.uuid4()),
                    "source_ptr": cls_ptr,
                    "target_ptr": str(uuid.uuid4())  # Placeholder
                }
                edges.append(edge)

    return nodes, edges
