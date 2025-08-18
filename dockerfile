# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN python -m pip install poetry

# Copy the project files into the container
COPY . /app

# Install dependencies using Poetry
RUN poetry install --no-root

# Expose port 5000 to the host
EXPOSE 5000

# Command to run the application
CMD ["poetry", "run", "examgen"]