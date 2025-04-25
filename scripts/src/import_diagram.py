import requests
from jinja2 import Template
import json
from scripts.src.extract_relationships import generate_diagram_json, json_template

# Assume you have this function from your script that returns the final rendered JSON string
def generate_diagram_json_text():
    # This would be the final dictionary from generate_diagram_json
    diagram_data = generate_diagram_json()
    rendered_json = diagram_data

    return rendered_json

def generate_diagram():
    # Auth token and headers
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDU2NDQ2OTksIm5iZiI6MTc0NTU1ODI5OSwiaXNzIjoidXJuOmFpNG1kZXN0dWRpbyIsImlhdCI6MTc0NTU1ODI5OSwidWlkIjoxfQ.0auQII151cdxV-SHZxYEsZjH0rRdkQ9BQATdO3s3NWg"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Generate the JSON data
    json_payload = generate_diagram_json_text()

    # Convert to JSON-compatible Python dict (if needed)
    try:
        payload = json.loads(json_payload)
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        exit()

    # Make the POST request
    url = "http://api.ai4mde.localhost/api/v1/diagram/import"
    response = requests.post(url, headers=headers, json=payload)

    # Print response
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

if __name__ == "__main__":
    # call the backend api
    generate_diagram()