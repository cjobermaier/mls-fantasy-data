import requests
import json
import csv

# Read data from a CSV file
def read_csv_data(filename):
    data = []
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def find_player_id(search_value, data):
    # Convert the search value to lowercase for case-insensitive comparison
    search_value = search_value.lower()

    # Iterate through each player record in the data
    for player in data:
        # Check if the search value (in lowercase) matches any of the four fields (also in lowercase)
        if any(search_value in str(field).lower() for field in player):
            return player[0]  # Return the id (the first element in the list)
    return None  # If no match is found

# Test the function
# Get the search value from the user
search_value = input("Enter the player's name or ID to search: ")

# Load data from the CSV file (replace 'players.csv' with your actual CSV filename)
data = read_csv_data('players_ids.csv')

# Find the player ID based on the user input
player_id = find_player_id(search_value, data)  # Pass 'data' here as the second argument

if player_id:
    print(f"Player ID for '{search_value}': {player_id}")
else:
    print(f"Player '{search_value}' not found.")

# URL for the JSON data from S3
url = f"https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/stats/players/{player_id}.json?_=1741793495420"
response = requests.get(url)

# Check if the request was successful 
if response.status_code == 200:
    # Load the response data as JSON
    players_data = response.json()

    # Process each player in the JSON data
    for player in players_data:
        # Extract player details
        values = [
            player.get("id", ""),
            player.get("sportec_id", ""),
            player.get("first_name", ""),
            player.get("last_name", ""),
            player.get("known_name", ""),
            player.get("squad_id", ""),
            player.get("cost", ""),
            player.get("status", ""),
            player.get("stats", {}).get("round_rank", ""),
            player.get("stats", {}).get("season_rank", ""),
            player.get("stats", {}).get("games_played", ""),
            player.get("stats", {}).get("total_points", ""),
            player.get("stats", {}).get("avg_points", ""),
            player.get("stats", {}).get("high_score", ""),
            player.get("stats", {}).get("low_score", ""),
            player.get("stats", {}).get("last_3_avg", ""),
            player.get("stats", {}).get("last_5_avg", ""),
            player.get("stats", {}).get("selections", ""),
            player.get("stats", {}).get("owned_by", ""),
            player.get("stats", {}).get("projected_scores", {}).get("20250409", ""),
            player.get("positions", [])[0] if player.get("positions") else ""
        ]

    print(players_data)
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")