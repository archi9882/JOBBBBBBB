# 同一個映像給 api 與 worker 使用，啟動指令由 compose 決定
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY tests/ tests/
ENV PYTHONPATH=/app/src FLOODSVC_DB=/data/floodsvc.db
RUN useradd --uid 10001 --create-home app && mkdir /data && chown app /data
USER app
EXPOSE 8000
CMD ["uvicorn", "floodsvc.api:app", "--host", "0.0.0.0", "--port", "8000"]
