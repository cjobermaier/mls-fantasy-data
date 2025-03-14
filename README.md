# MLS Fantasy Data Viewer

A Flask web application for viewing and analyzing MLS Fantasy player statistics.

## Features

- Interactive data table with advanced sorting and filtering
- Column visibility toggles to customize your view
- Dark mode support
- Export to CSV functionality
- Filter players by position, stats, and price range
- Responsive design for mobile and desktop viewing

## JavaScript Architecture

The application uses a centralized initialization script (`init.js`) that:

1. Initializes the DataTable
2. Sets up filtering functionality
3. Manages column visibility
4. Handles dark mode preferences
5. Provides CSV export functionality

## Project Structure

```
app/
├── static/
│   ├── css/
│   │   ├── main.css        # Main stylesheet
│   │   └── dark-mode.css   # Dark mode styles
│   ├── js/
│   │   ├── table.js        # DataTable initialization and functionality
│   │   ├── filters.js      # Filter functionality
│   │   └── dark-mode.js    # Dark mode toggle
│   └── images/             # For any images you might add later
├── templates/
│   ├── base.html           # Base template with common elements
│   ├── index.html          # Main content template (extends base.html)
│   └── partials/           # For reusable template parts
│       ├── filters.html    # Filter section
│       └── table.html      # Table section
├── app.py                  # Flask application
├── data_service.py         # Service for handling data operations
├── player_stats.csv        # CSV data file
├── Dockerfile              # Docker configuration
├── fly.toml                # Fly.io configuration
└── nginx.conf              # Nginx configuration
```

## Setup and Running Locally

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Access the application at http://localhost:80

## Docker Deployment

Build and run with Docker:

```bash
docker build -t mls-fantasy-data .
docker run -p 80:80 mls-fantasy-data
```