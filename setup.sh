#!/bin/bash

# Create virtual environment
python -m venv fastapi-env

# Activate virtual environment
source fastapi-env/bin/activate

# Install dependencies
pip install -r requirements.txt