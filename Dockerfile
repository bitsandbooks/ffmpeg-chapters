FROM python:3.11-slim

# Install dependencies (ffmpeg, obviously) and clean up afterward
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Security best practice: non-root user to run the container
RUN useradd -m appuser
USER appuser

# Set the working directory inside the container
WORKDIR /data

# Copy Python script into the container
# DON'T FORGET TO LINT IT FIRST!
COPY makechapters.py /app/

# Define the default command that runs when the container starts
ENTRYPOINT ["python", "/app/makechapters.py"]