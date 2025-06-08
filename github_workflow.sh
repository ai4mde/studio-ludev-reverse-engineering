#!/bin/bash

# frontend tests
# Tsc
npm --prefix ./frontend/ run tsc --noEmit
# Eslint
npm --prefix ./frontend/ run lint_index

# beacked tests
# Ruff
ruff check ./api/model/importer/
# MyPi
mypy --follow-imports=skip --config-file="./api/pyproject.toml" ./api/model/importer/
# Unit tests
pytest