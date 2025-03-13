# Use an official Nginx image to serve the files
FROM nginx:alpine

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip python3-dev build-base

# Create a virtual environment
RUN python3 -m venv /venv

# Install Flask within the virtual environment
RUN /venv/bin/pip install flask

# Set up the working directory
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Copy the CSV file into the container
COPY player_stats.csv /app/

# Expose the port the app will run on
EXPOSE 80

# Set the entrypoint to use the virtual environment
CMD ["/venv/bin/python", "app.py"]
