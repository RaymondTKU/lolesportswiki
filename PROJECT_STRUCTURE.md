# 英雄聯盟電競資訊網 - 專案結構說明

## 專案概述
這是一個專為英雄聯盟電競愛好者設計的資訊網站，提供最新的賽事資訊、隊伍介紹、選手資料等功能。

## 技術架構
- **前端**: HTML + CSS (純原生，不使用框架)
- **後端**: Python (Flask/Django)
- **資料庫**: MongoDB
- **身份驗證**: JWT Token
- **圖片處理**: PIL/Pillow

## 檔案結構
```
lolesportswiki/
├── index.html              # 首頁
├── css/
│   ├── style.css          # 主要樣式
│   ├── animations.css     # 動畫效果
│   └── responsive.css     # 響應式設計
├── js/
│   ├── main.js           # 主要JavaScript功能
│   ├── api.js            # API 請求處理
│   └── utils.js          # 工具函數
├── images/
│   ├── logo.png          # 網站Logo
│   ├── heroes/           # 英雄圖片
│   ├── teams/            # 隊伍Logo
│   └── players/          # 選手頭像
├── pages/
│   ├── login.html        # 登入頁面
│   ├── register.html     # 註冊頁面
│   ├── matches.html      # 賽事列表
│   ├── teams.html        # 隊伍介紹
│   ├── players.html      # 選手資料
│   └── admin/            # 管理後台
├── backend/
│   ├── app.py            # Flask應用主檔
│   ├── models/           # 資料模型
│   ├── routes/           # API路由
│   ├── utils/            # 工具函數
│   └── config.py         # 配置檔案
└── README.md             # 專案說明
```

## 首頁設計特色

### 1. 視覺設計
- **英雄聯盟官方色彩**: 使用藍金配色方案
- **漸層背景**: 深藍色漸層營造電競氛圍
- **金色點綴**: 使用金色作為重點色彩
- **現代化設計**: 卡片式布局，乾淨簡潔

### 2. 互動效果
- **滾動視差**: 背景圖片視差效果
- **懸浮動畫**: 滑鼠懸浮時的動畫效果
- **載入動畫**: 頁面載入時的動畫效果
- **平滑滾動**: 錨點跳轉平滑滾動

### 3. 響應式設計
- **移動端優化**: 320px-768px 手機版布局
- **平板端適配**: 768px-1024px 平板版布局
- **桌面端優化**: 1024px+ 桌面版布局

## 功能模組

### 1. 使用者系統
- 註冊/登入功能
- 個人資料管理
- 收藏功能
- JWT身份驗證

### 2. 賽事管理
- 賽事列表展示
- 賽事詳情頁面
- 賽事搜尋功能
- 賽事時間倒數

### 3. 隊伍與選手
- 隊伍介紹頁面
- 選手資料展示
- 統計數據顯示
- 關聯性查詢

### 4. 互動功能
- 留言系統
- 收藏功能
- 搜尋建議
- 即時通知

## 開發優先順序

### 第一階段：基礎架構
1. 完成首頁HTML結構
2. 實現基本CSS樣式
3. 建立Python後端架構
4. 設計MongoDB資料結構

### 第二階段：核心功能
1. 使用者註冊/登入系統
2. 賽事資料CRUD操作
3. 基本的API介面
4. 前端JavaScript互動

### 第三階段：進階功能
1. 搜尋功能實現
2. 收藏系統
3. 留言功能
4. 管理後台

### 第四階段：優化部署
1. 性能優化
2. 響應式設計完善
3. 測試與除錯
4. 部署到雲端平台

## 注意事項

1. **純CSS實現**: 所有動畫效果都使用CSS實現，不依賴JavaScript框架
2. **MongoDB設計**: 使用PyMongo進行資料庫操作
3. **響應式優先**: 採用Mobile-First設計理念
4. **性能考慮**: 圖片優化、CSS壓縮、快取策略
5. **使用者體驗**: 載入動畫、錯誤提示、表單驗證

## 相關資源

- [英雄聯盟官方色彩規範](https://brand.riotgames.com/en-us/league-of-legends/color)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Flask 官方文檔](https://flask.palletsprojects.com/)
- [CSS Grid 布局指南](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [響應式設計最佳實踐](https://web.dev/responsive-web-design-basics/)
