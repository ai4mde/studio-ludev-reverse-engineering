from ninja import Router
from django.http import HttpRequest, JsonResponse
from typing import List
from api.model.diagram.functions.extract_to_diagram import generate_diagram_json

# Create a router instance
system = Router()

@system.get("/diagram-json/", response=dict)
def get_diagram_json(request: HttpRequest):
    """
    This view generates and returns the diagram JSON.
    It uses the generate_diagram_json function to create the diagram and return it as a response.
    """
    try:
        # Generate the diagram JSON
        diagram_json = generate_diagram_json()
        return JsonResponse(diagram_json, safe=False)

    except Exception as e:
        # Handle errors and return an error response
        return JsonResponse({"error": str(e)}, status=500)

# Include the router in the module's `__all__`
__all__ = ["system"]
