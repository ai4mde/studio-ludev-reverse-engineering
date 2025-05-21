import inspect
import uuid
import pytest
from django.db import models
from django.apps import AppConfig, apps
from unittest.mock import Mock
from scripts.src.utils.helper import (
    collect_all_valid_models, is_enum_field, get_model_all_methods,
    verify_data_integrity, initialize_model_ptr_map, get_custom_methods, is_method_without_args
)
from scripts.src.utils.django_environment_setup import *

configure_django_settings()

# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def mock_enum_field():
    """Create mock enum field"""
    field = Mock()
    field.choices = [('A', 'Active'), ('I', 'Inactive')]
    return field


@pytest.fixture
def mock_app_config():
    """Create mock AppConfig with models"""
    name_suffix = uuid.uuid4().hex[:6]
    app_label = 'test'

    class BaseModel(models.Model):
        class Meta:
            app_label = 'test_app'


    class TestModel(BaseModel):
        class Meta:
            app_label = 'test_app'


    BaseModel.__name__ = f"BaseModel{name_suffix}"
    TestModel.__name__ = f"TestModel{name_suffix}"

    for model in [BaseModel, TestModel]:
        try:
            apps.get_model(app_label, model.__name__)
        except LookupError:
            apps.register_model(app_label, model)

    config = Mock(spec=AppConfig)
    config.get_models.return_value = [TestModel]
    return config, TestModel, BaseModel



@pytest.fixture
def test_model_with_methods():
    """Dynamically create test model with methods"""
    name = f"TestModel{uuid.uuid4().hex[:6]}"

    class Meta:
        app_label = 'test_exmaple'

    attrs = {
        '__module__': 'test',
        'Meta': Meta,
        'custom_method': lambda self: None,
        'method_with_args': lambda self, arg1: None,
        '_private_method': lambda self: None,
        'save': lambda self: None,
    }

    model = type(name, (models.Model,), attrs)
    apps.register_model('test', model)
    return model


@pytest.fixture
def mock_data():
    """Create mock graph data"""
    return {
        'nodes': [
            {'id': 'node1'},
            {'id': 'node2'}
        ],
        'edges': [
            {
                'source_ptr': 'node1',
                'target_ptr': 'node2'
            },
            {
                'source_ptr': 'node2',
                'target_ptr': 'node3'  # Non-existent node
            }
        ]
    }

# -------------------------
# Tests
# -------------------------

# Enum field checking
def test_is_enum_field_valid(mock_enum_field):
    assert is_enum_field(mock_enum_field) is True


def test_is_enum_field_invalid():
    """Test invalid enum field scenarios"""
    fieldinsp = Mock()

    # Test when choices attribute is None
    fieldinsp.choices = None
    assert is_enum_field(fieldinsp) is False

    # Test empty list case
    fieldinsp.choices = []
    assert is_enum_field(fieldinsp) is False

    # Test invalid choice format
    fieldinsp.choices = [('A', 'Active'), ([], 'Invalid')]
    assert is_enum_field(fieldinsp) is False

    # Test malformed choices
    fieldinsp.choices = [None]
    assert is_enum_field(fieldinsp) is False

    # Test non-binary tuple choices
    fieldinsp.choices = [('A',)]
    assert is_enum_field(fieldinsp) is False


# Model collection
def test_collect_all_valid_models(mock_app_config):
    config, test_model, parent_model = mock_app_config
    models = collect_all_valid_models(config)

    assert len(models) == 2
    assert test_model in models
    assert parent_model in models


def test_collect_all_valid_models_with_django_parent():
    class TestModel():
        class Meta:
            app_label = 'test'

    config = Mock(spec=AppConfig)
    config.get_models.return_value = [TestModel]

    models = collect_all_valid_models(config)
    assert len(models) == 1
    assert TestModel in models


# Method retrieval
def test_get_model_all_methods(test_model_with_methods):
    methods = get_model_all_methods(test_model_with_methods)

    assert isinstance(methods, dict)
    assert 'custom_method' in methods
    assert 'method_with_args' in methods
    assert '_private_method' in methods


def test_get_model_all_methods_error(monkeypatch):
    model = Mock()
    model.__name__ = "TestModel"

    def fake_getmembers(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr(inspect, "getmembers", fake_getmembers)
    result = get_model_all_methods(model)
    assert result is None


# Pointer map
def test_initialize_model_ptr_map():
    models = {Mock(), Mock(), Mock()}
    ptr_map = initialize_model_ptr_map(models)

    assert len(ptr_map) == len(models)
    assert all(isinstance(ptr, str) for ptr in ptr_map.values())
    assert len(set(ptr_map.values())) == len(models)


# Data integrity check
def test_verify_data_integrity(mock_data, capsys):
    verify_data_integrity(mock_data)
    captured = capsys.readouterr()

    assert "Warning: Target node not found node3" in captured.out
    assert "Warning: Source node not found" not in captured.out


# Custom method filtering
def test_get_custom_methods(test_model_with_methods):
    custom_methods = get_custom_methods(test_model_with_methods)

    assert 'custom_method' in custom_methods
    assert 'method_with_args' not in custom_methods
    assert '_private_method' not in custom_methods
    assert 'save' not in custom_methods


# Method param checking
@pytest.mark.parametrize("func,expected", [
    (lambda self: None, True),
    (lambda self, arg: None, False),
    (lambda: None, False),
    (lambda self, *args: None, False),
    ("not_a_function", False)
])
def test_is_method_without_args(func, expected):
    assert is_method_without_args(func) == expected
