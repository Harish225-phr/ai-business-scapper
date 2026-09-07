FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Update pip
RUN pip install --upgrade pip

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install playwright chromium browser without OS deps (since the base image already has them)
RUN playwright install chromium

# Copy app files
COPY . .

# Expose port
EXPOSE 10000

# Start app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "600", "app:app"]
