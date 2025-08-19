from flask import Flask, render_template, request, jsonify
import os
from data_service import get_player_stats, get_player_by_id, compare_players, get_weekly_player_stats, get_available_weeks, compare_players_weekly

app = Flask(__name__)

@app.route('/')
def display_stats():
    """Render the main page with player statistics."""
    week = request.args.get('week')
    data = get_weekly_player_stats(week) if week else get_player_stats()
    available_weeks = get_available_weeks()
    ga_id = os.environ.get('GA_MEASUREMENT_ID', '')
    return render_template('index.html', data=data, available_weeks=available_weeks, 
                         selected_week=week, ga_measurement_id=ga_id)

@app.route('/api/players')
def get_players_api():
    """API endpoint to return player data as JSON."""
    data = get_player_stats()
    return jsonify(data)

@app.route('/compare')
def compare_page():
    """Render the player comparison page."""
    week = request.args.get('week')
    data = get_weekly_player_stats(week) if week else get_player_stats()
    available_weeks = get_available_weeks()
    ga_id = os.environ.get('GA_MEASUREMENT_ID', '')
    return render_template('compare.html', data=data, available_weeks=available_weeks,
                         selected_week=week, ga_measurement_id=ga_id)

@app.route('/api/compare')
def compare_api():
    """API endpoint to compare players."""
    player_ids = request.args.getlist('players')
    week = request.args.get('week')
    
    if len(player_ids) < 2:
        return jsonify({'error': 'At least 2 players required for comparison'}), 400
    
    if week:
        comparison_data = compare_players_weekly(player_ids, week)
    else:
        comparison_data = compare_players(player_ids)
    
    return jsonify(comparison_data)

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