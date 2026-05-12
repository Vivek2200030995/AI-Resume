FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create upload directory and set permissions
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# Expose the app port
EXPOSE 5000

# Use production settings by default
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Start Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120"]
