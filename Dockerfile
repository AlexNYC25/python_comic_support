# Use an official Python runtime as a base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install unrar and p7zip-full for handling rar and 7z files
RUN apt-get update && apt-get install -y \
    unrar-free \
    p7zip-full

# Set the environment variable to include /usr/bin
ENV PATH="/usr/bin:${PATH}"

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Dockerfile command section
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "run:app"]

