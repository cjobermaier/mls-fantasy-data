import requests
import json
import csv

def load_data_from_url(url):
    """Load data from a public S3 bucket URL."""
    response = requests.get(url)
    if response.status_code == 200:
        # Assuming the content is JSON
        return response.json()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

def search_player(data, search_term):
    """Search player data by id, first_name, last_name, or known_name."""
    results = []
    for player in data:
        # Ensure the comparison fields are either empty strings or strings
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

def export_to_csv(results, filename):
    """Export search results to a CSV file."""
    if not results:
        print("No results to export.")
        return
    
    # Open a CSV file in write mode
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        
        # Write header
        writer.writeheader()
        
        # Write player data
        for player in results:
            writer.writerow(player)
    
    print(f"Data has been exported to {filename}")

url = 'https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741804692858'
data = load_data_from_url(url)

if data:
    # Let the user input a search term (id, first_name, last_name, or known_name)
    search_term = input("Enter player id, first name, last name, or known name to search: ").strip()

    # Search for players
    results = search_player(data, search_term)

    # Export the results to CSV
    export_to_csv(results, "search_results.csv")