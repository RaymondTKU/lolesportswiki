# 英雄聯盟電競資訊網 - 安裝與執行指南

## 📋 系統需求

### 必要軟體
- **Python 3.7+** - [下載連結](https://www.python.org/downloads/)
- **MongoDB** - [下載連結](https://www.mongodb.com/try/download/community)
- **現代瀏覽器** (Chrome、Firefox、Safari、Edge)

### 推薦工具
- **MongoDB Compass** - 資料庫管理工具
- **Postman** - API 測試工具
- **VS Code** - 程式碼編輯器

## 🚀 快速開始

### 1. 下載專案
```bash
git clone https://github.com/RaymondTKU/lolesportswiki.git
cd lolesportswiki
```

### 2. 啟動 MongoDB
```bash
# Windows
mongod

# macOS/Linux
sudo systemctl start mongod
```

### 3. 設定後端環境
```bash
cd backend

# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 4. 設定環境變數
```bash
# 複製環境變數範例檔案
cp .env.example .env

# 編輯 .env 檔案，設定您的配置
```

### 5. 啟動後端服務
```bash
python app.py
```

### 6. 開啟前端
在瀏覽器中開啟 `index.html` 或使用 Live Server 擴充功能

## 🔧 詳細設定

### 環境變數設定 (.env)
```env
# Flask 設定
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# MongoDB 設定
MONGODB_URI=mongodb://localhost:27017/lolesportswiki_dev

# 上傳設定
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# 其他設定
DEBUG=True
```

### MongoDB 設定
1. 確保 MongoDB 服務正在運行
2. 預設連接：`mongodb://localhost:27017`
3. 資料庫名稱：`lolesportswiki_dev`

### 開發模式設定
```bash
# 設定 Flask 環境
export FLASK_ENV=development
export FLASK_DEBUG=1

# 啟動開發服務器
flask run --host=0.0.0.0 --port=5000
```

## 📡 API 端點

### 認證 API
- `POST /api/auth/register` - 使用者註冊
- `POST /api/auth/login` - 使用者登入
- `GET /api/auth/me` - 取得當前使用者資訊
- `PUT /api/auth/me` - 更新使用者資訊
- `POST /api/auth/logout` - 使用者登出

### 測試 API
```bash
# 健康檢查
curl http://localhost:5000/health

# 註冊測試
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 登入測試
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## 🛠️ 開發工具

### 推薦的 VS Code 擴充功能
- Python
- MongoDB for VS Code
- REST Client
- Live Server
- Prettier
- ESLint

### 資料庫管理
```bash
# 連接 MongoDB
mongo

# 查看資料庫
show dbs

# 使用資料庫
use lolesportswiki_dev

# 查看集合
show collections

# 查看使用者
db.users.find()
```

## 🐛 常見問題

### Q1: MongoDB 連接失敗
**解決方案：**
1. 確保 MongoDB 服務正在運行
2. 檢查防火牆設定
3. 確認連接字串正確

### Q2: Python 依賴安裝失敗
**解決方案：**
1. 更新 pip：`pip install --upgrade pip`
2. 使用虛擬環境：`python -m venv venv`
3. 檢查 Python 版本：`python --version`

### Q3: CORS 錯誤
**解決方案：**
1. 檢查後端 CORS 設定
2. 確保前端請求 URL 正確
3. 使用 Live Server 而非直接開啟 HTML

### Q4: JWT Token 問題
**解決方案：**
1. 檢查 JWT_SECRET_KEY 設定
2. 確認 token 格式正確
3. 檢查 token 是否過期

## 📁 專案結構
```
lolesportswiki/
├── index.html              # 首頁
├── pages/                  # 其他頁面
│   ├── login.html         # 登入頁面
│   └── register.html      # 註冊頁面
├── css/                    # 樣式檔案
├── js/                     # JavaScript 檔案
├── images/                 # 圖片資源
├── backend/                # 後端程式碼
│   ├── app.py             # Flask 應用
│   ├── config.py          # 配置檔案
│   ├── models/            # 資料模型
│   ├── routes/            # API 路由
│   └── requirements.txt   # Python 依賴
├── start_backend.bat      # Windows 啟動腳本
└── README.md              # 專案說明
```

## 🔐 安全注意事項

1. **永不** 在生產環境中使用預設的 SECRET_KEY
2. 使用強密碼和安全的 JWT 密鑰
3. 定期更新依賴包
4. 在生產環境中關閉 DEBUG 模式
5. 使用 HTTPS 連接

## 🚀 部署指南

### 本地開發
1. 使用 `start_backend.bat` 啟動後端
2. 使用 Live Server 開啟前端

### 生產部署
1. 設定環境變數
2. 使用 Gunicorn 或 uWSGI
3. 配置 Nginx 反向代理
4. 設定 SSL 憑證

## 📞 支援與回饋

如果您遇到問題或有建議，請：
1. 查看此安裝指南
2. 檢查 GitHub Issues
3. 聯繫開發團隊

---

**開發者：** Raymond  
**專案連結：** https://github.com/RaymondTKU/lolesportswiki  
**最後更新：** 2024年7月16日
