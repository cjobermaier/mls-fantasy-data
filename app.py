from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

# Load data from the public S3 bucket URL
def load_data_from_url(url):
    """Load data from a public S3 bucket URL."""
    response = requests.get(url)
    if response.status_code == 200:
        # Assuming the content is JSON
        return response.json()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

# Search function to find players based on search term
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the search page and handle search queries."""
    url = 'https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1741804692858'
    data = load_data_from_url(url)  # Load data from the URL
    
    results = []
    
    if request.method == 'POST':
        # Get the search term from the form
        search_term = request.form.get('search_term', '').strip()
        if search_term:
            # Perform the search
            results = search_player(data, search_term)
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
