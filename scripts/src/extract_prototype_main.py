import os
import sys
import uuid
import django
from django.apps import apps
from django.conf import settings
from scripts.src.utils.diagram_template import diagram_template_obj
from scripts.src.utils.node_handler import process_enum_field_node, create_attribute, create_model_node
from scripts.src.utils.relationship_handler import extract_method_dependencies, process_model_relationships
from scripts.src.utils.helper import is_enum_field, collect_all_valid_models, initialize_model_ptr_map, verify_data_integrity
from scripts.src.utils.django_environment_setup import configure_django_settings


configure_django_settings()


# Functions related to diagram initialization
def initialize_diagram_data():
    """Initialize the basic data needed for the diagram"""
    return {
        'diagram_id': str(uuid.uuid4()),
        'system_id': "a8465cb2-2df2-4a52-9946-6d762ebfd36f",
        'project_id': "",
        'nodes': [],
        'edges': [],
        'model_ptr_map': {},
        'enum_ptr_map': {}
    }


def process_model(model, data, app_config, is_show_method_dependency):
    """Process a single model"""
    try:
        cls_ptr = data['model_ptr_map'][model]  # Use existing UUID
        print(f"Processing model: {model.__name__}")
        print(f"Model ID: {cls_ptr}")

        # Only create a node if it hasn't been processed yet
        if not any(node['id'] == cls_ptr for node in data['nodes']):
            try:
                attributes = []
                for field in model._meta.get_fields():
                    try:
                        if not field.is_relation:
                            enum_ref = None
                            if is_enum_field(field):
                                try:
                                    enum_node, enum_ref = process_enum_field_node(field, data['enum_ptr_map'])
                                    if enum_node:
                                        data['nodes'].append(enum_node)
                                except Exception as e:
                                    print(f"Error processing enum field: {field.name}, error: {str(e)}")
                                    continue

                            attributes.append(create_attribute(field, enum_ref))
                    except Exception as e:
                        print(f"Error processing field: {field.name}, error: {str(e)}")
                        continue

                node = create_model_node(model, cls_ptr, attributes)
                data['nodes'].append(node)
            except Exception as e:
                print(f"Error creating model node: {model.__name__}, error: {str(e)}")
                return

        if is_show_method_dependency:
            try:
                extract_method_dependencies(model, app_config.get_models(), data)
            except Exception as e:
                print(f"Error extracting method dependencies: {model.__name__}, error: {str(e)}")

        try:
            process_model_relationships(model, data['model_ptr_map'], data['enum_ptr_map'], data['edges'])
        except Exception as e:
            print(f"Error processing model relationships: {model.__name__}, error: {str(e)}")

    except Exception as e:
        print(f"Error processing model: {model.__name__ if model else 'Unknown'}, error: {str(e)}")


def generate_diagram_json(show_method_dependency):
    """Main function to generate diagram JSON"""
    data = initialize_diagram_data()

    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            print(f"Extracting models from: {app_config.verbose_name}")

            # First, collect all models (including parent classes)
            all_models = collect_all_valid_models(app_config)

            # Initialize model_ptr_map for all models
            data['model_ptr_map'] = initialize_model_ptr_map(all_models)

            # Process all models
            for model in app_config.get_models():
                process_model(model, data, app_config, show_method_dependency)

    verify_data_integrity(data)
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