FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app
WORKDIR /app

# Command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]