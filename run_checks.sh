#!/bin/bash
# Run all quality checks for the project

set -e  # Exit on error

echo "================================"
echo "Running Tests..."
echo "================================"
python manage.py test home.tests

echo ""
echo "================================"
echo "Running Type Checks..."
echo "================================"
mypy .

echo ""
echo "================================"
echo "✓ All checks passed!"
echo "================================"
