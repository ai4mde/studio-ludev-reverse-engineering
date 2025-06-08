import sys
import uuid
import argparse
from django.apps import apps
from utils.diagram_template import diagram_template_obj
from utils.node_handler import process_enum_field_node, create_attribute, create_model_node
from utils.relationship_handler import extract_method_dependencies, process_model_relationships
from utils.helper import is_enum_field, collect_all_valid_models, initialize_model_ptr_map, verify_data_integrity
from utils.django_environment_setup import configure_django_settings


# Functions related to diagram initialization
def initialize_diagram_data(project_id, system_id):
    """Initialize the basic data needed for the diagram"""
    return {
        'diagram_id': str(uuid.uuid4()),
        'project_id': project_id,
        'system_id': system_id,
        'nodes': [],
        'edges': [],
        'model_ptr_map': {},
        'enum_ptr_map': {}
    }


def process_model(model, data, app_config, is_show_method_dependency):
    """Process a single model"""
    try:
        cls_ptr = data['model_ptr_map'][model]  # Use existing UUID
        # print(f"Processing model: {model.__name__}")
        # print(f"Model ID: {cls_ptr}")

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
                                except Exception:
                                    # print(f"Error processing enum field: {field.name}, error: {str(e)}")
                                    continue

                            attributes.append(create_attribute(field, enum_ref))
                    except Exception:
                        # print(f"Error processing field: {field.name}, error: {str(e)}")
                        continue

                node = create_model_node(model, cls_ptr, attributes)
                data['nodes'].append(node)
            except Exception as e:
                sys.exit(f"Error creating model node: {model.__name__}, error: {str(e)}")

        if is_show_method_dependency:
            try:
                extract_method_dependencies(model, app_config.get_models(), data)
            except Exception as e:
                sys.exit(f"Error extracting method dependencies: {model.__name__}, error: {str(e)}")

        try:
            process_model_relationships(model, data['model_ptr_map'], data['enum_ptr_map'], data['edges'])
        except Exception as e:
            sys.exit(f"Error processing model relationships: {model.__name__}, error: {str(e)}")

    except Exception as e:
        sys.exit(f"Error processing model: {model.__name__ if model else 'Unknown'}, error: {str(e)}")


def generate_diagram_json(project_id, system_id, show_method_dependencies):
    """Main function to generate diagram JSON"""
    data = initialize_diagram_data(project_id, system_id)

    for app_config in apps.get_app_configs():
        if app_config.name == 'shared_models':
            # print(f"Extracting models from: {app_config.verbose_name}")

            # First, collect all models (including parent classes)
            all_models = collect_all_valid_models(app_config)

            # Initialize model_ptr_map for all models
            data['model_ptr_map'] = initialize_model_ptr_map(all_models)

            # Process all models
            for model in app_config.get_models():
                process_model(model, data, app_config, show_method_dependencies)

    verify_data_integrity(data)
    rendered = diagram_template_obj.render(
        diagram_id=data['diagram_id'],
        project_id=data['project_id'],
        system_id=data['system_id'],
        nodes=data['nodes'],
        edges=data['edges']
    )

    return rendered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", default=".", help="starting path")
    parser.add_argument("--project_id", "-pid", help="id of the project the diagram needs to be added to")
    parser.add_argument("--system_id", "-sid", help="id of the system the diagram needs to be added to")
    parser.add_argument("--method_dependencies", "-md", help="if method dependencies should be included or not")
    args = parser.parse_args()

    configure_django_settings(args.path)
    diagram = generate_diagram_json(args.project_id, args.system_id, bool(args.method_dependencies))

    print(diagram)


if __name__ == "__main__":
    main()
