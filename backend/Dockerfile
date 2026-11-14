FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements-runtime.txt backend/requirements-runtime.txt
COPY ml/requirements.txt ml/requirements.txt
RUN pip install --no-cache-dir --retries 8 --timeout 60 -r backend/requirements-runtime.txt
ARG INSTALL_ML=false
RUN if [ "$INSTALL_ML" = "true" ]; then pip install --no-cache-dir --retries 8 --timeout 60 -r ml/requirements.txt; fi
COPY backend backend
COPY ml ml
COPY scripts scripts
RUN useradd --create-home agrosphere && chown -R agrosphere:agrosphere /app
USER agrosphere
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
