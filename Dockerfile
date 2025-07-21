# 基於官方 Python 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製後端程式碼
COPY backend/ ./backend/

# 安裝依賴
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -v -r backend/requirements.txt && \
    pip show flask_jwt_extended

# 設定環境變數（可依需求調整）
ENV FLASK_APP=backend/run.py
ENV FLASK_ENV=production

# 開放 Flask 預設埠
EXPOSE 5000

# 啟動指令
CMD ["python", "-m", "backend.run"]
