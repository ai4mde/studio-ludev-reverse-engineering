### High-Level Overview

The `src` folder contains the core logic for a reverse-engineering tool that inspects the models of a Django project, generates a JSON representation of its class diagram, and automates the process of importing this diagram into the AI4MDE platform.

The project shows an evolution from an initial, monolithic script to a more robust, modular architecture.

* **Initial Approach (`extract_jinja2.py`)**: This script represents the first version of the tool. It is a self-contained module that can parse command-line arguments to accept a zipped Django project, set up the necessary environment, extract model data, and render a JSON output using a hardcoded Jinja2 template.

* **Modular Architecture (`extract_prototype_main.py` and `utils/`)**: This represents the current, more advanced implementation. The logic is broken down into specialized modules within the `utils` subdirectory, each handling a specific part of the process (e.g., node creation, relationship handling, environment setup). The main script, `extract_prototype_main.py`, orchestrates the workflow by calling these utility modules. This design is more maintainable, extensible, and testable.

* **End-to-End Automation (`import_diagram.py`)**: This script is the final entry point for the user. It leverages the modular architecture (`extract_prototype_main.py`) to generate the diagram data and then communicates with an external API to authenticate, import the diagram, and trigger an auto-layout feature, providing a complete, automated workflow.

---

### Technical Description

This section provides a more detailed technical breakdown of each component within the `src` folder.

#### Main Scripts

* **`extract_jinja2.py`**
    * **Argument Parsing**: Uses the `argparse` library to handle command-line arguments, requiring a single `--zip_file` or `-z` argument for the path to the Django project's zip file.
    * **Environment Setup**:
        * The `extract_zip` function unpacks the provided zip file into a `../projects` folder.
        * `get_project_root` finds the project's root directory by searching for the `settings.py` file within the extracted contents.
        * It then configures the Django environment by adding the project root to `sys.path` and setting the `DJANGO_SETTINGS_MODULE` environment variable before calling `django.setup()`.
    * **Data Extraction**:
        * The `generate_diagram_json` function iterates through the models of the `shared_models` app.
        * For each model, it creates a `node` dictionary, populating attributes from `model._meta.get_fields()` and methods from a custom `get_custom_methods` function.
        * It identifies relationships by checking `field.is_relation` and specific boolean flags like `field.many_to_one` or `field.many_to_many`. However, the `target_ptr` for these relationships is a placeholder UUID, as it doesn't map them to the actual target model nodes.
    * **Rendering**: The final JSON is rendered using a single, hardcoded Jinja2 template string defined within the file.

* **`extract_prototype_main.py`**
    * **Orchestration**: This script acts as the main controller for the modular extraction process. Its `generate_diagram_json` function is the primary entry point.
    * **Workflow**:
        1.  Initializes a data dictionary to hold nodes, edges, and mapping tables.
        2.  Calls `configure_django_settings()` from the `utils` module to set up the environment.
        3.  Uses `collect_all_valid_models` to gather all models, including parent classes, from the target app (`shared_models`).
        4.  Pre-populates a map of models to unique IDs using `initialize_model_ptr_map` to ensure consistent references.
        5.  The `process_model` function is called for each model, which in turn uses the `node_handler` and `relationship_handler` utilities to build the diagram components.
        6.  Optionally, it calls `extract_method_dependencies` if the `show_method_dependency` flag is true.
        7.  Before rendering, it runs `verify_data_integrity` to check for broken relationships.
        8.  Finally, it renders the output using the external `diagram_template_obj`.

* **`import_diagram.py`**
    * **API Workflow**: The `call_endpoints_to_import_diagram` function executes a three-step API interaction.
    * **Step 1: Authentication**: It sends a POST request with a username and password to the `/api/v1/auth/token` endpoint to retrieve a JWT token.
    * **Step 2: Import**: It calls `generate_diagram_json` to get the diagram data, then sends this payload in a POST request to `/api/v1/diagram/import`, including the JWT token in the `Authorization` header.
    * **Step 3: Auto-Layout**: If the import request returns a status code of 200, it extracts the diagram ID from the response body and sends a POST request to `/api/v1/diagram/{diagram_id}/auto_layout` to trigger the layout algorithm.

#### `utils` Subdirectory

* **`diagram_template.py`**
    * Contains a single Jinja2 `Template` object named `diagram_template_obj`.
    * This template is more advanced than the one in `extract_jinja2.py`, as it includes conditional logic (`{% if node.cls.type == 'enum' %}`) to render nodes as either standard classes or enumerations.

* **`django_environment_setup.py`**
    * `configure_django_settings`: Sets up a live Django environment using a hardcoded project path.
    * `configure_mock_django_settings`: Creates a minimal, in-memory Django environment for testing by using `settings.configure()` with a basic `INSTALLED_APPS` list and an in-memory SQLite database.

* **`helper.py`**
    * `is_enum_field`: Checks if a model field is an enumeration by verifying that its `choices` attribute is a non-empty list of tuples.
    * `collect_all_valid_models`: Recursively inspects the `__bases__` of each model to find and include parent models in the analysis.
    * `get_custom_methods`: Filters out standard Django methods and private methods (starting with `_`), then uses `is_method_without_args` to ensure only methods callable with just `self` are included.
    * `verify_data_integrity`: A sanity check that iterates through all edges and ensures their `source_ptr` and `target_ptr` values correspond to an existing node `id` in the `nodes` list.

* **`node_handler.py`**
    * `process_enum_field_node`: Creates JSON nodes for enum types. It uses an `enum_ptr_map` to avoid duplicating nodes for the same enum.
    * `map_field_type`: A utility function that converts Django `models.Field` types (e.g., `CharField`, `IntegerField`) into simple string representations (`str`, `int`, `datetime`, etc.) for the diagram.
    * `create_attribute` / `create_model_node`: Factory functions that build the dictionary structures for attributes and class nodes according to the schema defined in `diagram_template.py`.

* **`relationship_handler.py`**
    * `process_inheritance_relationships`: Identifies `generalization` relationships by iterating through a model's `__bases__` attribute.
    * `process_field_relationships`: Iterates through a model's fields via `_meta.get_fields()` and delegates relationship creation to more specialized functions based on the field type (`ManyToManyField`, `ForeignKey`, etc.).
    * `get_relationship_type`: Contains logic to classify `ForeignKey` and `OneToOneField` relationships. It identifies a `composition` if `on_delete` is set to `models.CASCADE` and the field is not nullable; otherwise, it is treated as an `association`.
    * `extract_method_dependencies`: Inspects the source code of model methods (retrieved via `get_model_all_methods`) and uses a regular expression (`re.search`) to find mentions of other model names, thereby creating `dependency` edges between them.