---
title: TODO

---

## 英雄聯盟比賽資訊網：細項任務 Todo 清單（依模組細分）

### 使用者功能模組
- [ ] A1：設計 User Schema  
  - [ ] 設計欄位（帳號、密碼、Email、權限、收藏清單等）  
  - [ ] 使用 Mongoose 實作 Schema  
  - [ ] 加入密碼加密（bcrypt）  
- [ ] A2：註冊 API + 驗證處理  
  - [ ] POST /api/users/register  
  - [ ] 欄位驗證（空值、Email格式）  
  - [ ] 密碼加密與存儲  
- [ ] A3：登入 API + JWT 實作  
  - [ ] POST /api/users/login  
  - [ ] JWT token 產生與回傳  
  - [ ] 錯誤處理（帳號錯誤、密碼錯誤）  
- [ ] A4：取得 / 更新使用者資訊 API  
  - [ ] GET /api/users/me  
  - [ ] PUT /api/users/me  
  - [ ] 權限驗證（需帶 token）  
- [ ] A5：收藏功能 API  
  - [ ] 設計 Favorite Schema（關聯隊伍、選手、比賽）  
  - [ ] POST /api/favorites  
  - [ ] GET /api/favorites  
  - [ ] DELETE /api/favorites/:targetId  
- [ ] A6：使用者前台頁面與表單設計  
  - [ ] 註冊頁面  
  - [ ] 登入頁面  
  - [ ] 我的收藏頁面  
  - [ ] 表單驗證與錯誤訊息處理  

### 賽事與選手模組
- [ ] B1：設計 Team / Player / Match Schema  
  - [ ] Team Schema：名稱、Logo、成員、戰績  
  - [ ] Player Schema：暱稱、真名、位置、所屬隊伍  
  - [ ] Match Schema：時間、隊伍A/B、賽果、賽季  
- [ ] B2：建立隊伍與選手 API  
  - [ ] POST /api/teams, GET /api/teams, GET /api/teams/:id  
  - [ ] POST /api/players, GET /api/players, GET /api/players/:id  
- [ ] B3：建立賽事 API  
  - [ ] POST /api/matches  
  - [ ] PUT /api/matches/:id  
  - [ ] DELETE /api/matches/:id  
- [ ] B4：賽事列表與詳情 API  
  - [ ] GET /api/matches  
  - [ ] GET /api/matches/:id  
- [ ] B5：隊伍與選手詳情 API  
  - [ ] 加入隊伍關聯選手查詢功能  
  - [ ] 加入選手過往賽事紀錄顯示  
- [ ] B6：前端頁面：賽事 / 隊伍 / 選手  
  - [ ] 賽事列表頁  
  - [ ] 賽事詳情頁（包含留言）  
  - [ ] 隊伍介紹頁  
  - [ ] 選手個人資料頁  
- [ ] B7：賽事 CRUD 管理功能（後台）  
  - [ ] 管理頁登入驗證  
  - [ ] 建立、編輯、刪除賽事  
  - [ ] 顯示賽事總覽表格與搜尋功能  

### 管理與留言模組
- [ ] C1：設計 Comment / Favorite Schema  
  - [ ] Comment：留言內容、留言者、比賽關聯、時間  
  - [ ] Favorite：type, targetId, userId  
- [ ] C2：建立留言與收藏 API  
  - [ ] POST /api/comments  
  - [ ] GET /api/comments/match/:matchId  
  - [ ] DELETE /api/comments/:id（需權限）  
- [ ] C3：設計 Announcement / AdminLog  
  - [ ] Announcement：內容、發布者、發布時間  
  - [ ] AdminLog：動作類型、管理員帳號、時間戳記  
- [ ] C4：建立公告與後台紀錄 API  
  - [ ] POST /api/announcements  
  - [ ] GET /api/announcements  
  - [ ] GET /api/admin/logs  
- [ ] C5：前端留言與收藏機制  
  - [ ] 比賽頁可留言與查看留言  
  - [ ] 收藏按鈕（選手/隊伍/比賽）  
  - [ ] 收藏總覽頁  
- [ ] C6：建立管理員後台頁面  
  - [ ] 後台登入 / 權限驗證  
  - [ ] 公告編輯介面  
  - [ ] 管理紀錄瀏覽頁  
- [ ] C7：設計圖片上傳功能  
  - [ ] POST /api/upload  
  - [ ] 上傳選手與隊伍 Logo 圖片  
  - [ ] 檔名處理與儲存路徑規劃  
