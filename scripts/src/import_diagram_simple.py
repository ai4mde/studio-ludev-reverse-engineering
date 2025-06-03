import requests
import json
import argparse
import sys
import uuid


def call_endpoints_to_import_diagram_simple(to_show_method_dependency=True):
    """
    A simplified version for testing API integration without Django dependencies.
    
    Args:
        to_show_method_dependency (bool): Whether to include method dependencies in the diagram
    """
    print(f"Simplified import diagram execution started")
    print(f"Method dependency setting: {to_show_method_dependency}")
    
    # Step 1: Obtain authentication token
    # Use localhost when running inside the API container
    auth_url = "http://localhost:8000/api/v1/auth/token"
    auth_payload = {
        "username": "admin",
        "password": "sequoias"
    }

    try:
        auth_response = requests.post(auth_url, json=auth_payload)
        auth_response.raise_for_status()
        print("Authentication successful")
    except requests.exceptions.RequestException as e:
        print(f"Authentication request failed: {e}")
        return False

    token = auth_response.json().get('token')

    # Set headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Create a project
    project_payload = {
        "name": f"Test Project (Method Deps: {to_show_method_dependency})",
        "description": "Test project created by simplified import script"
    }
    
    try:
        project_response = requests.post("http://localhost:8000/api/v1/metadata/projects/", 
                                       headers=headers, json=project_payload)
        if project_response.status_code != 200:
            print(f"Failed to create project: {project_response.status_code} - {project_response.text}")
            return False
        
        project_id = project_response.json().get('id')
        print(f"Project created with ID: {project_id}")
    except Exception as e:
        print(f"Error creating project: {e}")
        return False

    # Step 3: Create a system
    system_payload = {
        "name": f"Test System (Method Deps: {to_show_method_dependency})",
        "description": "Test system created by simplified import script",
        "project": project_id
    }
    
    try:
        system_response = requests.post("http://localhost:8000/api/v1/metadata/systems/", 
                                      headers=headers, json=system_payload)
        if system_response.status_code != 200:
            print(f"Failed to create system: {system_response.status_code} - {system_response.text}")
            return False
        
        system_id = system_response.json().get('id')
        print(f"System created with ID: {system_id}")
    except Exception as e:
        print(f"Error creating system: {e}")
        return False

    # Generate UUIDs for the test diagram
    diagram_id = str(uuid.uuid4())
    node_id = str(uuid.uuid4())
    cls_ptr = str(uuid.uuid4())

    # Step 4: Create a test diagram
    dummy_payload = {
        "id": diagram_id,
        "name": f"Test Diagram (Method Deps: {to_show_method_dependency})",
        "type": "classes",
        "nodes": [
            {
                "id": node_id,
                "cls": {
                    "leaf": False,
                    "name": "TestClass",
                    "type": "class",
                    "methods": [
                        {
                            "body": "",
                            "name": "test_method",
                            "type": "str",
                            "description": f"Method dependency demo: {to_show_method_dependency}"
                        }
                    ] if to_show_method_dependency else [],
                    "abstract": False,
                    "namespace": "",
                    "attributes": [
                        {
                            "body": None,
                            "enum": None,
                            "name": "test_field",
                            "type": "str",
                            "derived": False,
                            "description": None
                        }
                    ]
                },
                "data": {
                    "position": {"x": 0, "y": 0}
                },
                "cls_ptr": cls_ptr
            }
        ],
        "edges": [],
        "system": system_id,
        "project": project_id,
        "description": f"Test diagram created by simplified import script with method dependency: {to_show_method_dependency}"
    }

    # Step 5: Import the test diagram
    import_url = "http://localhost:8000/api/v1/diagram/import"
    try:
        import_response = requests.post(import_url, headers=headers, json=dummy_payload)
        print(f"Import status code: {import_response.status_code}")

        if import_response.status_code == 200:
            response_data = import_response.json()
            print(f"Import successful: {response_data}")
            
            # Step 6: Apply auto-layout
            diagram_id_returned = response_data.get('id')
            if diagram_id_returned:
                layout_url = f"http://localhost:8000/api/v1/diagram/{diagram_id_returned}/auto_layout"
                try:
                    layout_response = requests.post(layout_url, headers=headers)
                    print(f"Auto-layout status code: {layout_response.status_code}")
                    print(f"Test diagram created successfully with ID: {diagram_id_returned}")
                    return True
                except requests.exceptions.RequestException as e:
                    print(f"Auto-layout request failed: {e}")
                    return False
            else:
                print("No diagram ID returned")
                return False
        else:
            print(f"Import failed with status: {import_response.status_code}")
            print(f"Response: {import_response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Import request failed: {e}")
        return False


def main():
    """
    Main function that handles command line arguments and calls the import diagram function.
    """
    parser = argparse.ArgumentParser(description='Simple test for import diagram API')
    parser.add_argument(
        '--include-method-dependency', 
        action='store_true', 
        default=True,
        help='Include method dependencies in the diagram (default: True)'
    )
    parser.add_argument(
        '--no-method-dependency', 
        action='store_true',
        help='Exclude method dependencies from the diagram'
    )
    
    args = parser.parse_args()
    
    # Handle the logic for method dependency
    if args.no_method_dependency:
        to_show_method_dependency = False
    else:
        to_show_method_dependency = args.include_method_dependency
    
    print(f"Starting simplified import diagram execution")
    print(f"Method dependency setting: {to_show_method_dependency}")
    
    success = call_endpoints_to_import_diagram_simple(to_show_method_dependency)
    
    if success:
        print("Simplified import diagram completed successfully")
        sys.exit(0)
    else:
        print("Simplified import diagram failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 