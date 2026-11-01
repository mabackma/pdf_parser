FROM python:3.12-slim

# Pre-install Python dependencies so test runs are fast
WORKDIR /setup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default command runs tests (used by docker-compose for local dev)
CMD ["pytest", "tests/", "-v", "--tb=short"]
