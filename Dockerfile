FROM python:3.12-slim

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./backend .

# Make sure the entry point can be executed
RUN chmod +x app.py

EXPOSE 5000

CMD ["python", "app.py"]