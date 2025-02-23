# Use official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (if necessary for an API)
EXPOSE 5000

# Define the command to run the pipeline
CMD ["python", "summarize.py", "data/"]

