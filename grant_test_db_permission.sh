#!/bin/bash
# Script to grant CREATEDB permission to the wagtail user for testing

echo "This script will grant CREATEDB permission to the wagtail PostgreSQL user."
echo "You may need to run this with sudo or as the postgres user."
echo ""
echo "Run this command:"
echo "  sudo -u postgres psql -c \"ALTER USER wagtail CREATEDB;\""
echo ""
echo "Or connect to PostgreSQL and run:"
echo "  ALTER USER wagtail CREATEDB;"
