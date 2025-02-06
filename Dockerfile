# Use official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
