# Use an official Python image as the base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the application port (5000 for Flask)
EXPOSE 5000

# Set the environment variable for Flask to use in production
ENV FLASK_ENV=production

# Start the Flask application using main.py
CMD ["python", "main.py"]
