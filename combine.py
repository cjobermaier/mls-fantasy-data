import requests
import math
import csv

def load_player_ids():
    # URL for the JSON data from S3 for player info
    url = "https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741793495420"
    
    # Fetch the data from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        players_data = response.json()

        # Extract player IDs
        player_ids = [player['id'] for player in players_data]
        return player_ids
    else:
        print(f"Failed to fetch player data, status code: {response.status_code}")
        return []


def load_game_stats(player_identification):
    # Dynamically generate the URL using player_identification
    url = f"https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/stats/players/{player_identification}.json?_=1741793495420"
    
    # Fetch the data from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Load the response data as JSON
        players_data = response.json()

        # Simulate extracting game stats from the JSON data
        game_stats = []
        for player in players_data:
            match_stats = player.get('stats', {})
            match_id = player.get('match_id', None)
            if match_id:
                game_stats.append({'match_id': match_id, 'stats': match_stats})
        return game_stats
    else:
        print(f"Failed to fetch game stats for player {player_identification}, status code: {response.status_code}")
        return []


def load_fantasy_stats(player_identification):
    # URL for the JSON data from S3 for fantasy stats
    url = f"https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741804692858"
    
    # Fetch the data from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        players_data = response.json()

        # Find the player's fantasy stats by matching the player ID
        for player in players_data:
            if player.get('id') == player_identification:
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
                    'positions': player.get('positions', [])
                }
    else:
        print(f"Failed to fetch fantasy stats data for player {player_identification}, status code: {response.status_code}")
        return {}


def combine_stats(player_identification):
    game_stats = load_game_stats(player_identification)
    fantasy_stats = load_fantasy_stats(player_identification)

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
        if min_played <= 60:
            min_points = 1  # 1 point for playing up to 60 minutes
        else:
            min_points = 2  # 2 points for playing over 60 minutes
    # Goals (GL) - 6 points for defenders or goalkeepers, else 5 points
        gl_points = game['stats'].get('GL', 0)
        # Determine if the player is a defender or goalkeeper
        is_defender_or_goalkeeper = 'DEF' in fantasy_stats['positions'] or 'GK' in fantasy_stats['positions']
        if is_defender_or_goalkeeper:
            gl_points = gl_points * 6  # 6 points for defenders/goalkeepers
        else:
            gl_points = gl_points * 5  # 5 points for others        
        ass_points = game['stats'].get('ASS', 0) * 3
        yc_points = game['stats'].get('YC', 0) * -1
        total_rc_points = game['stats'].get('RC', 0) * -3
        gc_points = game['stats'].get('GC', 0) * -1
        cs_points = game['stats'].get('CS', 0) * 4
        is_goalkeeper = 'GK' in game['stats'].get('positions', [])
        if is_goalkeeper:
            gs_points = game['stats'].get('GS', 0) // 4  # Every 4 saves = 1 point, positive for goalkeepers
            ps_points = game['stats'].get('PS', 0) * 5  # 5 points for every PS

        else:
            gs_points = 0  # No points for saves if not a goalkeeper 
            ps_points = 0      
        pm_points = game['stats'].get('PM', 0) * -2
        og_points = game['stats'].get('OG', 0) * -2
        sgs_points = game['stats'].get('SGS', 0) // 4
        fs_points = game['stats'].get('FS', 0) // 4  # Every 4 fouls = 1 point and rounds down
        pss_points = math.floor(game['stats'].get('PSS', 0) / 10)
        aps_points = math.floor(game['stats'].get('APS', 0) / 10)
        crs_points = game['stats'].get('CRS', 0) * 1
        kp_points = math.floor(game['stats'].get('KP', 0) / 4)
        asg_points = game['stats'].get('ASG', 0) * 2
        sh_points = math.floor(game['stats'].get('SH', 0) / 2)
        cl_points = game['stats'].get('CL', 0) * 2
        int_points = game['stats'].get('INT', 0) * 1
        wf_points = game['stats'].get('WF', 0) // 4 * -1
        # Check if player played 60 minutes or more and did not concede any goals
        if min_played >= 60 and goals_conceded == 0:
            if is_defender_or_goalkeeper:
                cs_points = 5  # 5 points for defenders or goalkeepers with a clean sheet
            elif is_midfielder:
                cs_points = 1  # 1 point for midfielders with a clean sheet
            else:
                cs_points = 0  # No points for other positions
        else:
            cs_points = 0  # No points if less than 60 minutes or goals conceded


        total_min_points += min_points
        total_gl_points += gl_points
        total_ass_points += ass_points
        total_yc_points += yc_points
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

    total_points = (
        total_gl_points + total_kp_points + total_ass_points + total_yc_points + total_gc_points +
        total_cs_points + total_gs_points + total_ps_points + total_pm_points + total_og_points +
        total_sgs_points + total_fs_points + total_pss_points + total_aps_points + total_crs_points +
        total_asg_points + total_sh_points + total_cl_points + total_int_points + total_wf_points
    )

    # Print the fantasy stats
    """ if fantasy_stats:
        print(f"Fantasy Stats for Player {player_identification}:")
        print(f"Player ID: {fantasy_stats['id']}")
        print(f"Name: {fantasy_stats['first_name']} {fantasy_stats['last_name']}")
        print(f"Cost: {fantasy_stats['cost']}")
        print(f"Total Points: {fantasy_stats['total_points']}")
        print(f"Average Points: {fantasy_stats['avg_points']}")
        print(f"Owned By: {fantasy_stats['owned_by']}%")
        print(f"High Score: {fantasy_stats['high_score']}")
        print(f"Low Score: {fantasy_stats['low_score']}")
        print(f"Positions: {fantasy_stats['positions']}") """

    # Prepare data for CSV export
    data = {
        'Player ID': fantasy_stats['id'],
        'Name': f"{fantasy_stats['first_name']} {fantasy_stats['last_name']}",
        'Cost': fantasy_stats['cost'],
        'Total Points': fantasy_stats['total_points'],
        'Average Points': fantasy_stats['avg_points'],
        'Owned By': fantasy_stats['owned_by'],
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

    # Export to CSV
    with open('player_stats.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if csvfile.tell() == 0:  # If file is empty, write the header
            writer.writeheader()
        writer.writerow(data)

    #print(f"Data exported for Player {player_identification} to 'player_stats.csv'")

    return total_points


def main():
    player_ids = load_player_ids()

    # Limit to the first 50 player IDs
    player_ids = player_ids[:50]  # Slice the list to the first 50 players

    for player_id in player_ids:
        combine_stats(player_id)



if __name__ == '__main__':
    main()
