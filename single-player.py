import requests
import math
import csv

# mid 3
# defender 2
# forward
# keeper

def load_game_stats():
    # URL for the JSON data from S3 for game stats
    url = "https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/stats/players/1672.json?_=1741793495420"
    
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
        print(f"Failed to fetch data, status code: {response.status_code}")
        return []


def load_fantasy_stats():
    # URL for the JSON data from S3 for fantasy stats
    url = "https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741804692858"
    
    # Fetch the data from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Load the response data as JSON
        players_data = response.json()

        # Find a specific player's fantasy stats (Example: ID = 1672)
        for player in players_data:
            if player.get('id') == 1672:  # Example player ID
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
        print(f"Failed to fetch fantasy stats data, status code: {response.status_code}")
        return {}


def combine_stats(player_id):
    game_stats = load_game_stats()
    fantasy_stats = load_fantasy_stats()

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
        min_played = game['stats'].get('MIN', 0)
        if min_played <= 60:
            min_points = 1  # 1 point for playing up to 60 minutes
        else:
            min_points = 2  # 2 points for playing over 60 minutes
        gl_points = game['stats'].get('GL', 0) * 5
        ass_points = game['stats'].get('ASS', 0) * 3
        yc_points = game['stats'].get('YC', 0) * -1
        gc_points = game['stats'].get('GC', 0) * -1
        cs_points = game['stats'].get('CS', 0) * 4
        gs_points = game['stats'].get('GS', 0) * 2
        ps_points = math.floor(game['stats'].get('PS', 0) / 10)
        pm_points = game['stats'].get('PM', 0) * -1
        og_points = game['stats'].get('OG', 0) * -2
        sgs_points = game['stats'].get('SGS', 0) * 1
        fs_points = game['stats'].get('FS', 0) * -1
        pss_points = math.floor(game['stats'].get('PSS', 0) / 10)
        aps_points = math.floor(game['stats'].get('APS', 0) / 10)
        crs_points = game['stats'].get('CRS', 0) * 1
        kp_points = math.floor(game['stats'].get('KP', 0) / 4)
        asg_points = game['stats'].get('ASG', 0) * 2
        sh_points = math.floor(game['stats'].get('SH', 0) / 2)
        cl_points = game['stats'].get('CL', 0) * 2
        int_points = game['stats'].get('INT', 0) * 1
        wf_points = game['stats'].get('WF', 0) * 0.5

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

    # Print the fantasy stats (this is where you requested to see the data)
    if fantasy_stats:
        print("Fantasy Stats:")
        print(f"Player ID: {fantasy_stats['id']}")
        print(f"Name: {fantasy_stats['first_name']} {fantasy_stats['last_name']}")
        print(f"Cost: {fantasy_stats['cost']}")
        print(f"Total Points: {fantasy_stats['total_points']}")
        print(f"Average Points: {fantasy_stats['avg_points']}")
        print(f"Owned By: {fantasy_stats['owned_by']}%")
        print(f"High Score: {fantasy_stats['high_score']}")
        print(f"Low Score: {fantasy_stats['low_score']}")
        print(f"Positions: {fantasy_stats['positions']}")

    print(f"\nGame Stats Points:")
    print(f"Total MIN Points: {total_min_points}")
    print(f"Total GL Points: {total_gl_points}")
    print(f"Total ASS Points: {total_ass_points}")
    print(f"Total YC Points: {total_yc_points}")
    print(f"Total GC Points: {total_gc_points}")
    print(f"Total CS Points: {total_cs_points}")
    print(f"Total GS Points: {total_gs_points}")
    print(f"Total PS Points: {total_ps_points}")
    print(f"Total PM Points: {total_pm_points}")
    print(f"Total OG Points: {total_og_points}")
    print(f"Total SGS Points: {total_sgs_points}")
    print(f"Total FS Points: {total_fs_points}")
    print(f"Total PSS Points: {total_pss_points}")
    print(f"Total APS Points: {total_aps_points}")
    print(f"Total CRS Points: {total_crs_points}")
    print(f"Total KP Points: {total_kp_points}")
    print(f"Total ASG Points: {total_asg_points}")
    print(f"Total SH Points: {total_sh_points}")
    print(f"Total CL Points: {total_cl_points}")
    print(f"Total INT Points: {total_int_points}")
    print(f"Total WF Points: {total_wf_points}")
    print(f"Total Combined Points: {total_points}")

     # Prepare data for CSV export (exclude "Game Stats Points" and "Fantasy Stats")
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
    with open('player_stats.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

    print(f"Data exported to 'player_stats.csv'")

    return total_points


def main():
    player_id = input('Enter the player ID to search: ')
    total_points = combine_stats(player_id)

if __name__ == '__main__':
    main()
