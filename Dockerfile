# Use an official Python runtime as the base image
FROM python:3.11

RUN apt-get update && apt-get install -y ffmpeg

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Define environment variable for configuration file path
ENV BB_CONFIG_FILE_PATH="./BoatBuddy/sample-config.json"

# Set the default command to run your Flask app
CMD ["python3", "-m", "BoatBuddy"]
