json_template = """
{
    "diagrams": [
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
                        "leaf": false,
                        "name": "{{ node.cls.name }}",
                        "type": "class",
                        "methods": [
                            {% for method in node.cls.methods %}
                            {
                                "body": "",
                                "name": "{{ method.name }}",
                                "type": "{{ method.type }}",
                                "description": ""
                            }
                            {% if not loop.last %},{% endif %}
                            {% endfor %}
                        ],
                        "abstract": false,
                        "namespace": "",
                        "attributes": [
                            {% for attribute in node.cls.attributes %}
                            {
                                "body": null,
                                "enum": null,
                                "name": "{{ attribute.name }}",
                                "type": "{{ attribute.type }}",
                                "derived": false,
                                "description": null
                            }
                            {% if not loop.last %},{% endif %}
                            {% endfor %}
                        ]
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
    ]
}
"""
