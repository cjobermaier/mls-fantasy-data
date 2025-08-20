import requests
import math
import csv
import os
from datetime import datetime

def fetch_all_team_data():
    """Fetch all team data from the S3 bucket once and store it."""
    url = "https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/squads.json?_=1741969652364"
    
    response = requests.get(url)
    if response.status_code == 200:
        teams = response.json()
        
        # Create a dictionary mapping team IDs to their data
        team_dict = {team['id']: team for team in teams}
        
        # Print the fetched team data for testing
       # for team_id, team_info in team_dict.items():
           # print(f"Team ID: {team_id}, Name: {team_info['name']}, Short Name: {team_info['short_name']}")
        
        return team_dict
    else:
        print(f"Failed to fetch team data, status code: {response.status_code}")
        return {}

def fetch_all_player_data():
    """Fetch all player data from the S3 bucket once and store it."""
    url = "https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741793495420"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch player data, status code: {response.status_code}")
        return []

def fetch_all_game_stats(player_ids):
    """Fetch game stats for all players and store them in a dictionary."""
    player_game_stats = {}
    
    for player_id in player_ids:
        url = f"https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/stats/players/{player_id}.json?_=1741793495420"
        response = requests.get(url)
        
        if response.status_code == 200:
            player_data = response.json()
            
            game_stats = []
            for player in player_data:
                match_stats = player.get('stats', {})
                match_id = player.get('match_id', None)
                if match_id:
                    game_stats.append({'match_id': match_id, 'stats': match_stats})
            
            player_game_stats[player_id] = game_stats
        else:
            print(f"Failed to fetch game stats for player {player_id}, status code: {response.status_code}")
            player_game_stats[player_id] = []
    
    return player_game_stats

def determine_week_from_match_id(match_id):
    """Determine the week/round from match_id using chronological ordering."""
    try:
        # Match IDs are in YYYYMMDD format
        match_num = int(match_id)
        
        # Define rough chronological ranges for MLS weeks based on match IDs
        # This is based on the observation that matches start around 20250104
        if match_num >= 20250000:  # 2025 season dates
            # Map date ranges to weeks more accurately
            if match_num <= 20250115:  # Early January
                week_num = 1
            elif match_num <= 20250215:  # Mid January to mid February
                week_num = 2
            elif match_num <= 20250315:  # Mid February to mid March  
                week_num = 3
            elif match_num <= 20250415:  # Mid March to mid April
                week_num = 4
            elif match_num <= 20250515:  # Mid April to mid May
                week_num = 5
            elif match_num <= 20250615:  # Mid May to mid June
                week_num = 6
            elif match_num <= 20250715:  # Mid June to mid July
                week_num = 7
            elif match_num <= 20250815:  # Mid July to mid August
                week_num = 8
            elif match_num <= 20250915:  # Mid August to mid September
                week_num = 9
            elif match_num <= 20251015:  # Mid September to mid October
                week_num = 10
            elif match_num <= 20251115:  # Mid October to mid November
                week_num = 11
            elif match_num <= 20251215:  # Mid November to mid December
                week_num = 12
            else:
                # Later dates spread across remaining weeks
                week_num = min(28, max(13, ((match_num - 20251215) // 100) + 13))
        else:
            # Fallback for non-date match IDs
            week_num = (match_num % 28) + 1
        
        week_num = max(1, min(28, week_num))
        return f"Week {week_num}"
    except:
        return "Week 14"  # Default fallback

def extract_fantasy_stats(player_data, player_id):
    """Extract fantasy stats for a specific player from the already downloaded data."""
    position_mapping = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    for player in player_data:
        if player.get('id') == player_id:
            positions = [position_mapping.get(pos, 'Unknown') for pos in player.get('positions', [])]
            return {
                'id': player['id'],
                'first_name': player.get('first_name', ''),
                'last_name': player.get('last_name', ''),
                'cost': player.get('cost', 0),
                'total_points': player.get('stats', {}).get('total_points', 0),
                'avg_points': player.get('stats', {}).get('avg_points', 0),
                'owned_by': player.get('stats', {}).get('owned_by', 0),
                'high_score': player.get('stats', {}).get('high_score', 0),
                'low_score': player.get('stats', {}).get('low_score', 0),
                'positions': positions,
                'squad_id': player.get('squad_id', 0)  # Add squad_id here
            }
    return {}

def calculate_player_points(game_stats, fantasy_stats, team_dict):
    """Calculate fantasy points for a player based on game statistics."""
    # MLSF GUI - S3 (GF - GL)
    total_min_points = 0 # MIN total minutes player
    total_gl_points = 0  # goals: GF - GL 
    total_ass_points = 0 # assists: A - ASS
    total_gc_points = 0  # goals conceded: GA - GC
    total_cs_points = 0  # clean sheet: CS - CS
    total_gs_points = 0  # goalkeeper saves: GS - GS
    total_ps_points = 0  # penalty save: PS - PS
    total_pm_points = 0  # penalty miss: PM - PM
    total_yc_points = 0  # yellow card: Y - YC
    total_rc_points = 0  # red card: R - RC
    total_og_points = 0  # own goals: OG - OG
    total_sgs_points = 0 # shots at goal: SGS - SGS
    total_fs_points = 0  # fouls received: FS - FS
    total_pss_points = 0 # pass: P - PSS
    total_crs_points = 0 # crosses: CRS - CRS
    total_kp_points = 0  # key pass: KP - KP
    total_cl_points = 0  # clearance: CL - CL
    total_wf_points = 0  # Fouls against: WF - WF

    # Check player positions once from fantasy_stats
    is_defender = 'Defender' in fantasy_stats['positions']
    is_goalkeeper = 'Goalkeeper' in fantasy_stats['positions']
    is_midfielder = 'Midfielder' in fantasy_stats['positions']
    is_defender_or_goalkeeper = is_defender or is_goalkeeper

    for game in game_stats:
        goals_conceded = game['stats'].get('GC', 0)
        min_played = game['stats'].get('MIN', 0)
        
        # Minutes played points
        if min_played <= 60:
            min_points = 1  # 1 point for playing up to 60 minutes
        else:
            min_points = 2  # 2 points for playing over 60 minutes
            
        # Goal points
        gl_points = game['stats'].get('GL', 0)
        if is_defender_or_goalkeeper:
            gl_points = gl_points * 6  # 6 points for defenders/goalkeepers
        else:
            gl_points = gl_points * 5  # 5 points for others
            
        # Goals conceded (for defenders and goalkeepers only)
        if is_defender_or_goalkeeper:
            gc_points = math.floor(game['stats'].get('GC', 0) / 2) * -1
        else:
            gc_points = 0
        
        # Clean sheet points (60+ minutes and no goals conceded)
        if min_played >= 60 and goals_conceded == 0:
            if is_defender_or_goalkeeper:
                cs_points = 5  # 5 points for defenders or goalkeepers with a clean sheet
            elif is_midfielder:
                cs_points = 1  # 1 point for midfielders with a clean sheet
            else:
                cs_points = 0  # No points for other positions
        else:
            cs_points = 0
            
        # Goalkeeper specific points
        if is_goalkeeper:
            gs_points = math.floor(game['stats'].get('GS', 0) // 4 ) # Every 4 saves = 1 point
            ps_points = math.floor(game['stats'].get('PS', 0) * 5)  # 5 points for every penalty save
        else:
            gs_points = 0
            ps_points = 0
            
        # Other stats points
        pm_points = math.floor(game['stats'].get('PM', 0) * -2)
        og_points = math.floor(game['stats'].get('OG', 0) * -2)
        sgs_points = math.floor(game['stats'].get('SGS', 0) // 4)
        fs_points = math.floor(game['stats'].get('FS', 0) // 4)
        # passes are supposed to be only if 84% accuracy but we don't have that stat
        pss_points = math.floor(game['stats'].get('PSS', 0) // 35)
        crs_points = math.floor(game['stats'].get('CRS', 0) // 3)
        kp_points = math.floor(game['stats'].get('KP', 0) // 4)
        cl_points = math.floor(game['stats'].get('CL', 0) // 4)
        wf_points = math.floor(game['stats'].get('WF', 0) // 4 * -1)
        ass_points = math.floor(game['stats'].get('ASS', 0) * 3)
        yc_points = math.floor(game['stats'].get('YC', 0) * -1)
        rc_points = math.floor(game['stats'].get('RC', 0) * -3)

        # Accumulate totals
        total_min_points += min_points
        total_gl_points += gl_points
        total_ass_points += ass_points
        total_yc_points += yc_points
        total_rc_points += rc_points
        total_gc_points += gc_points
        total_cs_points += cs_points
        total_gs_points += gs_points
        total_ps_points += ps_points
        total_pm_points += pm_points
        total_og_points += og_points
        total_sgs_points += sgs_points
        total_fs_points += fs_points
        total_pss_points += pss_points
        total_crs_points += crs_points
        total_kp_points += kp_points
        total_cl_points += cl_points
        total_wf_points += wf_points

    # Calculate total points
    total_points = (
        total_min_points +
        total_gl_points + 
        total_ass_points + 
        total_yc_points + 
        total_rc_points + 
        total_gc_points +
        total_cs_points + 
        total_gs_points + 
        total_ps_points + 
        total_pm_points + 
        total_og_points +
        total_sgs_points + 
        total_fs_points + 
        total_pss_points + 
        total_crs_points +
        total_kp_points + 
        total_cl_points + 
        total_wf_points
    )
    
    # At the end, add the Team Name to your return dictionary:
    squad_id = fantasy_stats.get('squad_id', 0)
    team_name = team_dict.get(squad_id, {}).get('name', 'Unknown Team')

    # Prepare data for CSV export
    return {
        'Player ID': fantasy_stats['id'],
        'Name': f"{fantasy_stats['first_name']} {fantasy_stats['last_name']}",
        'Team': team_name,  # Add team name here
        'Cost': f"${fantasy_stats['cost'] / 1_000_000:.1f}M",  # Format as million with one decimal place
        'Total Points': fantasy_stats['total_points'],
        'Average Points': fantasy_stats['avg_points'],
        'Owned By': f"{fantasy_stats['owned_by']:.2f}%",
        'High Score': fantasy_stats['high_score'],
        'Low Score': fantasy_stats['low_score'],
        'Positions': ', '.join(map(str, fantasy_stats['positions'])),
        'Total MIN Points': total_min_points,
        'Total GL Points': total_gl_points,
        'Total ASS Points': total_ass_points,
        'Total YC Points': total_yc_points,
        'Total RC Points': total_rc_points,
        'Total GC Points': total_gc_points,
        'Total CS Points': total_cs_points,
        'Total GS Points': total_gs_points,
        'Total PS Points': total_ps_points,
        'Total PM Points': total_pm_points,
        'Total OG Points': total_og_points,
        'Total SGS Points': total_sgs_points,
        'Total FS Points': total_fs_points,
        'Total PSS Points': total_pss_points,
        #'Total APS Points': total_aps_points,
        'Total CRS Points': total_crs_points,
        'Total KP Points': total_kp_points,
       # 'Total ASG Points': total_asg_points,
        #'Total SH Points': total_sh_points,
        'Total CL Points': total_cl_points,
       # 'Total INT Points': total_int_points,
        'Total WF Points': total_wf_points,
        'Total Combined Points': total_points
    }

def export_to_csv(player_data_list, filename='player_stats.csv'):
    """Export all player data to a CSV file."""
    if not player_data_list:
        return

    field_names = player_data_list[0].keys()

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(player_data_list)

    print(f"Data exported for {len(player_data_list)} players to '{filename}'")

def generate_weekly_data(all_player_data, all_game_stats, all_team_data):
    """Generate weekly CSV files from game data."""
    print("\nGenerating weekly data...")
    
    # Group games by week
    weekly_data = {}
    
    for player_id, games in all_game_stats.items():
        fantasy_stats = extract_fantasy_stats(all_player_data, player_id)
        if not fantasy_stats:
            continue
            
        for game in games:
            match_id = game.get('match_id')
            if not match_id:
                continue
                
            week = determine_week_from_match_id(match_id)
            
            if week not in weekly_data:
                weekly_data[week] = {}
            
            if player_id not in weekly_data[week]:
                weekly_data[week][player_id] = {
                    'fantasy_stats': fantasy_stats,
                    'games': [],
                    'total_points': 0
                }
            
            # Calculate points for this individual game
            game_points = calculate_game_points([game], fantasy_stats)
            weekly_data[week][player_id]['games'].append(game)
            weekly_data[week][player_id]['total_points'] += game_points
    
    # Create weekly CSV files
    os.makedirs('app/weekly_data', exist_ok=True)
    
    for week, players_data in weekly_data.items():
        week_filename = f"app/weekly_data/{week.lower().replace(' ', '_')}_stats.csv"
        weekly_player_list = []
        
        for player_id, player_data in players_data.items():
            fantasy_stats = player_data['fantasy_stats']
            games = player_data['games']
            
            if not games:
                continue
            
            # Calculate aggregate stats for the week
            total_stats = {}
            for game in games:
                for stat, value in game['stats'].items():
                    total_stats[stat] = total_stats.get(stat, 0) + (value or 0)
            
            # Get team name
            squad_id = fantasy_stats.get('squad_id', 0)
            team_name = all_team_data.get(squad_id, {}).get('name', 'Unknown Team')
            
            weekly_row = {
                'Player ID': player_id,
                'Name': f"{fantasy_stats['first_name']} {fantasy_stats['last_name']}",
                'Team': team_name,
                'Cost': f"${fantasy_stats['cost'] / 1_000_000:.1f}M",
                'Positions': ', '.join(map(str, fantasy_stats['positions'])),
                'Games Played': len(games),
                'Total Points': player_data['total_points'],
                'Average Points': round(player_data['total_points'] / len(games), 2) if games else 0,
                'Goals': total_stats.get('GL', 0),
                'Assists': total_stats.get('ASS', 0),
                'Minutes': total_stats.get('MIN', 0),
                'Yellow Cards': total_stats.get('YC', 0),
                'Red Cards': total_stats.get('RC', 0),
                'Clean Sheets': total_stats.get('CS', 0),
                'Goals Conceded': total_stats.get('GC', 0),
                'Shots on Goal': total_stats.get('SGS', 0),
                'Key Passes': total_stats.get('KP', 0)
            }
            
            weekly_player_list.append(weekly_row)
        
        if weekly_player_list:
            export_to_csv(weekly_player_list, week_filename)
    
    print(f"Generated weekly data for {len(weekly_data)} weeks")
    return weekly_data

def calculate_game_points(game_stats, fantasy_stats):
    """Calculate fantasy points for specific games (used for weekly data)."""
    total_points = 0
    
    # Check player positions
    is_defender = 'Defender' in fantasy_stats['positions']
    is_goalkeeper = 'Goalkeeper' in fantasy_stats['positions']
    is_midfielder = 'Midfielder' in fantasy_stats['positions']
    is_defender_or_goalkeeper = is_defender or is_goalkeeper
    
    for game in game_stats:
        goals_conceded = game['stats'].get('GC', 0)
        min_played = game['stats'].get('MIN', 0)
        
        # Minutes played points
        if min_played <= 60:
            total_points += 1
        else:
            total_points += 2
            
        # Goal points
        gl_points = game['stats'].get('GL', 0)
        if is_defender_or_goalkeeper:
            total_points += gl_points * 6
        else:
            total_points += gl_points * 5
            
        # Goals conceded (for defenders and goalkeepers only)
        if is_defender_or_goalkeeper:
            total_points += math.floor(goals_conceded / 2) * -1
        
        # Clean sheet points
        if min_played >= 60 and goals_conceded == 0:
            if is_defender_or_goalkeeper:
                total_points += 5
            elif is_midfielder:
                total_points += 1
        
        # Goalkeeper specific points
        if is_goalkeeper:
            total_points += math.floor(game['stats'].get('GS', 0) // 4)
            total_points += math.floor(game['stats'].get('PS', 0) * 5)
        
        # Other stats
        total_points += math.floor(game['stats'].get('PM', 0) * -2)
        total_points += math.floor(game['stats'].get('OG', 0) * -2)
        total_points += math.floor(game['stats'].get('SGS', 0) // 4)
        total_points += math.floor(game['stats'].get('FS', 0) // 4)
        total_points += math.floor(game['stats'].get('PSS', 0) // 35)
        total_points += math.floor(game['stats'].get('CRS', 0) // 3)
        total_points += math.floor(game['stats'].get('KP', 0) // 4)
        total_points += math.floor(game['stats'].get('CL', 0) // 4)
        total_points += math.floor(game['stats'].get('WF', 0) // 4 * -1)
        total_points += math.floor(game['stats'].get('ASS', 0) * 3)
        total_points += math.floor(game['stats'].get('YC', 0) * -1)
        total_points += math.floor(game['stats'].get('RC', 0) * -3)
    
    return total_points

def main():
    print("MLS Fantasy Data Generator")
    print("=" * 40)
    
    # Fetch all team data once
    print("Fetching team data...")
    all_team_data = fetch_all_team_data()
    
    # Fetch all player data once
    print("Fetching player data...")
    all_player_data = fetch_all_player_data()
    
    # Extract player IDs
    player_ids = [player['id'] for player in all_player_data]
    
    # Process all players for complete data
    print(f"Processing {len(player_ids)} players...")
    
    # Fetch game stats for all players at once
    print("Fetching game stats for all players...")
    all_game_stats = fetch_all_game_stats(player_ids)
    
    # Generate season totals (original functionality)
    print("\nGenerating season totals...")
    player_results = []
    for player_id in player_ids:
        fantasy_stats = extract_fantasy_stats(all_player_data, player_id)
        game_stats = all_game_stats.get(player_id, [])
        
        if fantasy_stats and game_stats:
            player_result = calculate_player_points(game_stats, fantasy_stats, all_team_data)
            player_results.append(player_result)
    
    # Export season totals to main CSV
    export_to_csv(player_results, 'player_stats.csv')
    
    # Generate weekly data
    weekly_data = generate_weekly_data(all_player_data, all_game_stats, all_team_data)
    
    print(f"\n✅ Generation complete!")
    print(f"📊 Season totals: player_stats.csv ({len(player_results)} players)")
    print(f"📅 Weekly data: app/weekly_data/ ({len(weekly_data)} weeks)")
    print(f"🎯 Ready for weekly filtering in your app!")

if __name__ == '__main__':
    main()