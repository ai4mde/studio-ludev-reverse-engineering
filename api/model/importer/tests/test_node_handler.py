import pytest
from django.db import models
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))
from unittest.mock import Mock, patch
from api.model.importer.src.utils.helper import get_custom_methods
from api.model.importer.src.utils.django_environment_setup import *
from api.model.importer.src.utils.node_handler import map_field_type, create_attribute, create_model_node, process_enum_field_node

# To run this from the parent directory: python -m coverage run --source=scripts.src.utils.node_handler -m pytest -s -v scripts/tests/test_node_handler.py && python -m coverage report -m

# 31/05/2025: Coverage report shows 100% coverage for this file, so no need to add more tests.


#  python -m coverage run --source=scripts.src.utils.node_handler -m pytest -s -v scripts/tests/test_node_handler.py && python -m coverage report -m

configure_mock_django_settings()

# Test the process_enum_field_node function
def test_process_enum_field_node_new_enum():
    """Test processing a new enum field"""
    field = Mock()
    field.name = "status"
    field.choices = [("A", "Active"), ("I", "Inactive")]
    enum_ptr_map = {}

    enum_node, enum_id = process_enum_field_node(field, enum_ptr_map)

    assert enum_node is not None
    assert enum_node["cls"]["name"] == "status"
    assert enum_node["cls"]["type"] == "enum"
    assert enum_node["cls"]["literals"] == ["A", "I"]
    assert enum_id in enum_ptr_map.values()
    assert enum_ptr_map["status"] == enum_id


def test_process_enum_field_node_existing_enum():
    """Test processing an already existing enum field"""
    field = Mock()
    field.name = "status"
    field.choices = [("A", "Active"), ("I", "Inactive")]
    existing_id = "existing-uuid"
    enum_ptr_map = {"status": existing_id}

    enum_node, enum_id = process_enum_field_node(field, enum_ptr_map)

    assert enum_node is None
    assert enum_id == existing_id


# Test the map_field_type function
@pytest.mark.parametrize("field_type,expected_type", [
    (models.CharField(), "str"),
    (models.TextField(), "str"),
    (models.IntegerField(), "int"),
    (models.BooleanField(), "bool"),
    (models.DateTimeField(), "datetime"),
    (models.DateField(), "datetime"),
    (models.FloatField(), "str")  # Default type
])
def test_map_field_type(field_type, expected_type):
    """Test mapping of various field types"""
    assert map_field_type(field_type) == expected_type


def test_map_field_type_enum():
    """Test mapping of enum field type"""
    field = Mock()
    field.choices = [("A", "Active"), ("I", "Inactive")]

    with patch('api.model.model.scripts.src.utils.helper.is_enum_field', return_value=True):
        assert map_field_type(field) == "enum"


# Test the create_attribute function
def test_create_attribute_normal_field():
    """Test creating a normal attribute"""
    field = Mock()
    field.name = "test_field"

    with patch('api.model.model.scripts.src.utils.node_handler.map_field_type', return_value="str"):
        attribute = create_attribute(field, None)

        assert attribute["name"] == "test_field"
        assert attribute["type"] == "str"
        assert attribute["enum"] is None
        assert attribute["derived"] is False
        assert attribute["body"] is None
        assert attribute["description"] is None


def test_create_attribute_enum_field():
    """Test creating an enum attribute"""
    field = Mock()
    field.name = "status"
    enum_ref = "enum-uuid"

    with patch('api.model.model.scripts.src.utils.node_handler.map_field_type', return_value="enum"):
        attribute = create_attribute(field, enum_ref)

        assert attribute["name"] == "status"
        assert attribute["type"] == "enum"
        assert attribute["enum"] == enum_ref


# Test the create_model_node function
def test_create_model_node_empty():
    """Test creating an empty model node"""
    model = Mock()
    model.__name__ = "TestModel"
    cls_ptr = "test-ptr"
    attributes = []

    with patch('api.model.model.scripts.src.utils.helper.get_custom_methods', return_value=[]):
        node = create_model_node(model, cls_ptr, attributes)

        assert node["id"] == cls_ptr
        assert node["cls"]["name"] == "TestModel"
        assert node["cls"]["type"] == "class"
        assert len(node["cls"]["methods"]) == 0
        assert node["cls"]["attributes"] == []



def test_create_model_node_with_methods_and_attributes():
    """Test creating a model node with methods and attributes"""

    # Create a mock class dynamically to simulate a real Django model with methods
    class TestModel:
        def custom_method(self):
            pass


    # Prepare the test input
    model = TestModel
    cls_ptr = "test-ptr"
    attributes = [{"name": "field1", "type": "str"}]
    custom_methods = get_custom_methods(model)  # Extract methods using the actual helper

    with patch('api.model.model.scripts.src.utils.helper.get_custom_methods', return_value=custom_methods):
        node = create_model_node(model, cls_ptr, attributes)

        # Basic structure checks
        assert node["id"] == cls_ptr
        assert node["cls"]["name"] == "TestModel"
        assert isinstance(node["cls"]["methods"], list)
        assert len(node["cls"]["methods"]) > 0, "Method list should not be empty"

        # Check if custom methods are present
        method_names = {method["name"] for method in node["cls"]["methods"]}
        assert "custom_method" in method_names

        # Attributes check
        assert node["cls"]["attributes"] == attributes



def test_create_model_node_structure():
    """Test the complete structure of a model node"""
    model = Mock()
    model.__name__ = "TestModel"
    cls_ptr = "test-ptr"
    attributes = []

    node = create_model_node(model, cls_ptr, attributes)

    assert "id" in node
    assert "cls" in node
    assert "data" in node
    assert "cls_ptr" in node
    assert "position" in node["data"]
    assert "x" in node["data"]["position"]
    assert "y" in node["data"]["position"]
    assert node["cls"]["leaf"] is False
    assert node["cls"]["abstract"] is False
    assert node["cls"]["namespace"] == ""
