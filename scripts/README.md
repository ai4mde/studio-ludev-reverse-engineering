# Django Model Diagram Generator – `scripts/` Module

This module is part of a larger Django-based application. It provides functionality to dynamically extract model structures from the `shared_models` Django app and generate structured JSON suitable for class diagram visualization.

## Purpose

Located within the `scripts/` directory of the main project, this module supports:

- Model introspection for documentation or visualization.
- API integration for frontend tools that consume diagram-formatted data.
- Diagram generation using either a custom Python structure or Jinja2 templating.

## Components

The module includes the following files:

- `extract.py`: Standalone script that extracts model and field metadata as JSON.
- `extract_to_diagram.py`: Converts model information into structured diagram data.
- `extract_jinja2.py`: Uses Jinja2 to format diagram JSON with extended customization.
- `endpoint.py`: Provides an HTTP endpoint via Django-Ninja for external access.

These scripts assume that Django is fully configured and initialized (e.g., `shop.settings` is accessible and points to the correct project settings).

## Usage Context

This code is designed to be executed **inside the main Django project context**, meaning:

- `DJANGO_SETTINGS_MODULE` is set to the main project (`shop.settings`).
- `sys.path` includes the full path to the Django application directory.
- It depends on the presence of an app named `shared_models` within `INSTALLED_APPS`.
