import uuid
from django.db import models
from django.db.models import ForeignKey, OneToOneField

from scripts.src.utils.helper import is_enum_field, get_model_all_methods


def create_edge(rel_type, label, multiplicity, source_ptr, target_ptr):
    """Create an edge object."""
    print(f"Creating edge:")
    print(f"  Type: {rel_type}")
    print(f"  Label: {label}")
    print(f"  Source node: {source_ptr}")
    print(f"  Target node: {target_ptr}")

    if not source_ptr or not target_ptr:
        print("Warning: Invalid node pointers")
        return None

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


def process_model_relationships(model, model_ptr_map, enum_ptr_map, edges):
    """Process relationships between models and generate corresponding edges."""
    source_ptr = model_ptr_map[model]
    # print("Processing model:", source_ptr, model)

    # Step 1: Process inheritance relationships
    process_inheritance_relationships(model, model_ptr_map, edges, source_ptr)

    # Step 2: Process other types of relationships
    process_field_relationships(model, model_ptr_map, enum_ptr_map, edges, source_ptr)


def process_inheritance_relationships(model, model_ptr_map, edges, source_ptr):
    """Process model inheritance relationships."""
    parent_classes = [base for base in model.__bases__ if hasattr(base, '__name__') and base is not object]

    # Collect fields from parent classes (inherited fields)
    inherited_fields = set()
    for parent_class in parent_classes:
        if issubclass(parent_class, models.Model) and parent_class != models.Model:
            inherited_fields.update(f.name for f in parent_class._meta.get_fields() if hasattr(f, 'name'))

    for parent_class in parent_classes:
        # print("parent_class:  ", parent_class)
        if (parent_class.__name__.startswith('django.') or
                parent_class.__name__ == 'Model' or
                parent_class.__name__ == 'object'):
            continue
        
        # FIX: Safely get the target_ptr to prevent KeyError if parent_class is not in the map.
        target_ptr = model_ptr_map.get(parent_class)
        if not target_ptr:
            continue

        edges.append(create_edge("generalization", "inherits", {"source": "1", "target": "1"},
                                 source_ptr, target_ptr))

    return inherited_fields


def process_field_relationships(model, model_ptr_map, enum_ptr_map, edges, source_ptr):
    """Process model field relationships."""
    inherited_fields = process_inheritance_relationships(model, model_ptr_map, edges, source_ptr)

    for field in model._meta.get_fields():
        if not hasattr(field, 'get_internal_type'):
            continue  # Skip this field if it doesn't have 'get_internal_type' attribute

        if field.name in inherited_fields:
            continue  # Skip this field if its name is in inherited_fields

        if field.is_relation and hasattr(field, 'related_model') and field.related_model:
            target_model = field.related_model
            target_ptr = model_ptr_map.get(target_model)
            if not target_ptr:
                continue  # Skip if no target_ptr exists

            process = True
            # Skip processing the edge if label starts with 'calls' and source/target match
            for edge in edges:
                if edge.get('rel', {}).get('label', '').startswith('calls'):
                    if edge.get('source_ptr') == source_ptr and edge.get('target_ptr') == target_ptr:
                        print(f"Skipping edge with label starting with 'calls' between {source_ptr} and {target_ptr}: {edge}")
                        process = False
                        continue
            if process:
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


def get_relationship_type(field, model):
    related_model = field.related_model
    if issubclass(model, related_model):
        return 'inheritance'

    if isinstance(field, (ForeignKey, OneToOneField)):
        if field.remote_field.on_delete == models.CASCADE:
            if not field.null:
                return 'composition'
            else:
                return 'association'
        else:
            return 'association'
    return 'unknown'


def process_many_to_many_field(field, edges, source_ptr, target_ptr):
    """Process many-to-many fields."""
    multiplicity = {
        "source": "*",
        "target": "1..*" if not field.null else "*"
    }
    edges.append(create_edge("association", "connect", multiplicity, source_ptr, target_ptr))


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
        if rel_type == "composition":
            edges.append(create_edge(rel_type, "compose", multiplicity, target_ptr, source_ptr))
        else:
            edges.append(create_edge(rel_type, "connect", multiplicity, source_ptr, target_ptr))


def process_foreign_key_field(field, model, edges, source_ptr, target_ptr):
    """Process foreign key fields."""
    if not getattr(field, 'concrete', False) or not hasattr(field, 'related_model'):
        return

    rel_type = get_relationship_type(field, model)

    multiplicity = {
                "source": "1..*" if not field.null else "*",
                "target": "1"
            }
    if rel_type in ["composition", "association"]:
        if rel_type == "composition":
            edges.append(create_edge(rel_type, "compose", multiplicity, target_ptr, source_ptr))
        else:
            edges.append(create_edge(rel_type, "connect", multiplicity, source_ptr, target_ptr))


def process_enum_field(field, enum_ptr_map, edges, source_ptr):
    """Process enum fields."""
    enum_ptr = enum_ptr_map.get(field.name)
    if enum_ptr:
        edges.append(create_edge("dependency", "depend",
                                 {"source": "1", "target": "1"}, source_ptr, enum_ptr))


# Fix: Add 2 blank lines before top-level function
def extract_method_dependencies(model, all_models, data):
    try:
        source_ptr = data['model_ptr_map'].get(model)
        if not source_ptr:
            return

        methods = get_model_all_methods(model)
        if methods is None:
            return

        model_names = {m.__name__: m for m in all_models}
        add_method_dependency_edges(model, methods, model_names, data, source_ptr)

    except Exception as outer_e:
        print(f"Unexpected error '{getattr(model, '__name__', str(model))}': {outer_e}")


def add_method_dependency_edges(model, source_code_map, model_names, data, source_ptr):
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
                            f"calls",
                            {"source": "1", "target": "1"},
                            source_ptr,
                            target_ptr
                        ))
                        added_targets.add(other_model_name)
            except Exception as inner_e:
                print(f"Error processing dependency from '{model.__name__}' to '{other_model_name}': {inner_e}")