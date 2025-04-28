import requests
import json
from scripts.src.extract_relationships import generate_diagram_json


def call_endpoints_to_import_diagram():  # noqa: C901
    """
    Generate a diagram including authentication, import, and auto-layout.
    """
    # Step 1: Obtain authentication token
    auth_url = "http://api.ai4mde.localhost/api/v1/auth/token"
    auth_payload = {
        "username": "admin",
        "password": "sequoias"
    }

    try:
        auth_response = requests.post(auth_url, json=auth_payload)
        auth_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Authentication request failed: {e}")
        return

    token = auth_response.json().get('token')
    print("Authentication successful")

    # Set headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Generate and import the diagram
    try:
        json_payload = generate_diagram_json()
        payload = json.loads(json_payload)

        # Debug information
        print("Payload sent:", json.dumps(payload, indent=2))

    except json.JSONDecodeError as e:
        print(f"Invalid generated JSON: {e}")
        print("Original payload:", json_payload)
        return
    except Exception as e:
        print(f"Error generating diagram data: {e}")
        return

    import_url = "http://api.ai4mde.localhost/api/v1/diagram/import"
    try:
        import_response = requests.post(import_url, headers=headers, json=payload)
        print(f"Import status code: {import_response.status_code}")

        # Print raw response content
        print(f"Raw response content: {import_response.text}")

        if import_response.status_code == 500:
            print("Server internal error, please check the server logs")
            return

        if not import_response.text:
            print("Server returned empty response")
            return

        response_data = import_response.json()
        print(f"Import response: {response_data}")

    except requests.exceptions.RequestException as e:
        print(f"Import request failed: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Unable to parse import response: {e}")
        print(f"Raw response content: {import_response.text}")
        return

    # Step 3: Apply auto-layout only when import is successful
    if import_response.status_code == 200:
        diagram_id = response_data.get('id')
        if not diagram_id:
            print("Diagram ID not found in the response")
            return

        layout_url = f"http://api.ai4mde.localhost/api/v1/diagram/{diagram_id}/auto_layout"
        try:
            layout_response = requests.post(layout_url, headers=headers)
            print(f"Auto-layout status code: {layout_response.status_code}")

            if layout_response.text:
                print(f"Auto-layout response: {layout_response.json()}")
            else:
                print("Auto-layout returned empty response")

        except requests.exceptions.RequestException as e:
            print(f"Auto-layout request failed: {e}")


if __name__ == "__main__":
    call_endpoints_to_import_diagram()
