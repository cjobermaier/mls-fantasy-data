import requests
import math
import csv

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
    total_min_points = 0
    total_gl_points = 0
    total_ass_points = 0
    total_gc_points = 0
    total_cs_points = 0
    total_gs_points = 0
    total_ps_points = 0
    total_pm_points = 0
    total_yc_points = 0
    total_rc_points = 0
    total_og_points = 0
    total_sgs_points = 0
    total_fs_points = 0
    total_pss_points = 0
    total_aps_points = 0
    total_crs_points = 0
    total_kp_points = 0
    total_asg_points = 0
    total_sh_points = 0
    total_cl_points = 0
    total_int_points = 0
    total_wf_points = 0

    for game in game_stats:
        is_midfielder = 'MF' in game['stats'].get('positions', [])
        goals_conceded = game['stats'].get('GC', 0)
        min_played = game['stats'].get('MIN', 0)
        
        # Minutes played points
        if min_played <= 60:
            min_points = 1  # 1 point for playing up to 60 minutes
        else:
            min_points = 2  # 2 points for playing over 60 minutes
            
        # Goals points
        gl_points = game['stats'].get('GL', 0)
        is_defender_or_goalkeeper = 'DEF' in fantasy_stats['positions'] or 'GK' in fantasy_stats['positions']
        if is_defender_or_goalkeeper:
            gl_points = gl_points * 6  # 6 points for defenders/goalkeepers
        else:
            gl_points = gl_points * 5  # 5 points for others
            
        # Other points calculations
        ass_points = game['stats'].get('ASS', 0) * 3
        yc_points = game['stats'].get('YC', 0) * -1
        rc_points = game['stats'].get('RC', 0) * -3
        gc_points = game['stats'].get('GC', 0) * -1
        
        # Clean sheet points
        if min_played >= 60 and goals_conceded == 0:
            if is_defender_or_goalkeeper:
                cs_points = 5  # 5 points for defenders or goalkeepers with a clean sheet
            elif is_midfielder:
                cs_points = 1  # 1 point for midfielders with a clean sheet
            else:
                cs_points = 0  # No points for other positions
        else:
            cs_points = 0  # No points if less than 60 minutes or goals conceded
            
        # Goalkeeper specific points
        is_goalkeeper = 'GK' in game['stats'].get('positions', [])
        if is_goalkeeper:
            gs_points = game['stats'].get('GS', 0) // 4  # Every 4 saves = 1 point
            ps_points = game['stats'].get('PS', 0) * 5  # 5 points for every PS
        else:
            gs_points = 0
            ps_points = 0
            
        # Other stats points
        pm_points = game['stats'].get('PM', 0) * -2
        og_points = game['stats'].get('OG', 0) * -2
        sgs_points = game['stats'].get('SGS', 0) // 4
        fs_points = game['stats'].get('FS', 0) // 4
        pss_points = math.floor(game['stats'].get('PSS', 0) / 10)
        aps_points = math.floor(game['stats'].get('APS', 0) / 10)
        crs_points = game['stats'].get('CRS', 0) * 1
        kp_points = math.floor(game['stats'].get('KP', 0) / 4)
        asg_points = game['stats'].get('ASG', 0) * 2
        sh_points = math.floor(game['stats'].get('SH', 0) / 2)
        cl_points = game['stats'].get('CL', 0) * 2
        int_points = game['stats'].get('INT', 0) * 1
        wf_points = game['stats'].get('WF', 0) // 4 * -1

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
        total_aps_points += aps_points
        total_crs_points += crs_points
        total_kp_points += kp_points
        total_asg_points += asg_points
        total_sh_points += sh_points
        total_cl_points += cl_points
        total_int_points += int_points
        total_wf_points += wf_points

    # Calculate total points
    total_points = (
        total_gl_points + total_kp_points + total_ass_points + total_yc_points + total_gc_points +
        total_cs_points + total_gs_points + total_ps_points + total_pm_points + total_og_points +
        total_sgs_points + total_fs_points + total_pss_points + total_aps_points + total_crs_points +
        total_asg_points + total_sh_points + total_cl_points + total_int_points + total_wf_points
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
        'Total APS Points': total_aps_points,
        'Total CRS Points': total_crs_points,
        'Total KP Points': total_kp_points,
        'Total ASG Points': total_asg_points,
        'Total SH Points': total_sh_points,
        'Total CL Points': total_cl_points,
        'Total INT Points': total_int_points,
        'Total WF Points': total_wf_points,
        'Total Combined Points': total_points
    }

def export_to_csv(player_data_list):
    """Export all player data to a CSV file."""
    if not player_data_list:
        return

    field_names = player_data_list[0].keys()

    with open('player_stats.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(player_data_list)

    print(f"Data exported for {len(player_data_list)} players to 'player_stats.csv'")

def main():
    # Fetch all team data once
    all_team_data = fetch_all_team_data()
    
    # Fetch all player data once
    all_player_data = fetch_all_player_data()
    
    # Extract player IDs
    player_ids = [player['id'] for player in all_player_data]
    
    # Limit to the first 50 player IDs for testing
    player_ids = player_ids[:5]  # Adjust as needed
    
    # Fetch game stats for all players at once
    all_game_stats = fetch_all_game_stats(player_ids)
    
    # Process each player and collect the results
    player_results = []
    for player_id in player_ids:
        fantasy_stats = extract_fantasy_stats(all_player_data, player_id)
        game_stats = all_game_stats.get(player_id, [])
        
        if fantasy_stats and game_stats:
            player_result = calculate_player_points(game_stats, fantasy_stats, all_team_data)
            player_results.append(player_result)
    
    # Export all player data at once
    export_to_csv(player_results)

if __name__ == '__main__':
    main()