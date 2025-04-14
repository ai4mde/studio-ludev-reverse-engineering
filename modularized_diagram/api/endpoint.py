from ninja import Router
from django.http import JsonResponse
from core.django_setup import setup_django
from core.model_loader import load_shared_models
from generator.diagram_builder import build_diagram_models
from generator.jinja_renderer import render_diagram_json
from .jinja_template import json_template  # separa el string grande

router = Router()

@router.get("/diagram-json/")
def get_diagram_json(request):
    try:
        setup_django("../test_prototype/generated_prototypes/c79c758a-d2c5-4e2c-bf71-eadcaf769299/shop", "shop.settings")
        models = load_shared_models()
        nodes, edges = build_diagram_models(models)
        json_data = render_diagram_json(
            json_template,
            diagram_id="some-uuid",  # puedes generar con uuid.uuid4()
            system_id="c79c758a-d2c5-4e2c-bf71-eadcaf769299",
            project_id="99fc3c09-07bc-43d2-bf59-429f99a35839",
            nodes=nodes,
            edges=edges
        )
        return JsonResponse(json_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
