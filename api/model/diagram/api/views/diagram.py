from typing import List

from diagram.api.schemas import (
    ImportDiagram,
    CreateDiagram,
    FullDiagram,
    ReadDiagram,
    UpdateDiagram,
)
from diagram.models import Diagram
from diagram.api.utils import create_node, create_edge
from metadata.models import System
from django.db import transaction
from ninja import Router

from .node import node
from .edge import edge
from .system import system

diagrams = Router()


@diagrams.get("/", response=List[ReadDiagram])
def list_diagrams(request):
    qs = Diagram.objects.all()
    return qs


@diagrams.get("/{uuid:diagram_id}", response=FullDiagram)
def read_diagram(request, diagram_id):
    return Diagram.objects.get(id=diagram_id)


@diagrams.post("/", response=ReadDiagram)
def create_diagram(request, body: CreateDiagram):
    system = System.objects.get(id=body.system)
    diagram = Diagram.objects.create(
        name=body.name,
        system=system,
        type=body.type,
    )
    return diagram


@diagrams.post("/import", response=FullDiagram)
@transaction.atomic
def import_diagram(request, body: ImportDiagram):
    system = System.objects.get(id=body.system)
    diagram = Diagram.objects.create(
        name=body.name,
        system=system,
        type=body.type,
    )

    # We track all the UUIDs here as we generate new ones,
    # to avoid collisions on import.
    # TODO: See if there is a more elegant way to do this
    nodes = dict()

    for node_in in body.nodes:
        n = create_node(diagram, node_in.cls)
        nodes[node_in.id] = n

    for edge_in in body.edges:
        create_edge(diagram, edge_in.rel, nodes[edge_in.source], nodes[edge_in.target])

    print("imported diagram")

    return diagram


@diagrams.patch("/{uuid:diagram_id}/", response=ReadDiagram)
def update_diagram(request, diagram_id, payload: UpdateDiagram):
    diagram = Diagram.objects.get(id=diagram_id)

    if payload.name:
        diagram.name = payload.name
        diagram.save()

    if payload.description:
        diagram.description = payload.description
        diagram.save()

    return diagram


@diagrams.delete("/{uuid:diagram_id}/")
def delete_diagram(request, diagram_id):
    try:
        diagram = Diagram.objects.get(id=diagram_id)
        diagram.delete()
    except Exception as e:
        raise Exception("Failed to delete diagram, error: " + e)
    return True


@diagrams.post("/{uuid:diagram_id}/auto_layout", response=FullDiagram)
def auto_layout_diagram(request, diagram_id):
    try:
        diagram = Diagram.objects.get(id=diagram_id)
    except Diagram.DoesNotExist:
        return 404

    diagram.auto_layout()
    return diagram


diagrams.add_router("/{uuid:diagram}/node", node, tags=["diagrams"])
diagrams.add_router("/{uuid:diagram}/edge", edge, tags=["diagrams"])
diagrams.add_router("/system/", system, tags=["diagrams"])

__all__ = ["diagrams"]
