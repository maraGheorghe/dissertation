# Use the official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the required files into the container
COPY api.py /app/
COPY requirments-docker.txt /app/requirments.txt

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
       git ffmpeg \
       && apt-get clean \
       && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirments.txt

# Expose the port that FastAPI (uvicorn) will run on
EXPOSE 8080

# Define the command to run your app with uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]