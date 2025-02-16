#!/bin/bash

echo "Installing poetry if not exists..."
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

echo "Installing dependencies..."
poetry install

echo "Building package..."
poetry build

echo "Running build tests..."
poetry run build-test 