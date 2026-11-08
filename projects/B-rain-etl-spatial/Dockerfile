# 映像標籤固定到 patch 版本（不用 :latest）。此標籤未在建置環境驗證（Docker Hub 被擋），
# 請在 WSL2 先 `docker pull` 確認存在；正式環境建議再釘 digest（python:...@sha256:...）。
FROM python:3.13.18-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 RAINB_WORK_DIR=/tmp/rainb
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY tests/ tests/

# 非 root 使用者（UID 固定，k8s 的 runAsUser 對應這個值）
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER 10001
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uvicorn", "rainb.api:default_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
