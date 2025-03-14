import csv
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def get_player_stats():
    """
    Load player statistics from CSV file.
    Using lru_cache to avoid repeated disk reads for the same data.
    """
    data = []
    # Use an absolute path to the CSV file in the Docker container
    csv_file_path = os.path.join(os.path.dirname(__file__), 'player_stats.csv')
    
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
    
    return data

def get_position_options():
    """Get unique position options from the data."""
    data = get_player_stats()
    positions = set()
    
    for player in data:
        if 'Positions' in player:
            player_positions = player['Positions'].split(', ')
            for pos in player_positions:
                positions.add(pos)
    
    return sorted(list(positions))

def get_team_options():
    """Get unique team options from the data."""
    data = get_player_stats()
    teams = {player['Team'] for player in data if 'Team' in player}
    return sorted(list(teams))