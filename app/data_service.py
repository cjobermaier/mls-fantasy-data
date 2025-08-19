import csv
import os
import glob
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

def get_player_by_id(player_id):
    """Get a specific player by their ID."""
    data = get_player_stats()
    for player in data:
        if player.get('Player ID') == str(player_id):
            return player
    return None

def compare_players(player_ids):
    """Compare multiple players by their IDs."""
    players = []
    for player_id in player_ids:
        player = get_player_by_id(player_id)
        if player:
            players.append(player)
    
    if len(players) < 2:
        return {'error': 'Not enough valid players found for comparison'}
    
    # Define comparison stats
    comparison_stats = [
        'Cost', 'Total Points', 'Average Points', 'Owned By',
        'Total Combined Points', 'Total GL Points', 'Total ASS Points',
        'Total YC Points', 'Total RC Points', 'Total CS Points',
        'Total MIN Points', 'Total KP Points', 'Total CRS Points'
    ]
    
    comparison_data = {
        'players': players,
        'stats': comparison_stats,
        'winner_stats': {}
    }
    
    # Determine winner for each stat (higher is better for most stats)
    negative_stats = ['Total YC Points', 'Total RC Points', 'Cost']
    
    for stat in comparison_stats:
        values = []
        for player in players:
            try:
                # Clean up the value (remove $ and % signs, convert to float)
                value_str = str(player.get(stat, '0'))
                value_str = value_str.replace('$', '').replace('M', '').replace('%', '')
                value = float(value_str) if value_str else 0
                values.append((value, player['Player ID']))
            except (ValueError, TypeError):
                values.append((0, player['Player ID']))
        
        if stat in negative_stats:
            # For negative stats, lower is better
            winner_id = min(values, key=lambda x: x[0])[1]
        else:
            # For positive stats, higher is better
            winner_id = max(values, key=lambda x: x[0])[1]
        
        comparison_data['winner_stats'][stat] = winner_id
    
    return comparison_data

@lru_cache(maxsize=10)
def get_weekly_player_stats(week=None):
    """
    Load player statistics for a specific week from CSV files.
    If week is None, returns the current season totals.
    """
    if week is None:
        return get_player_stats()
    
    # Construct the weekly CSV file path
    week_filename = f"{week.lower().replace(' ', '_')}_stats.csv"
    weekly_csv_path = os.path.join(os.path.dirname(__file__), 'weekly_data', week_filename)
    
    if not os.path.exists(weekly_csv_path):
        print(f"Weekly data not found: {weekly_csv_path}")
        return []
    
    data = []
    try:
        with open(weekly_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Weekly CSV file not found: {weekly_csv_path}")
    
    return data

def get_available_weeks():
    """Get list of available weeks from the weekly_data directory."""
    weekly_data_dir = os.path.join(os.path.dirname(__file__), 'weekly_data')
    
    if not os.path.exists(weekly_data_dir):
        return []
    
    # Find all weekly CSV files
    csv_files = glob.glob(os.path.join(weekly_data_dir, 'week_*_stats.csv'))
    weeks = []
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        # Extract week from filename (e.g., 'week_14_stats.csv' -> 'Week 14')
        week_part = filename.replace('_stats.csv', '').replace('week_', '')
        week_name = f"Week {week_part}"
        weeks.append(week_name)
    
    # Sort weeks numerically
    weeks.sort(key=lambda x: int(x.split()[-1]))
    return weeks

def compare_players_weekly(player_ids, week=None):
    """Compare multiple players by their IDs for a specific week."""
    players = []
    for player_id in player_ids:
        player = get_player_by_id_weekly(player_id, week)
        if player:
            players.append(player)
    
    if len(players) < 2:
        return {'error': 'Not enough valid players found for comparison'}
    
    # Define comparison stats (adjusted for weekly data)
    comparison_stats = [
        'Cost', 'Games Played', 'Total Points', 'Average Points',
        'Goals', 'Assists', 'Minutes', 'Yellow Cards', 'Red Cards',
        'Clean Sheets', 'Goals Conceded', 'Shots on Goal', 'Key Passes'
    ]
    
    comparison_data = {
        'players': players,
        'stats': comparison_stats,
        'winner_stats': {},
        'week': week or 'Season Total'
    }
    
    # Determine winner for each stat
    negative_stats = ['Yellow Cards', 'Red Cards', 'Cost', 'Goals Conceded']
    
    for stat in comparison_stats:
        values = []
        for player in players:
            try:
                value_str = str(player.get(stat, '0'))
                value_str = value_str.replace('$', '').replace('M', '').replace('%', '')
                value = float(value_str) if value_str else 0
                values.append((value, player['Player ID']))
            except (ValueError, TypeError):
                values.append((0, player['Player ID']))
        
        if stat in negative_stats:
            winner_id = min(values, key=lambda x: x[0])[1]
        else:
            winner_id = max(values, key=lambda x: x[0])[1]
        
        comparison_data['winner_stats'][stat] = winner_id
    
    return comparison_data

def get_player_by_id_weekly(player_id, week=None):
    """Get a specific player by their ID for a specific week."""
    data = get_weekly_player_stats(week)
    for player in data:
        if player.get('Player ID') == str(player_id):
            return player
    return None