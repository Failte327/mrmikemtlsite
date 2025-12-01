#!/bin/bash

pip install -r ../requirements.txt
echo "Running tournament data gathering script..."
python3 tournament_data_gather.py

echo "Running points reset script..."
python3 reset_points.py

echo "Running points calculation script"
python3 calculate_points.py

echo "Tournament data up-to-date!"