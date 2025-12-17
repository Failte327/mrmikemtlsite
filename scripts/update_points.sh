#!/bin/bash

pip install -r ../requirements.txt
echo "Running tournament data gathering script..."
python3 tournament_data_gather.py

echo "Running missing tournament ids script..."
python3 add_missing_tournament_ids.py

echo "Running missing user ids script..."
python3 add_missing_user_ids.py

echo "Running points reset script..."
python3 reset_points.py

echo "Running points calculation script"
python3 calculate_points.py

echo "Running win/loss update script"
python3 update_wins_losses.py

echo "Tournament data up-to-date!"