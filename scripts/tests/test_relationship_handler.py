import uuid
import pytest
from unittest.mock import patch, Mock
from django.db import models
from django.test.utils import isolate_apps
from scripts.src.utils.relationship_handler import (
    process_field_relationships,
    get_relationship_type,
    extract_method_dependencies,
    process_many_to_many_field,
    create_edge,
    process_inheritance_relationships
)
from scripts.src.utils.django_environment_setup import *

configure_mock_django_settings()

# --------- Fixtures ---------

@pytest.fixture
@isolate_apps("test")
def model_setup():
    class TestParentModel(models.Model):
        class Meta:
            app_label = 'test'

    class TestChildModel(TestParentModel):
        name = models.CharField(max_length=100)
        parent = models.ForeignKey(TestParentModel, on_delete=models.CASCADE, related_name='children')

        class Meta:
            app_label = 'test'

    return {
        'parent_model': TestParentModel,
        'child_model': TestChildModel,
        'model_ptr_map': {
            TestParentModel: str(uuid.uuid4()),
            TestChildModel: str(uuid.uuid4())
        },
        'enum_ptr_map': {},
        'edges': []
    }


@pytest.fixture
def mock_uuid():
    with patch('uuid.uuid4') as mock:
        mock.return_value = "test-uuid"
        yield mock


@pytest.fixture
@isolate_apps("test")
def dependency_setup():
    class ModelA(models.Model):
        class Meta:
            app_label = 'test'

        def method_a(self):
            return "ModelB"

    class ModelB(models.Model):
        class Meta:
            app_label = 'test'

    return {
        'model_a': ModelA,
        'model_b': ModelB,
        'data': {
            'model_ptr_map': {
                ModelA: str(uuid.uuid4()),
                ModelB: str(uuid.uuid4())
            },
            'edges': []
        }
    }

# --------- Unit Tests ---------

def test_create_edge_with_valid_inputs():
    source_ptr = str(uuid.uuid4())
    target_ptr = str(uuid.uuid4())

    edge = create_edge("association", "connect",
                       {"source": "1", "target": "*"},
                       source_ptr, target_ptr)

    assert edge is not None
    assert edge["rel"]["type"] == "association"
    assert edge["rel"]["label"] == "connect"
    assert edge["source_ptr"] == source_ptr
    assert edge["target_ptr"] == target_ptr


def test_create_edge_with_invalid_inputs():
    edge = create_edge("association", "connect",
                       {"source": "1", "target": "*"},
                       None, None)
    assert edge is None


def test_process_inheritance_relationships(model_setup):
    source_ptr = model_setup['model_ptr_map'][model_setup['child_model']]

    inherited_fields = process_inheritance_relationships(
        model_setup['child_model'],
        model_setup['model_ptr_map'],
        model_setup['edges'],
        source_ptr
    )

    assert isinstance(inherited_fields, set)
    assert len(model_setup['edges']) == 1
    edge = model_setup['edges'][0]
    assert edge["rel"]["type"] == "generalization"
    assert edge["rel"]["label"] == "inherits"


def test_process_field_relationships(model_setup):
    source_ptr = model_setup['model_ptr_map'][model_setup['child_model']]

    process_field_relationships(
        model_setup['child_model'],
        model_setup['model_ptr_map'],
        model_setup['enum_ptr_map'],
        model_setup['edges'],
        source_ptr
    )

    edges = [e for e in model_setup['edges']
             if e["rel"]["type"] in ["composition", "association", "generalization"]]
    assert len(edges) > 0


@pytest.mark.parametrize("method_code,expected_edges", [
    ('def method_a(self):\n    return "ModelB"', 1),
])
def test_extract_method_dependencies(dependency_setup, method_code, expected_edges):
    with patch('scripts.src.utils.helper.get_model_all_methods') as mock_get_methods:
        mock_get_methods.return_value = {'method_a': method_code}

        extract_method_dependencies(
            dependency_setup['model_a'],
            [dependency_setup['model_a'], dependency_setup['model_b']],
            dependency_setup['data']
        )

        dependency_edges = [e for e in dependency_setup['data']['edges']
                            if e["rel"]["type"] == "dependency"]
        assert len(dependency_edges) == expected_edges
        if expected_edges > 0:
            assert dependency_edges[0]["rel"]["label"].startswith("calls")


@pytest.mark.parametrize("method_code,expected_edges", [
    ('def method_a(self):\n    return "Other"', 0),
])
def test_extract_withpout_model_method_dependencies(dependency_setup, method_code, expected_edges):
    with patch('scripts.src.utils.helper.get_model_all_methods') as mock_get_methods:
        mock_get_methods.return_value = {'method_b': method_code}

        extract_method_dependencies(
            dependency_setup['model_b'],
            [dependency_setup['model_b'], dependency_setup['model_b']],
            dependency_setup['data']
        )

        dependency_edges = [e for e in dependency_setup['data']['edges']
                            if e["rel"]["type"] == "dependency"]
        assert len(dependency_edges) == expected_edges


def test_relationship_type_detection(model_setup):
    field = model_setup['child_model']._meta.get_field('parent')
    rel_type = get_relationship_type(field, model_setup['child_model'])
    assert rel_type in ["inheritance"]


def test_process_many_to_many_field():
    edges = []
    source_ptr = str(uuid.uuid4())
    target_ptr = str(uuid.uuid4())

    field = Mock()
    field.null = False
    field.name = "test_m2m"

    process_many_to_many_field(field, edges, source_ptr, target_ptr)

    assert len(edges) == 1
    assert edges[0]["rel"]["type"] == "association"
    assert edges[0]["rel"]["multiplicity"]["source"] == "*"
