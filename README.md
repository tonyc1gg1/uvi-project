模擬 IoT 感測資料收集 → 後端儲存 → Web 可視化 的完整開發流程。

🔍 專案簡介
本專案以 Python 撰寫爬蟲定時抓取政府公開 UVI（紫外線指數）資料，透過 Flask 後端框架進行 API 設計與資料處理，儲存至 MySQL 資料庫，並使用 ECharts 將台灣各地即時與歷史資料視覺化呈現。

🔧 技術棧
Python（資料擷取與邏輯處理）

Flask（後端伺服器）

MySQL（資料儲存）

Pandas（資料清洗與分析）

ECharts（地圖與折線圖視覺化）

Git / GitHub（版本控制）

Render（部署平台）

📦 系統功能
✅ 定時擷取 UVI 資料並存入資料庫

✅ API 支援縣市查詢與歷史平均值分析

✅ 地圖熱區與折線圖展示即時資料

✅ 支援城市篩選與平均值統計

✅ 已部署至 Render（提供線上展示）

📁 專案結構
csharp
複製
編輯
uvi-project/
│
├── app.py               # 主伺服器邏輯
├── templates/           # 前端 HTML 模板
├── static/              # 靜態資源 (ECharts, CSS)
├── crawler.py           # UVI 爬蟲模組
├── db.py                # MySQL 連線模組
└── requirements.txt     # 環境依賴
📚 待辦與延伸計畫
 -MQTT 模擬器接入，模擬感測器資料推送

 -Docker 容器化部署整個系統

 -接入 Grafana 進行儀表板展示

 -實作 OPC UA 資料流學習

 -與 ERP / MES API 進行串接測試
