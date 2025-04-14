from core.django_setup import setup_django
from core.model_loader import load_shared_models
from generator.diagram_builder import build_diagram_models
from generator.jinja_renderer import render_diagram_json
import uuid

# --- Hardcoded Config (you can change this)
PROJECT_PATH = "../test_prototype/generated_prototypes/c79c758a-d2c5-4e2c-bf71-eadcaf769299/shop"
SETTINGS_MODULE = "shop.settings"
SYSTEM_ID = "c79c758a-d2c5-4e2c-bf71-eadcaf769299"
PROJECT_ID = "99fc3c09-07bc-43d2-bf59-429f99a35839"

# --- Jinja Template (import or inline for testing)
from api.jinja_template import json_template

def test_generate_diagram():
    print("[1] Setting up Django...")
    setup_django(PROJECT_PATH, SETTINGS_MODULE)

    print("[2] Loading models from 'shared_models'...")
    models = load_shared_models()
    assert models, "No models found in 'shared_models' app."

    print(f"     Loaded {len(models)} models.")

    print("[3] Building nodes and edges...")
    nodes, edges = build_diagram_models(models)

    print(f"     Built {len(nodes)} nodes and {len(edges)} edges.")

    print("[4] Rendering diagram JSON...")
    rendered_json = render_diagram_json(
        json_template,
        diagram_id=str(uuid.uuid4()),
        system_id=SYSTEM_ID,
        project_id=PROJECT_ID,
        nodes=nodes,
        edges=edges
    )

    print("[5]  Render complete. Diagram JSON preview:\n")
    print(rendered_json[:1000] + "\n...\n")  # Print only first 1000 chars for brevity

if __name__ == "__main__":
    test_generate_diagram()
