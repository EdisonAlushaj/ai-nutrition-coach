# In user_service/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app ./app

# Command to run the application when the container starts
# We expose port 8000 and bind to 0.0.0.0 to make it accessible
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]