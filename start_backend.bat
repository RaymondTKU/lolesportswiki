@echo off
echo 正在啟動英雄聯盟電競資訊網後端服務...
echo.

cd /d "%~dp0backend"

echo 檢查是否已安裝 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤：未找到 Python，請先安裝 Python 3.7+
    pause
    exit /b 1
)

echo 檢查是否已安裝依賴包...
if not exist "venv" (
    echo 創建虛擬環境...
    python -m venv venv
)

echo 啟動虛擬環境...
call venv\Scripts\activate

echo 安裝依賴包...
pip install -r requirements.txt

echo 初始化管理員帳號...
python init_admin.py

echo 檢查 MongoDB 連接...
echo 請確保 MongoDB 服務正在運行！
echo.

echo ========================================
echo 🚀 服務器啟動中...
echo 📡 API 地址: http://localhost:5000
echo 🔗 管理後台: http://localhost:5000/pages/admin.html
echo 🏠 前端頁面: http://localhost:5000/index.html
echo ========================================
echo.

echo 啟動 Flask 應用...
python run.py

pause
