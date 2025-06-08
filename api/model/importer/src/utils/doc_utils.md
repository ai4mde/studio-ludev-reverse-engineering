### High-Level Overview

The `utils` folder serves as a foundational library for the primary extraction script, `extract_prototype_main.py`. It encapsulates the core logic of the reverse-engineering process into a set of specialized, modular, and reusable components. Each module in this directory has a distinct responsibility, such as handling the Jinja2 template, setting up the Django environment, creating diagram nodes, or processing relationships. This modular design makes the overall system more organized, maintainable, and easier to test compared to the original monolithic script.

---

### Technical Description

* **`diagram_template.py`**
    * This module contains a single variable, `diagram_template_obj`, which is an instance of a Jinja2 `Template` object.
    * The template string is designed to generate a complex JSON structure. It features conditional logic using `{% if node.cls.type == 'enum' %}` to render a node differently if it is an enumeration versus a standard class.
    * It uses Jinja2 `for` loops to iterate over lists of `nodes`, `edges`, `methods`, and `attributes` to dynamically build the final JSON output.

* **`django_environment_setup.py`**
    * `configure_django_settings`: This function sets up the environment for a real Django project. It uses a hardcoded absolute path to the project root, appends this path to `sys.path`, and sets the `DJANGO_SETTINGS_MODULE` environment variable before calling `django.setup()`.
    * `configure_mock_django_settings`: This function is used for testing. It calls `settings.configure()` to create a temporary, in-memory Django environment if one is not already configured. It sets up a minimal configuration with an in-memory SQLite database, which avoids the need for a real project or database during tests.

* **`helper.py`**
    * `is_enum_field`: Determines if a Django model field represents an enumeration by checking if its `choices` attribute is a non-empty list where each item is a tuple of length two.
    * `collect_all_valid_models`: Gathers all relevant models by iterating through an app's models and then recursively traversing their `__bases__` attribute to find and include parent classes, excluding standard Django base models.
    * `get_custom_methods`: Identifies user-defined methods on a model. It filters out methods that are part of the standard `models.Model`, are listed in `DJANGO_GENERATED_METHODS`, or start with an underscore. It then uses `is_method_without_args` to ensure the method only takes `self` as a parameter.
    * `verify_data_integrity`: A validation function that loops through all generated edges and checks that their `source_ptr` and `target_ptr` values correspond to an actual node `id` in the list of nodes, printing a warning if a match is not found.

* **`node_handler.py`**
    * This module acts as a factory for creating diagram nodes and their components.
    * `process_enum_field_node`: Creates a JSON node for an enum. It uses a provided `enum_ptr_map` dictionary to check if the enum has already been processed, preventing duplicate nodes.
    * `map_field_type`: A utility function that converts Django `models.Field` objects into simple string types for the diagram (e.g., `models.CharField` becomes `"str"`). It uses a series of `isinstance` checks to perform the mapping.
    * `create_attribute` and `create_model_node`: These functions construct the dictionary objects for attributes and class nodes, respectively, ensuring they conform to the JSON schema expected by the `diagram_template.py`.

* **`relationship_handler.py`**
    * This module contains the logic for identifying and creating all relationships (edges) in the diagram.
    * `process_inheritance_relationships`: Discovers `generalization` (inheritance) relationships by inspecting a model's `__bases__` attribute and creating edges to its parent models.
    * `process_field_relationships`: The main dispatcher for field-based relationships. It iterates over a model's fields using `model._meta.get_fields()` and delegates to more specific functions like `process_many_to_many_field` or `process_foreign_key_field`.
    * `get_relationship_type`: Differentiates between `composition` and `association` for foreign key and one-to-one fields. A relationship is considered a `composition` if the `on_delete` behavior is `models.CASCADE` and the field is not `null`; otherwise, it is an `association`.
    * `extract_method_dependencies`: Performs dependency analysis by retrieving the source code of a model's methods (using `get_model_all_methods` from the helper) and then using `re.search` to find textual mentions of other model names within the code, creating a `dependency` edge if a match is found.