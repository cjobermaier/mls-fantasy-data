import csv
import json
import math
import requests


def load_game_stats():
    # Simulate all game stats including individual matches and 'all' round
    return [
        {'match_id': 20250115, 'stats': {'MIN': 90, 'GL': 2, 'ASS': 0, 'GC': 0, 'CS': 1, 'GS': 0, 'PS': 0, 'PM': 0, 'YC': 0, 'RC': 0, 'OG': 0, 'SGS': 3, 'FS': 2, 'PSS': 36, 'APS': 30, 'CRS': 0, 'KP': 5, 'ASG': 1, 'SH': 4, 'CL': 0, 'INT': 0, 'WF': 1}},
        {'match_id': 20250210, 'stats': {'MIN': 90, 'GL': 0, 'ASS': 0, 'GC': 0, 'CS': 1, 'GS': 0, 'PS': 0, 'PM': 0, 'YC': 0, 'RC': 0, 'OG': 0, 'SGS': 2, 'FS': 1, 'PSS': 50, 'APS': 40, 'CRS': 3, 'KP': 8, 'ASG': 3, 'SH': 5, 'CL': 0, 'INT': 0, 'WF': 0}},
        {'match_id': 20250310, 'stats': {'MIN': 90, 'GL': 1, 'ASS': 0, 'GC': 1, 'CS': 0, 'GS': 0, 'PS': 0, 'PM': 0, 'YC': 0, 'RC': 0, 'OG': 0, 'SGS': 4, 'FS': 0, 'PSS': 29, 'APS': 27, 'CRS': 1, 'KP': 18, 'ASG': 7, 'SH': 11, 'CL': 0, 'INT': 0, 'WF': 0}}
    ]

def load_data_from_url(url):
    """Load data from a public S3 bucket URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

def search_player(data, search_term):
    results = []
    for player in data:
        first_name = player.get('first_name', '').lower() if player.get('first_name') else ''
        last_name = player.get('last_name', '').lower() if player.get('last_name') else ''
        known_name = player.get('known_name', '').lower() if player.get('known_name') else ''
        player_id = str(player.get('id', ''))

        if (search_term.lower() == player_id or
            search_term.lower() == first_name or
            search_term.lower() == last_name or
            search_term.lower() == known_name):
            results.append(player)
    return results

def combine_stats(player_id):
    # Load data from the URL
    url = 'https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741804692858'
    data = load_data_from_url(url)
    
    if data is None:
        print("Failed to load player data.")
        return

    # Search for the player by id
    player_data = search_player(data, player_id)
    
    if not player_data:
        print(f"Player with ID {player_id} not found.")
        return

    # Assuming the first player is the one we want (adjust if necessary)
    player = player_data[0]
    fantasy_stats = {
        'id': player['id'],
        'first_name': player.get('first_name', 'N/A'),
        'last_name': player.get('last_name', 'N/A'),
        'cost': player.get('cost', 0),
        'total_points': player.get('total_points', 0),
        'avg_points': player.get('avg_points', 0),
        'owned_by': player.get('owned_by', 0),
        'high_score': player.get('high_score', 0),
        'low_score': player.get('low_score', 0),
        'positions': player.get('positions', []),
    }

    print(f"Fantasy Stats for Player: {fantasy_stats}")

    game_stats = load_game_stats()

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
        min_points = math.floor(game['stats']['MIN'] / 60)
        gl_points = game['stats']['GL'] * 5
        ass_points = game['stats']['ASS'] * 3
        yc_points = game['stats']['YC'] * -1
        gc_points = game['stats']['GC'] * -1
        cs_points = game['stats']['CS'] * 4
        gs_points = game['stats']['GS'] * 2
        ps_points = math.floor(game['stats']['PS'] / 10)
        pm_points = game['stats']['PM'] * -1
        og_points = game['stats']['OG'] * -2
        sgs_points = game['stats']['SGS'] * 1
        fs_points = game['stats']['FS'] * -1
        pss_points = math.floor(game['stats']['PSS'] / 10)
        aps_points = math.floor(game['stats']['APS'] / 10)
        crs_points = game['stats']['CRS'] * 1
        kp_points = math.floor(game['stats']['KP'] / 4)
        asg_points = game['stats']['ASG'] * 2
        sh_points = math.floor(game['stats']['SH'] / 2)
        cl_points = game['stats']['CL'] * 2
        int_points = game['stats']['INT'] * 1
        wf_points = game['stats']['WF'] * 0.5

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

    print(f"Player: {fantasy_stats['first_name']} {fantasy_stats['last_name']}")
    print(f"Cost: {fantasy_stats['cost']} points")
    print(f"Total Combined Points: {total_points}")

    return total_points

def main():
    player_id = input('Enter the player ID to search: ')
    total_points = combine_stats(player_id)

if __name__ == '__main__':
    main()
