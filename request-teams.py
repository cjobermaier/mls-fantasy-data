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
        for team_id, team_info in team_dict.items():
            print(f"Team ID: {team_id}, Name: {team_info['name']}, Short Name: {team_info['short_name']}")
        
        return team_dict
    else:
        print(f"Failed to fetch team data, status code: {response.status_code}")
        return {}


if __name__ == '__main__':
    fetch_all_team_data()
