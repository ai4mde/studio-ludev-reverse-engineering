#!/bin/bash

# frontend tests
# Tsc
npm --prefix ./frontend/ run tsc --noEmit
# Eslint
npm --prefix ./frontend/ run lint_index

# beacked tests
# Ruff
ruff check ./api/model/model ./scripts
# MyPi
mypy --follow-imports=skip ./scripts/src/ ./scripts/tests/
# Unit tests
pytest