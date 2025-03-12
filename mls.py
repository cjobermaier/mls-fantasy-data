import requests
import json

# URL for the JSON data from S3
url = "https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741793495420"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Load the response data as JSON
    players_data = response.json()

    # CSV Header
    csv_data = [
        "id", "sportec_id", "first_name", "last_name", "known_name", "squad_id", "cost", "status",
        "round_rank", "season_rank", "games_played", "total_points", "avg_points", "high_score", 
        "low_score", "last_3_avg", "last_5_avg", "selections", "owned_by", "projected_scores_20250409",
        "position"
    ]

    # Prepare an empty list to store all players' data
    all_players_data = []

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

        # Append player values to the list
        all_players_data.append(values)

    # Create CSV format string
    header = ",".join(csv_data)
    rows = "\n".join([",".join(str(value) for value in player) for player in all_players_data])

    # Combine header and rows
    csv_output = f"{header}\n{rows}"

    # Write the CSV data to a file
    with open('players_data.csv', 'w') as file:
        file.write(csv_output)

    print("CSV file saved as 'players_data.csv'.")

else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
