# 英雄聯盟電競資訊網 🏆

一個專為英雄聯盟電競愛好者設計的資訊網站，提供最新的賽事資訊、隊伍介紹、選手資料等功能。

## 🚀 技術架構

- **前端**: HTML + CSS (純原生，不使用框架)
- **後端**: Python (Flask/Django)
- **資料庫**: MongoDB
- **身份驗證**: JWT Token
- **圖片處理**: PIL/Pillow

## 🎨 設計特色

### 視覺設計
- 英雄聯盟官方藍金配色方案
- 現代化卡片式布局
- 漸層背景與動畫效果
- 響應式設計（支援各種螢幕尺寸）

### 互動效果
- 滾動視差效果
- 懸浮動畫
- 載入動畫
- 平滑滾動

## 📂 檔案結構

```
lolesportswiki/
├── index.html              # 首頁
├── css/
│   ├── style.css          # 主要樣式
│   └── animations.css     # 動畫效果
├── js/
│   └── main.js           # 主要JavaScript功能
├── images/               # 圖片資源
├── pages/                # 其他頁面
├── backend/              # Python後端
└── README.md            # 專案說明
```

## 🔧 開發環境設定

1. **前端開發**
   ```bash
   # 直接在瀏覽器中開啟 index.html
   # 或使用 Live Server 擴充功能
   ```

2. **後端開發**
   ```bash
   # 安裝 Python 依賴
   pip install flask pymongo bcrypt pyjwt pillow
   
   # 啟動 Flask 應用
   python backend/app.py
   ```

3. **資料庫設定**
   ```bash
   # 安裝 MongoDB
   # 啟動 MongoDB 服務
   mongod
   ```

## 🌟 主要功能

### 使用者系統
- [x] 註冊/登入功能
- [x] 個人資料管理
- [x] 收藏功能
- [x] JWT身份驗證

### 賽事管理
- [x] 賽事列表展示
- [x] 賽事詳情頁面
- [x] 賽事搜尋功能
- [x] 賽事時間倒數

### 隊伍與選手
- [x] 隊伍介紹頁面
- [x] 選手資料展示
- [x] 統計數據顯示
- [x] 關聯性查詢

### 互動功能
- [x] 留言系統
- [x] 收藏功能
- [x] 搜尋建議
- [x] 即時通知

## 📱 響應式設計

- **移動端** (320px-768px): 手機版布局
- **平板端** (768px-1024px): 平板版布局
- **桌面端** (1024px+): 桌面版布局

## 🎯 開發進度

請參考 [TODO.md](TODO.md) 查看詳細的開發任務清單。

## 🤝 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 建立 Pull Request

## 📝 授權條款

此專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡方式

- 專案作者: [RaymondTKU](https://github.com/RaymondTKU)
- 專案連結: [https://github.com/RaymondTKU/lolesportswiki](https://github.com/RaymondTKU/lolesportswiki)

## 🙏 致謝

感謝 Riot Games 提供的英雄聯盟遊戲內容與設計靈感。