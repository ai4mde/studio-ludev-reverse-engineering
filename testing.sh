#!/bin/bash

# frontend tests
# Tsc
npm --prefix ./frontend/ run tsc
# Eslint
npm --prefix ./frontend/ run lint_index.tsx

# beacked tests
# Ruff
ruff check ./api/model/model ./scripts
# MyPi
mypy --follow-imports=skip ./api/model/model/api.py