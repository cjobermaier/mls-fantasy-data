from flask import Flask, render_template, request, jsonify
import os
from data_service import get_player_stats

app = Flask(__name__)

@app.route('/')
def display_stats():
    """Render the main page with player statistics."""
    data = get_player_stats()
    ga_id = os.environ.get('GA_MEASUREMENT_ID', '')
    return render_template('index.html', data=data, ga_measurement_id=ga_id)

@app.route('/api/players')
def get_players_api():
    """API endpoint to return player data as JSON."""
    data = get_player_stats()
    return jsonify(data)

@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        if 'static' in request.path:
            # Cache static assets for 1 week
            response.headers['Cache-Control'] = 'public, max-age=604800'
        else:
            # No caching for dynamic content
            response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)