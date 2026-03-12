# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies for OpenCV and general utilities
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt .

# Install dependencies (CPU versions to save space and cost on standard AWS instances)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code and the models directory
COPY backend /app/backend
COPY model /app/model

# Set the working directory to backend
WORKDIR /app/backend

# Expose port 8000
EXPOSE 8000

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
