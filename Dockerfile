FROM python:3.13-slim

WORKDIR /app

# Copy ONLY requirements first — caching trick
COPY  requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app code
COPY . .

# Uvicorn needs to bind 0.0.0.0, not 127.0.0.1, to be reachable from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
