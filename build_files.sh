#!/bin/bash
echo "Building project packages..."
python3 -m pip install -r requirements.txt --break-system-packages
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
echo "Build complete!"
