#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# If you use Flask-Migrate, uncomment the line below:
# flask db upgrade