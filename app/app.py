from flask import Flask, render_template
import csv
import os

app = Flask(__name__)

# Define the route to display the CSV data
@app.route('/')
def display_stats():
    data = []
    # Use an absolute path to the CSV file in the Docker container
    csv_file_path = os.path.join(os.path.dirname(__file__), 'player_stats.csv')
    
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
