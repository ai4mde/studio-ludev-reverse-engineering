from jinja2 import Template

def render_diagram_json(template_str, diagram_id, system_id, project_id, nodes, edges):
    template = Template(template_str)
    return template.render(
        diagram_id=diagram_id,
        system_id=system_id,
        project_id=project_id,
        nodes=nodes,
        edges=edges
    )
