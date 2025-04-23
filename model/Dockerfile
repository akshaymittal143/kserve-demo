FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy model and server code
COPY model_files/model.joblib /app/model.joblib
COPY model_server.py /app/

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "model_server.py"]