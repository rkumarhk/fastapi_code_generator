#!/bin/bash

pip install -r requirements.txt

# Initialize database
alembic init db

# Create tables
alembic upgrade head