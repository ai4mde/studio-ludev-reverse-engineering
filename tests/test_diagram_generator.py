import sys
import os
import pytest
import json

# Add the parent directory to sys.path to locate 'scripts' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import the script module
import scripts.extract_to_diagram as extract_module

def test_generate_diagram_json_structure():
    result = extract_module.generate_diagram_json()
    assert isinstance(result, dict)
    assert "diagrams" in result
    assert isinstance(result["diagrams"], list)
    assert len(result["diagrams"]) > 0

def test_nodes_have_required_fields():
    result = extract_module.generate_diagram_json()
    nodes = result["diagrams"][0]["nodes"]
    for node in nodes:
        assert "id" in node
        assert "cls" in node
        assert isinstance(node["cls"]["attributes"], list)
        assert isinstance(node["cls"]["methods"], list)

def test_attributes_have_types():
    result = extract_module.generate_diagram_json()
    nodes = result["diagrams"][0]["nodes"]
    for node in nodes:
        for attr in node["cls"]["attributes"]:
            assert "name" in attr
            assert "type" in attr
            assert isinstance(attr["type"], str)
