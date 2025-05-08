# Use the official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run the app with Gunicorn
CMD ["gunicorn", "-b", ":8080", "app:app"]
