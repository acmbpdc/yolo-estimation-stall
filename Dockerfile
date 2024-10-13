# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential

# Set the working directory in the container
WORKDIR /

# Copy the current directory contents into the container at /app
ADD . /

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run the application
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "myproject.wsgi", "--bind", "0.0.0.0:8000"]

