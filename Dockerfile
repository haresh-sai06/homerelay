FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser && mkdir /app/data && chown appuser /app/data
COPY --chown=appuser:appuser homerelay ./homerelay
USER appuser
EXPOSE 8741
CMD ["python", "-m", "uvicorn", "homerelay.app:app", "--host", "0.0.0.0", "--port", "8741"]
