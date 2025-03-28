FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser
USER appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env /app/.env
COPY src/ ./src

# Add src to PYTHONPATH so internal modules can be imported
ENV PYTHONPATH=/app/src

EXPOSE 5000

# Run as a module so that imports like 'from logic.xxx' work
ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "src/main.py"]