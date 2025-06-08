### High-Level Overview

The `tests` folder contains the unit tests for the entire project, ensuring the reliability and correctness of both the legacy script (`extract_jinja2.py`) and the modular `utils` components. The tests are built using the `pytest` framework and leverage tools like `pytest-cov` for measuring code coverage, with several test files indicating that 100% coverage has been achieved for those modules. The testing strategy relies heavily on fixtures to create controlled, isolated environments and on mocking to prevent dependencies on external systems or files.

---

### Technical Description

* **`test_extract_jinja2.py`**
    * This script tests the original, monolithic extraction file.
    * **Fixtures**: It defines a `fake_sys_argv` fixture that uses `monkeypatch.setattr` to modify `sys.argv`, allowing it to test the `argparse` configuration without running the script from the command line.
    * It also includes a `dummy_zip_file` fixture, which uses `pytest`'s built-in `tmp_path` fixture to create a temporary directory structure for a fake Django project and then packages it into a zip file using the `zipfile` library. This allows tests for `extract_zip` and `get_project_root` to run in a predictable and isolated manner.

* **`test_helper.py`**
    * This script tests the functions in `utils/helper.py`.
    * **Environment**: It begins by calling `configure_mock_django_settings()` to ensure a valid (but minimal) Django environment is active for the tests.
    * **Fixtures**: It uses fixtures like `mock_enum_field` and `mock_app_config` that create mock objects using `unittest.mock.Mock`. These mocks simulate Django fields and app configurations, allowing functions like `is_enum_field` and `collect_all_valid_models` to be tested without needing real Django models.
    * **Output Capturing**: It uses `pytest`'s `capsys` fixture to capture standard output, which is used to verify that `verify_data_integrity` prints the correct warning messages for broken relationships.

* **`test_node_handler.py`**
    * This script tests the node creation logic in `utils/node_handler.py`.
    * **Parametrization**: It uses the `@pytest.mark.parametrize` decorator to efficiently test the `map_field_type` function with a wide range of different Django field types and their expected string outputs, making the test concise and comprehensive.
    * **Mocking**: It uses `patch` from `unittest.mock` to isolate functions under test. For example, it patches `helper.is_enum_field` to force a specific return value when testing how `map_field_type` handles an enum, ensuring the test is focused only on the mapping logic itself.

* **`test_relationship_handler.py`**
    * This is the most complex test suite, covering the relationship detection logic from `utils/relationship_handler.py`.
    * **Isolated Model Definitions**: It uses the `@isolate_apps("test")` decorator provided by Django's test utilities. This allows for the dynamic definition of mock Django models within test fixtures (`model_setup`, `extended_model_setup`, etc.) without interfering with the global Django app registry.
    * **Complex Fixtures**: The fixtures in this file create various constellations of Django models to test specific relationship scenarios, such as inheritance (`TestParentModel`, `TestChildModel`), one-to-one fields with different `on_delete` behaviors, foreign keys, and many-to-many fields.
    * **Behavioral Patching**: It uses `patch` to modify the behavior of objects for specific tests. For example, it patches a field's `concrete` attribute to `False` to test that non-concrete fields are correctly ignored during relationship processing.