import uuid
import pytest
from unittest.mock import patch, Mock
from django.db import models
from django.test.utils import isolate_apps
from enum import Enum
import copy
# Assuming the following imports are from the user's project structure
from api.model.importer.src.utils.relationship_handler import (
    process_field_relationships,
    get_relationship_type,
    extract_method_dependencies,
    process_many_to_many_field,
    create_edge,
    process_inheritance_relationships,
    process_one_to_one_field,
    process_foreign_key_field,
    process_enum_field,
    process_model_relationships,
    add_method_dependency_edges
)
from api.model.importer.src.utils.django_environment_setup import configure_mock_django_settings

# Configure the mock Django environment for the tests
configure_mock_django_settings()

# --------- Fixtures ---------

@pytest.fixture
@isolate_apps("test")
def model_setup():
    """Fixture for basic model inheritance and ForeignKey relationships."""
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
    """Fixture for testing method dependencies between models."""
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

class StatusEnum(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@pytest.fixture
@isolate_apps("test")
def extended_model_setup():
    """ Fixture for testing various relationship types and edge cases. """
    class Owner(models.Model):
        name = models.CharField(max_length=50)
        class Meta: 
            app_label = 'test'

    class Profile(models.Model):
        owner = models.OneToOneField(Owner, on_delete=models.CASCADE)
        class Meta: 
            app_label = 'test'

    class Account(models.Model):
        owner = models.OneToOneField(Owner, on_delete=models.CASCADE, null=True)
        class Meta: 
            app_label = 'test'

    class Ticket(models.Model):
        owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True)
        status = models.CharField(max_length=10, choices=[(tag.name, tag.value) for tag in StatusEnum])
        class Meta: 
            app_label = 'test'
        
    class ModelWithM2M(models.Model):
        tickets = models.ManyToManyField(Ticket, null=True)
        class Meta: 
            app_label = 'test'

    model_map = {
        Owner: str(uuid.uuid4()),
        Profile: str(uuid.uuid4()),
        Account: str(uuid.uuid4()),
        Ticket: str(uuid.uuid4()),
        ModelWithM2M: str(uuid.uuid4())
    }
    enum_map = {"status": str(uuid.uuid4())}

    return {
        'Owner': Owner,
        'Profile': Profile,
        'Account': Account,
        'Ticket': Ticket,
        'ModelWithM2M': ModelWithM2M,
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

def test_process_one_to_one_field_composition(extended_model_setup):
    edges = []
    model = extended_model_setup['Profile']
    field = model._meta.get_field('owner')
    source_ptr = extended_model_setup['model_ptr_map'][model]
    target_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Owner']]
    process_one_to_one_field(field, model, edges, source_ptr, target_ptr)
    assert len(edges) == 1
    edge = edges[0]
    assert edge['rel']['type'] == 'composition'
    assert edge['source_ptr'] == target_ptr
    assert edge['target_ptr'] == source_ptr

def test_process_one_to_one_field_association(extended_model_setup):
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

@patch('api.model.model.scripts.src.utils.relationship_handler.process_enum_field')
def test_process_field_relationships_with_enum(mock_process_enum, extended_model_setup):
    model = extended_model_setup['Ticket']
    source_ptr = extended_model_setup['model_ptr_map'][model]
    with patch('api.model.model.scripts.src.utils.helper.is_enum_field') as mock_is_enum:
        mock_is_enum.side_effect = lambda f: f.name == 'status'
        process_field_relationships(
            model,
            extended_model_setup['model_ptr_map'],
            extended_model_setup['enum_ptr_map'],
            [],
            source_ptr
        )
    mock_process_enum.assert_called_once()

def test_process_field_relationships_no_target_ptr(model_setup):
    edges = []
    model_ptr_map = {k: v for k, v in model_setup['model_ptr_map'].items() if k != model_setup['parent_model']}
    process_field_relationships(
        model_setup['child_model'],
        model_ptr_map,
        {},
        edges,
        model_ptr_map[model_setup['child_model']]
    )
    assert not any(e['rel']['type'] == 'composition' for e in edges)

def test_extract_method_dependencies_no_source_ptr(dependency_setup):
    data = dependency_setup['data']
    data['model_ptr_map'].pop(dependency_setup['model_a'])
    extract_method_dependencies(
        dependency_setup['model_a'],
        [dependency_setup['model_a'], dependency_setup['model_b']],
        data
    )
    assert len(data['edges']) == 0

def test_process_one_to_one_field_non_concrete(extended_model_setup):
    edges = []
    model = extended_model_setup['Profile']
    field = model._meta.get_field('owner')
    source_ptr = extended_model_setup['model_ptr_map'][model]
    target_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Owner']]
    with patch.object(field, 'concrete', False):
        process_one_to_one_field(field, model, edges, source_ptr, target_ptr)
    assert len(edges) == 0

def test_process_foreign_key_field_non_concrete(extended_model_setup):
    edges = []
    model = extended_model_setup['Ticket']
    field = model._meta.get_field('owner')
    source_ptr = extended_model_setup['model_ptr_map'][model]
    target_ptr = extended_model_setup['model_ptr_map'][extended_model_setup['Owner']]
    with patch.object(field, 'concrete', False):
        process_foreign_key_field(field, model, edges, source_ptr, target_ptr)
    assert len(edges) == 0

def test_process_enum_field_no_enum_ptr():
    edges = []
    source_ptr = "any_source"
    field = Mock()
    field.name = "non_existent_enum"
    process_enum_field(field, {}, edges, source_ptr)
    assert len(edges) == 0

def test_extract_method_dependencies_no_methods(dependency_setup):
    with patch('api.model.model.scripts.src.utils.helper.get_model_all_methods') as mock_get_methods:
        mock_get_methods.return_value = None
        extract_method_dependencies(
            dependency_setup['model_a'],
            [],
            dependency_setup['data']
        )
    assert len(dependency_setup['data']['edges']) == 0

def test_add_method_dependency_edges_exception_handling(dependency_setup, capsys):
    model_a = dependency_setup['model_a']
    model_b = dependency_setup['model_b']
    source_ptr = dependency_setup['data']['model_ptr_map'][model_a]
    model_names = {model_a.__name__: model_a, model_b.__name__: model_b, 123: "Invalid Model"}
    source_code_map = {'method_a': 'some code with ModelB'}
    add_method_dependency_edges(model_a, source_code_map, model_names, dependency_setup['data'], source_ptr)
    captured = capsys.readouterr()
    assert f"Error processing dependency from '{model_a.__name__}'" in captured.out

def test_process_many_to_many_field_with_null(extended_model_setup):
    edges = []
    source_ptr = str(uuid.uuid4())
    target_ptr = str(uuid.uuid4())
    model = extended_model_setup['ModelWithM2M']
    field = model._meta.get_field('tickets')
    process_many_to_many_field(field, edges, source_ptr, target_ptr)
    assert len(edges) == 1
    edge = edges[0]
    assert edge["rel"]["type"] == "association"
    assert edge["rel"]["multiplicity"]["target"] == "*"

def test_process_inheritance_relationships_skips_django_base():
    class AnotherModel(models.Model):
        class Meta:
            app_label = 'test'
    edges = []
    source_ptr = str(uuid.uuid4())
    model_ptr_map = {AnotherModel: source_ptr, models.Model: "django-model-ptr"}
    process_inheritance_relationships(AnotherModel, model_ptr_map, edges, source_ptr)
    assert len(edges) == 0

@patch('api.model.model.scripts.src.utils.relationship_handler.process_field_relationships')
@patch('api.model.model.scripts.src.utils.relationship_handler.process_inheritance_relationships')
def test_process_model_relationships(mock_inheritance, mock_fields, model_setup):
    model = model_setup['child_model']
    model_ptr_map = model_setup['model_ptr_map']
    enum_ptr_map = {}
    edges = []
    process_model_relationships(model, model_ptr_map, enum_ptr_map, edges)
    mock_inheritance.assert_called_once()
    mock_fields.assert_called_once()

def test_process_field_relationships_with_non_field_attribute(model_setup):
    model = model_setup['child_model']
    source_ptr = model_setup['model_ptr_map'][model]
    edges = []
    original_fields = model._meta.get_fields()
    mock_field = Mock()
    del mock_field.get_internal_type
    with patch.object(model._meta, 'get_fields', return_value=[*original_fields, mock_field]):
        process_field_relationships(model, model_setup['model_ptr_map'], {}, edges, source_ptr)
    assert len(edges) > 0

def test_extract_method_dependencies_creates_edge(dependency_setup):
    """
    Tests that a dependency edge IS created when a model name is in the code.
    """
    method_code = 'def method_a(self):\n    return "ModelB"'
    with patch('api.model.model.scripts.src.utils.helper.get_model_all_methods') as mock_get_methods:
        mock_get_methods.return_value = {'method_a': method_code}
        isolated_data = copy.deepcopy(dependency_setup['data'])
        
        extract_method_dependencies(
            dependency_setup['model_a'],
            [dependency_setup['model_a'], dependency_setup['model_b']],
            isolated_data
        )
        
        dependency_edges = [e for e in isolated_data['edges'] if e["rel"]["type"] == "dependency"]
        assert len(dependency_edges) == 1
        assert dependency_edges[0]["rel"]["label"].startswith("calls")

def test_process_enum_field():
    """
    Tests the creation of a dependency edge for an enum field.
    """
    edges = []
    source_ptr = "source_model_ptr"
    enum_ptr_map = {"status": "enum_status_ptr"}
    field = Mock()
    field.name = 'status'
    
    process_enum_field(field, enum_ptr_map, edges, source_ptr)
    
    assert len(edges) == 1
    edge = edges[0]
    assert edge['rel']['type'] == 'dependency'
    assert edge['rel']['label'] == 'depend'
    assert edge['target_ptr'] == "enum_status_ptr"

def test_process_field_relationships_skips_existing_calls_edge(model_setup):
    """
    Ensures a new relationship isn't created if a 'calls' edge already exists.
    """
    source_ptr = model_setup['model_ptr_map'][model_setup['child_model']]
    target_ptr = model_setup['model_ptr_map'][model_setup['parent_model']]
    
    edges = [{
        "rel": {"label": "calls", "type": "dependency"}, 
        "source_ptr": source_ptr, 
        "target_ptr": target_ptr
    }]
    
    process_field_relationships(
        model_setup['child_model'], 
        model_setup['model_ptr_map'], 
        {}, 
        edges, 
        source_ptr
    )
    
    has_unwanted_edge = any(e['rel'].get('type') in ['composition', 'association'] for e in edges)
    assert not has_unwanted_edge