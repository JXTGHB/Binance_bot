# -------------------------------
# Dockerfile
# -------------------------------
FROM python:3.11-bullseye

# 設定工作目錄
WORKDIR /app

# 複製依賴清單
COPY requirements.txt .

# 安裝必要套件
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && update-ca-certificates
# 複製專案程式碼
COPY . /app

# 設定環境變數（讓 .env 也能被載入）
ENV PYTHONUNBUFFERED=1

# 對外開放 FastAPI port
EXPOSE 8000

# 啟動伺服器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
