from metadata.models import System, Classifier, Interface
from metadata.api.schemas import ReadInterface
from typing import List, Dict, Any, Optional
from enum import Enum
from uuid import uuid4


class CrudType(Enum):
    CREATE = 1
    READ = 2
    UPDATE = 3
    DELETE = 4
    OTHER = 5


class ModelAttribute():
    def __init__(self,
                 name: str,
                 type: str,
                 derived: bool,
                 enum: Optional[str]):
        self.name = name
        self.type = type
        self.derived = derived
        self.enum = enum


class DefaultUsecase():
    def __init__(self,
                 name: str,
                 crud_types: List[CrudType],
                 model: Dict[str, Any],
                 attributes: List[ModelAttribute]):
        self.name = name
        self.crud_types = crud_types
        self.model = model
        self.attributes = attributes


def get_directly_linked_use_cases(system: System, actor: Classifier) -> List[Classifier]:
    directly_linked_use_cases = []
    for relation in system.relations.filter(data__type='interaction'):
        if relation.source == actor:
            directly_linked_use_cases.append(relation.target)
        elif relation.target == actor:
            directly_linked_use_cases.append(relation.source)

    return directly_linked_use_cases


def get_extended_use_cases(system: System, use_cases: List[Classifier]) -> List[Classifier]:
    extended_use_cases = []
    for relation in system.relations.filter(data__type='extension'):
        for use_case in use_cases:
            if relation.source == use_case and relation.target not in use_cases and relation.target not in extended_use_cases:
                extended_use_cases.append(relation.target)

    return extended_use_cases


def get_class_acted_on(system: System, use_case_name: str) -> str:
    for cls in system.classifiers.filter(data__type='class'):
        if 'name' not in cls.data:
            continue
        if cls.data['name'].lower() in use_case_name:
            return cls.id

    return None


def get_crud_type(use_case_name: str) -> CrudType:
    create_words = ['create', 'make', 'new', 'post']
    read_words = ['read', 'view', 'get', 'see']
    update_words = ['update', 'edit', 'patch', 'put']
    delete_words = ['delete', 'remove', 'erase']

    if [word for word in create_words if(word in use_case_name)]:
        return CrudType.CREATE

    if [word for word in read_words if(word in use_case_name)]:
        return CrudType.READ

    if [word for word in update_words if(word in use_case_name)]:
        return CrudType.UPDATE

    if [word for word in delete_words if(word in use_case_name)]:
        return CrudType.DELETE

    return CrudType.OTHER


def get_class_attributes(class_id: str) -> List[ModelAttribute]:
    cls = Classifier.objects.get(pk=class_id)
    if not cls:
        return []
    if 'attributes' not in cls.data:
        return []
    out = []
    for attribute in cls.data['attributes']:
        att = ModelAttribute(
            name = attribute['name'],
            type = attribute['type'],
            derived = attribute['derived'],
            enum = attribute['enum']
        )
        out.append(att)
    return out


def get_default_use_cases(system: System, relevant_use_cases: List[Classifier]) -> List[DefaultUsecase]:
    out = []
    crud_types_per_class: Dict[str, List[CrudType]] = {}

    for use_case in relevant_use_cases:
        if 'name' not in use_case.data:
            continue
        name = use_case.data['name'].lower()
        class_acted_on = get_class_acted_on(system, name)
        if not class_acted_on:
            continue
        crud_type = get_crud_type(name)
        if class_acted_on not in crud_types_per_class:
            crud_types_per_class[class_acted_on] = []
        crud_types_per_class[class_acted_on].append(crud_type)

    classes_visited = []
    for use_case in relevant_use_cases:
        if 'name' not in use_case.data:
            continue
        name = use_case.data['name'].lower()
        class_acted_on = get_class_acted_on(system, name)
        if not class_acted_on:
            continue
        if get_crud_type(name) == CrudType.OTHER:
            continue

        if class_acted_on in classes_visited:
            for previous_usecase in out:
                if previous_usecase.model == class_acted_on:
                    previous_usecase.name += f" and {name}"
                    break
        else:
            classes_visited.append(class_acted_on)
            attributes = get_class_attributes(class_acted_on)
            model_name = None
            for cls in system.classifiers.filter(data__type='class'):
                if 'name' not in cls.data:
                    continue
                if cls.data['name'].lower() in name:
                    model_name = cls.data['name']
            default_use_case = DefaultUsecase(
                name = name,
                crud_types = crud_types_per_class[class_acted_on],
                model = {'id': class_acted_on, 'name': model_name},
                attributes = attributes
            )
            out.append(default_use_case)

    return out


def build_data_section_attributes(use_case: DefaultUsecase) -> List[Dict[str, Any]]:
    out = []
    for attribute in use_case.attributes:
        att = {
            "name": attribute.name,
            "type": attribute.type,
            "derived": attribute.derived,
            "enum": attribute.enum
        }
        out.append(att)
    return out


def build_data_section_operations(use_case: DefaultUsecase) -> Dict[str, Any]:
    return {
        "create": CrudType.CREATE in use_case.crud_types,
        "update": CrudType.UPDATE in use_case.crud_types,
        "delete": CrudType.DELETE in use_case.crud_types
    }


def build_data_sections(default_use_case_objects: List[DefaultUsecase]) -> List[Dict[str, Any]]:
    out = []
    for use_case in default_use_case_objects:
        section = {
            "id": uuid4().hex,
            "name": use_case.name,
            "class": str(use_case.model['id']),
            "model_name": str(use_case.model['name']),
            "attributes": build_data_section_attributes(use_case),
            "operations": build_data_section_operations(use_case),
            "text": "",
        }
        out.append(section)
    return out


def build_data_pages(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for section in sections:
        page = {
            "id": uuid4().hex,
            "name": section["name"] + " page",
            "category": {
                "label": section["model_name"],
                "value": {
                    "id": section["class"],
                    "name": section["model_name"]
                }
            }, # TODO: this is a redundant structure, but the frontend must first be changed accordingly
            "sections": [
                {
                    "label": section['name'],
                    "value": section['id']
                }
            ]
        }
        out.append(page)
    return out


def build_data_styling() -> Dict[str, Any]:
    return {
        "radius": 0,
        "textColor": "#000000",
        "accentColor": "#F5F5F4",
        "selectedStyle": "modern",
        "backgroundColor": "#FFFFFF"
    }


def build_data_categories(default_use_case_objects: List[DefaultUsecase]) -> List[Dict[str, Any]]:
    out = []
    models_written = []
    for use_case in default_use_case_objects:
        if use_case.model in models_written:
            continue
        category = {
            "id": uuid4().hex,
            "name": str(use_case.model['name']),
        }
        models_written.append(use_case.model)
        out.append(category)
    return out


def build_data(default_use_case_objects: List[DefaultUsecase]) -> Dict[str, Any]:
    sections = build_data_sections(default_use_case_objects)
    categories = build_data_categories(default_use_case_objects)
    pages = build_data_pages(sections)
    styling = build_data_styling()

    data = {
        "sections": sections,
        "pages": pages,
        "categories": categories,
        "styling": styling,
    }
    return data


def get_default_interface_data(system: System, actor: Classifier) -> str:
    directly_linked_use_cases = get_directly_linked_use_cases(system, actor)
    extended_use_cases = get_extended_use_cases(system, directly_linked_use_cases)
    relevant_use_cases = directly_linked_use_cases + extended_use_cases
    default_use_case_objects = get_default_use_cases(system, relevant_use_cases)
    return build_data(default_use_case_objects)


def create_default_interface(system: System, actor: Classifier) -> ReadInterface:
    if actor.data['type'] != 'actor':
        return 404, "Classifier is not an actor"

    return Interface.objects.create(
        name = actor.data['name'],
        description = actor.data['name'] + " application",
        system = system,
        actor = actor,
        data = get_default_interface_data(system, actor) # smart defaulting
    )
