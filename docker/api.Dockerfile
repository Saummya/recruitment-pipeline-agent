FROM python:3.12-slim
WORKDIR /code

# Copy requirements first: Docker caches this layer,
# so rebuilds are fast when only your code changes.
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]