# Use the official Python image from the Docker Hub
FROM python:3.12-bullseye

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the application
EXPOSE 80

# Run the application with Gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]
