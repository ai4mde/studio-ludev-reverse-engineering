import uuid
import pytest
from unittest.mock import patch, Mock
from django.db import models
from django.test.utils import isolate_apps
from enum import Enum
import copy # Import the copy module

from scripts.src.utils.relationship_handler import (
    process_field_relationships,
    get_relationship_type,
    extract_method_dependencies,
    process_many_to_many_field,
    create_edge,
    process_inheritance_relationships,
    process_one_to_one_field,
    process_foreign_key_field,
    process_enum_field
)
from scripts.src.utils.django_environment_setup import *

# To run this script from the parent folder: python -m coverage run --source=scripts.src.utils.relationship_handler -m pytest -s -v scripts/tests/test_relationship_handler.py && python -m coverage report -m

# Current testing has a coverage of 85%. Improved from 70%.

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

# --------- New Fixtures for Extended Coverage ---------

class StatusEnum(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@pytest.fixture
@isolate_apps("test")
def extended_model_setup():
    """ Fixture for testing various relationship types and edge cases. """
    class Owner(models.Model):
        name = models.CharField(max_length=50)
        class Meta: app_label = 'test'

    class Profile(models.Model):
        owner = models.OneToOneField(Owner, on_delete=models.CASCADE)
        class Meta: app_label = 'test'

    class Account(models.Model):
        # This relationship will be an association because of null=True
        owner = models.OneToOneField(Owner, on_delete=models.CASCADE, null=True)
        class Meta: app_label = 'test'

    class Ticket(models.Model):
        # This relationship will be an association because of on_delete=SET_NULL
        owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True)
        status = models.CharField(max_length=10, choices=[(tag.name, tag.value) for tag in StatusEnum])
        class Meta: app_label = 'test'

    model_map = {
        Owner: str(uuid.uuid4()),
        Profile: str(uuid.uuid4()),
        Account: str(uuid.uuid4()),
        Ticket: str(uuid.uuid4())
    }
    enum_map = {"status": str(uuid.uuid4())}

    return {
        'Owner': Owner,
        'Profile': Profile,
        'Account': Account,
        'Ticket': Ticket,
        'model_ptr_map': model_map,
        'enum_ptr_map': enum_map
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

        # FIX: Use a deep copy to prevent polluting the fixture for other tests.
        isolated_data = copy.deepcopy(dependency_setup['data'])

        extract_method_dependencies(
            dependency_setup['model_a'],
            [dependency_setup['model_a'], dependency_setup['model_b']],
            isolated_data
        )

        dependency_edges = [e for e in isolated_data['edges']
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

# --------- New Tests For Increased Coverage ---------

def test_process_one_to_one_field_composition(extended_model_setup):
    """ Tests OneToOneField resulting in a 'composition' relationship. """
    edges = []
    model = extended_model_setup['Profile']
    field = model._meta.get_field('owner')
    source_ptr = extended_model_setup['model_ptr_map'][model]
    target_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Owner']]

    process_one_to_one_field(field, model, edges, source_ptr, target_ptr)

    assert len(edges) == 1
    edge = edges[0]
    assert edge['rel']['type'] == 'composition'
    # For composition, the source is the container (Owner) and target is the contained (Profile)
    assert edge['source_ptr'] == target_ptr
    assert edge['target_ptr'] == source_ptr

def test_process_one_to_one_field_association(extended_model_setup):
    """ Tests OneToOneField resulting in an 'association' relationship (due to null=True). """
    edges = []
    model = extended_model_setup['Account']
    field = model._meta.get_field('owner')
    source_ptr = extended_model_setup['model_ptr_map'][model]
    target_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Owner']]

    process_one_to_one_field(field, model, edges, source_ptr, target_ptr)

    assert len(edges) == 1
    edge = edges[0]
    assert edge['rel']['type'] == 'association'
    assert edge['source_ptr'] == source_ptr
    assert edge['target_ptr'] == target_ptr

def test_process_foreign_key_field_association(extended_model_setup):
    """ Tests ForeignKey resulting in an 'association' (due to on_delete=SET_NULL). """
    edges = []
    model = extended_model_setup['Ticket']
    field = model._meta.get_field('owner')
    source_ptr = extended_model_setup['model_ptr_map'][model]
    target_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Owner']]

    process_foreign_key_field(field, model, edges, source_ptr, target_ptr)

    assert len(edges) == 1
    edge = edges[0]
    assert edge['rel']['type'] == 'association'
    assert edge['source_ptr'] == source_ptr
    assert edge['target_ptr'] == target_ptr

def test_process_enum_field(extended_model_setup):
    """ Tests the creation of a dependency edge for an enum field. """
    edges = []
    source_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Ticket']]
    enum_ptr = extended_model_setup['enum_ptr_map']['status']

    # Mock a field object that would be identified as an enum
    field = Mock()
    field.name = 'status'

    process_enum_field(field, extended_model_setup['enum_ptr_map'], edges, source_ptr)

    assert len(edges) == 1
    edge = edges[0]
    assert edge['rel']['type'] == 'dependency'
    assert edge['target_ptr'] == enum_ptr

@patch('scripts.src.utils.relationship_handler.process_enum_field')
def test_process_field_relationships_with_enum(mock_process_enum, extended_model_setup):
    """ Ensures enum fields are correctly dispatched to process_enum_field. """
    model = extended_model_setup['Ticket']
    source_ptr = extended_model_setup['model_ptr_map'][model]
    with patch('scripts.src.utils.helper.is_enum_field') as mock_is_enum:
        # Make is_enum_field return True for the 'status' field
        mock_is_enum.side_effect = lambda f: f.name == 'status'

        process_field_relationships(
            model,
            extended_model_setup['model_ptr_map'],
            extended_model_setup['enum_ptr_map'],
            [], # edges
            source_ptr
        )

    mock_process_enum.assert_called_once()

def test_process_field_relationships_no_target_ptr(model_setup):
    """ Tests that a relationship is skipped if the target model is not in the ptr map. """
    edges = []
    # Remove the parent model from the map
    model_ptr_map = {k: v for k, v in model_setup['model_ptr_map'].items() if k != model_setup['parent_model']}

    process_field_relationships(
        model_setup['child_model'],
        model_ptr_map,
        {},
        edges,
        model_ptr_map[model_setup['child_model']]
    )

    # Only the inheritance edge should be created (if any), but no FK edge
    assert not any(e['rel']['type'] == 'composition' for e in edges)

def test_extract_method_dependencies_no_source_ptr(dependency_setup):
    """ Tests that the function exits early if the source model is not in the ptr map. """
    data = dependency_setup['data']
    # Remove ModelA from the map
    data['model_ptr_map'].pop(dependency_setup['model_a'])

    extract_method_dependencies(
        dependency_setup['model_a'],
        [dependency_setup['model_a'], dependency_setup['model_b']],
        data
    )
    assert len(data['edges']) == 0