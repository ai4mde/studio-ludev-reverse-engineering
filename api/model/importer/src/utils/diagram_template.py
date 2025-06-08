from jinja2 import Template

diagram_template = """
{
    "id": "{{ diagram_id }}",
    "name": "Diagram",
    "type": "classes",
    "edges": [
        {% for edge in edges %}
        {
            "id": "{{ edge.id }}",
            "rel": {
                "type": "{{ edge.rel.type }}",
                "label": "{{ edge.rel.label }}",
                "multiplicity": {
                    "source": "{{ edge.rel.multiplicity.source }}",
                    "target": "{{ edge.rel.multiplicity.target }}"
                }
            },
            "data": {},
            "rel_ptr": "{{ edge.rel_ptr }}",
            "source_ptr": "{{ edge.source_ptr }}",
            "target_ptr": "{{ edge.target_ptr }}"
        }
        {% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "nodes": [
        {% for node in nodes %}
        {
          "id": "{{ node.id }}",
          "cls": {
            {% if node.cls.type == 'enum' %}
            "name": "{{ node.cls.name }}",
            "type": "enum",
            "literals": {{ node.cls.literals | tojson }},
            "namespace": "{{ node.cls.namespace }}"
            {% else %}
            "leaf": {{ node.cls.leaf | lower }},
            "name": "{{ node.cls.name }}",
            "type": "class",
            "methods": [
              {% for method in node.cls.methods %}
              {
                "body": "{{ method.body }}",
                "name": "{{ method.name }}",
                "type": "{{ method.type }}",
                "description": "{{ method.description }}"
              }
              {% if not loop.last %},{% endif %}
              {% endfor %}
            ],
            "abstract": {{ node.cls.abstract | lower}},
            "namespace": "{{ node.cls.namespace }}",
            "attributes": [
              {% for attribute in node.cls.attributes %}
              {
                "body": "{{ attribute.body }}",
                "enum": "{{ attribute.enum }}",
                "name": "{{ attribute.name }}",
                "type": "{{ attribute.type }}",
                "derived": "{{ attribute.derived | lower }}",
                "description": "{{ attribute.description }}"
              }
              {% if not loop.last %},{% endif %}
              {% endfor %}
            ]
            {% endif %}
          },
          "data": {
            "position": {
              "x": {{ node.data.position.x }},
              "y": {{ node.data.position.y }}
            }
          },
          "cls_ptr": "{{ node.cls_ptr }}"
        }
        {% if not loop.last %},{% endif %}
        {% endfor %}
    ],
    "system": "{{ system_id }}",
    "project": "{{ project_id }}",
    "description": ""
}
"""

# create the template object
diagram_template_obj = Template(diagram_template)
