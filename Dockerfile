# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8505

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port","8505","--logger.level=debug","--server.enableCORS=true", "--server.address","0.0.0.0"]

