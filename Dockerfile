FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY . /code/

# Install dependencies via Poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Expose port
EXPOSE 8000

# Run Django server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
