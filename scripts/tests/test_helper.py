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

import os
print(">> CURRENT WORKING DIRECTORY:", os.getcwd())
import scripts.src.utils.helper as helper
print(">> TESTS IMPORTING HELPER FROM:", helper.__file__)

# python -m coverage run --source=scripts.src.utils.helper -m pytest -s -v scripts/tests/test_helper.py && python -m coverage report -m

# 31/05/2025: Coverage report shows 100% coverage for this file, so no need to add more tests.

configure_mock_django_settings()

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

    def custom_method(self): pass
    def method_with_args(self, arg1): pass
    def _private_method(self): pass
    def save(self): pass

    attrs = {
        '__module__': 'test',
        'Meta': Meta,
        'custom_method': custom_method,
        'method_with_args': method_with_args,
        '_private_method': _private_method,
        'save': save,
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

def test_is_enum_field_valid(mock_enum_field):
    assert is_enum_field(mock_enum_field) is True

def test_is_enum_field_invalid():
    fieldinsp = Mock()
    fieldinsp.choices = None
    assert is_enum_field(fieldinsp) is False
    fieldinsp.choices = []
    assert is_enum_field(fieldinsp) is False
    fieldinsp.choices = [('A', 'Active'), ([], 'Invalid')]
    assert is_enum_field(fieldinsp) is False
    fieldinsp.choices = [None]
    assert is_enum_field(fieldinsp) is False
    fieldinsp.choices = [('A',)]
    assert is_enum_field(fieldinsp) is False

def test_is_enum_field_exception():
    class WeirdField:
        choices = [object()]
    assert is_enum_field(WeirdField()) is False

    class WeirdField2:
        choices = [()]
    assert is_enum_field(WeirdField2()) is False

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

def test_get_model_all_methods_getsource_error(monkeypatch):
    class Dummy:
        def foo(self): pass

    def fake_getsource(obj):
        raise Exception("Source error")
    monkeypatch.setattr(inspect, "getsource", fake_getsource)
    result = get_model_all_methods(Dummy)
    assert result is None

def test_initialize_model_ptr_map():
    models = {Mock(), Mock(), Mock()}
    ptr_map = initialize_model_ptr_map(models)
    assert len(ptr_map) == len(models)
    assert all(isinstance(ptr, str) for ptr in ptr_map.values())
    assert len(set(ptr_map.values())) == len(models)

def test_verify_data_integrity(mock_data, capsys):
    verify_data_integrity(mock_data)
    captured = capsys.readouterr()
    assert "Warning: Target node not found node3" in captured.out
    assert "Warning: Source node not found" not in captured.out

def test_get_custom_methods(test_model_with_methods):
    custom_methods = get_custom_methods(test_model_with_methods)
    assert 'custom_method' in custom_methods
    assert 'method_with_args' not in custom_methods
    assert '_private_method' not in custom_methods
    assert 'save' not in custom_methods

def test_get_custom_methods_covers_line80():
    class SimpleModel(models.Model):
        class Meta:
            app_label = 'test'
        def custom_method(self):
            pass
        def not_custom(self, x):
            pass

    result = get_custom_methods(SimpleModel)
    assert 'custom_method' in result
    assert 'not_custom' not in result

@pytest.mark.parametrize("func,expected", [
    (lambda self: None, True),
    (lambda self, arg: None, False),
    (lambda: None, False),
    (lambda self, *args: None, False),
    ("not_a_function", False)
])
def test_is_method_without_args(func, expected):
    assert is_method_without_args(func) == expected

def test_get_custom_methods_explicit_line80():
    class Plain:
        def custom(self): pass
    found = get_custom_methods(Plain)
    assert 'custom' in found

def test_get_custom_methods_explicit_line80_false():
    class Plain:
        def custom(self, arg): pass
    found = get_custom_methods(Plain)
    assert 'custom' not in found

def test_is_method_without_args_signature_exception(monkeypatch):
    def bad_func():
        pass
    monkeypatch.setattr(inspect, "signature", lambda f: (_ for _ in ()).throw(ValueError("No signature!")))
    assert is_method_without_args(bad_func) is False

def test_is_enum_field_indexerror():
    # Create a tuple subclass whose __getitem__ always raises IndexError
    class BadTuple(tuple):
        def __getitem__(self, idx):
            raise IndexError("broken")

    class F:
        choices = [BadTuple(('A', 'B'))]
    assert is_enum_field(F()) is False  # triggers the except → lines 29–30

def test_verify_data_integrity_source_missing(capsys):
    data = {
        'nodes': [{'id': 'n1'}],
        'edges': [
            {'source_ptr': 'n2', 'target_ptr': 'n1'}  # source missing, target OK
        ]
    }
    verify_data_integrity(data)
    out = capsys.readouterr().out
    assert "Warning: Source node not found n2" in out
    assert "Warning: Target node not found" not in out
