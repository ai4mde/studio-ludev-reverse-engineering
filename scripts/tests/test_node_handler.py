import pytest
from django.db import models
from unittest.mock import Mock, patch
from scripts.src.utils.node_handler import map_field_type, create_attribute, create_model_node, process_enum_field_node
from scripts.src.utils.django_environment_setup import *

configure_django_settings()


# Fixtures
@pytest.fixture
def mock_enum_field():
    """Create mock enum field"""
    field = Mock()
    field.name = "status"
    field.choices = [
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('P', 'Pending')
    ]
    return field


@pytest.fixture
def mock_model():
    """Create mock Django model"""

    class TestModel(models.Model):
        name = models.CharField(max_length=100)
        status = models.CharField(max_length=1, choices=[
            ('A', 'Active'),
            ('I', 'Inactive')
        ])

        def custom_method(self):
            pass

        class Meta:
            app_label = 'test'

    return TestModel


# Test enum field node processing
def test_process_enum_field_node_new(mock_enum_field):
    """Test processing new enum field node"""
    enum_ptr_map = {}
    node, ref = process_enum_field_node(mock_enum_field, enum_ptr_map)

    assert node is not None
    assert isinstance(node, dict)
    assert node['cls']['name'] == "status"
    assert node['cls']['type'] == "enum"
    assert node['cls']['literals'] == ['A', 'I', 'P']
    assert ref in enum_ptr_map.values()


def test_process_enum_field_node_existing(mock_enum_field):
    """Test processing existing enum field node"""
    existing_ref = "existing-uuid"
    enum_ptr_map = {"status": existing_ref}

    node, ref = process_enum_field_node(mock_enum_field, enum_ptr_map)

    assert node is None
    assert ref == existing_ref


# Test field type mapping
@pytest.mark.parametrize("field_type,expected_type", [
    (models.CharField, "str"),
    (models.TextField, "str"),
    (models.IntegerField, "int"),
    (models.BooleanField, "bool"),
    (models.DateTimeField, "datetime"),
    (models.DateField, "datetime"),
    (models.EmailField, "str"),  # default case
])
def test_map_field_type(field_type, expected_type):
    """Test mapping different field types"""
    field = Mock(spec=field_type)

    with patch('scripts.src.utils.helper.is_enum_field', return_value=False):
        result = map_field_type(field)
        assert result == expected_type


def test_map_field_type_enum():
    """Test enum field type mapping"""
    field = Mock()
    with patch('scripts.src.utils.helper.is_enum_field', return_value=True):
        result = map_field_type(field)
        assert result == "enum"


# Test attribute creation
def test_create_attribute_normal_field():
    """Test creating normal field attribute"""
    field = Mock(spec=models.CharField)
    field.name = "test_field"

    with patch('scripts.src.utils.helper.is_enum_field', return_value=False):
        attribute = create_attribute(field, None)

        assert attribute["name"] == "test_field"
        assert attribute["type"] == "str"
        assert attribute["enum"] is None
        assert attribute["derived"] is False


def test_create_attribute_enum_field():
    """Test creating enum field attribute"""
    field = Mock(spec=models.CharField)
    field.name = "status"
    enum_ref = "enum-uuid"

    with patch('scripts.src.utils.helper.is_enum_field', return_value=True):
        attribute = create_attribute(field, enum_ref)

        assert attribute["name"] == "status"
        assert attribute["type"] == "enum"
        assert attribute["enum"] == enum_ref


# Test model node creation
@pytest.mark.parametrize("custom_methods,attributes", [
    (["method1", "method2"], [{"name": "field1", "type": "str"}]),
    ([], []),
    (["test_method"], [{"name": "field1", "type": "str"}, {"name": "field2", "type": "int"}])
])
def test_create_model_node(custom_methods, attributes):
    """Test creating model node with different method and attribute combinations"""
    model = Mock()
    model.__name__ = "TestModel"
    cls_ptr = "test-cls-ptr"

    with patch('scripts.src.utils.helper.get_custom_methods', return_value=custom_methods):
        node = create_model_node(model, cls_ptr, attributes)

        assert node["id"] == cls_ptr
        assert node["cls"]["name"] == "TestModel"
        assert node["cls"]["type"] == "class"
        assert len(node["cls"]["methods"]) == len(custom_methods)
        assert node["cls"]["attributes"] == attributes


def test_create_model_node_complete(mock_model):
    """Test creating complete model node"""
    cls_ptr = "test-cls-ptr"
    attributes = [
        {
            "name": "name",
            "type": "str",
            "enum": None,
            "derived": False
        },
        {
            "name": "status",
            "type": "enum",
            "enum": "enum-uuid",
            "derived": False
        }
    ]

    with patch('scripts.src.utils.helper.get_custom_methods', return_value=["custom_method"]):
        node = create_model_node(mock_model, cls_ptr, attributes)

        assert node["id"] == cls_ptr
        assert node["cls"]["name"] == "TestModel"
        assert len(node["cls"]["methods"]) == 1
        assert node["cls"]["methods"][0]["name"] == "custom_method"
        assert len(node["cls"]["attributes"]) == len(attributes)