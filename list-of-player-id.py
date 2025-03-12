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
        "id", "first_name", "last_name", "known_name"
    ]

    # Prepare an empty list to store all players' data
    all_players_data = []

    # Process each player in the JSON data
    for player in players_data:
        # Extract player details
        values = [
            player.get("id", ""),
            player.get("first_name", ""),
            player.get("last_name", ""),
            player.get("known_name", ""),
        ]

        # Append player values to the list
        all_players_data.append(values)
        #print(all_players_data)

    # Create CSV format string
    header = ",".join(csv_data)
    rows = "\n".join([",".join(str(value) for value in player) for player in all_players_data])

    # Combine header and rows
    csv_output = f"{header}\n{rows}"

    # Write the CSV data to a file
    with open('players_ids.csv', 'w') as file:
        file.write(csv_output)

    print("CSV file saved as 'players_ids.csv'.")

else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")