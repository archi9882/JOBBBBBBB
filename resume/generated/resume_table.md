# 履歷生產表（自動產生，勿手改）

已解鎖 0／16 條。重新產生：`python tools/resume_gen.py --refresh`

| 敘述 | 能力 | 狀態 | 還缺什麼 | 面試會被問 |
|---|---|---|---|---|
| L1-tsunami-sensitivity | M1 數值模擬與物理判斷 | 鎖定 | 實驗室卡 09 未完成；實驗室卡 12 未完成；實驗室卡 13 未完成；實驗室卡 14 未完成 | 網格要多細才夠？你怎麼知道？什麼情況你不信這個模式的結果？ |
| A1-solver | M1 數值模擬與物理判斷 | 鎖定 | grill A/conservation-form 分數 0 < 2；grill A/hll-flux 分數 0 < 2；grill A/analytic-and-convergence 分數 0 < 2；grill A/wet-dry 分數 0 < 2 | 為什麼收斂階不是 1？前緣落後怎麼修？什麼情況你不會用這個求解器？ |
| A2-async-api | REST API | 鎖定 | grill A/job-queue 分數 0 < 2；grill A/api-contract 分數 0 < 2 | worker 被 kill -9 時會怎樣？為什麼不在 POST 裡直接算？SQLite 佇列什麼時候該換掉？ |
| A3-compose | M2 自架基礎設施 | 鎖定 | grill A/deployment 分數 0 < 2 | worker 擴到 10 個時哪裡先壞？你會換成什麼，代價是什麼？ |
| B1-etl | ETL 與數值計算 | 鎖定 | grill B/etl-time-units 分數 0 < 2；grill B/dedup-merge-idempotent 分數 0 < 2 | 兩個來源同一小時數值不同怎麼辦？怎麼發現來源其實是開始標記？ |
| B2-spatial | 空間資訊 | 鎖定 | grill B/thiessen-and-projection 分數 0 < 2；grill B/areal-rainfall-missing 分數 0 < 2 | 權重和＝1 抓不到哪些錯？重新正規化在什麼雨型下會偏差很大？ |
| B3-k8s-metrics | M2 自架基礎設施 | 鎖定 | grill B/k8s-and-metrics 分數 0 < 2；grill B/api 分數 0 < 2；課程 07/02 未出貨 | replicas 改成 3 時哪裡會出錯？你會對哪個指標設告警？ |
| C1-ade | M1 數值模擬與物理判斷 | 鎖定 | 專案 C L1-ade-solver 未通過 | 數值擴散和物理延散怎麼分辨？ |
| C2-inverse | M1 數值模擬與物理判斷 | 鎖定 | 專案 C L2-inverse-dispersion 未通過 | 什麼時候反求出的 D 不可信？ |
| C3-to-C5-service | M2 自架基礎設施 | 鎖定 | 專案 C L3-well-etl-spatial 未通過；專案 C L4-service 未通過；專案 C L5-platform 未通過 | 哪一層最脆弱？刪掉一個 Pod 時發生了什麼？ |
| C6-decisions | M2 自架基礎設施 | 鎖定 | 專案 C L6-decisions 未通過 | 哪個決策你最可能推翻？ |
| L2-own-verification-tools | M1 數值模擬與物理判斷 | 鎖定 | 實驗室卡 06 未完成；實驗室卡 07 未完成；實驗室卡 14 未完成 | 你的走時和 COMCOT 差在哪？什麼情況 Richardson 外插不能用？ |
| L3-geodata-etl | 空間資訊與 ETL | 鎖定 | 實驗室卡 08 未完成；實驗室卡 10 未完成；實驗室卡 15 未完成 | 兩筆同站同時刻的數值不同，你為什麼不留其中一筆？ |
| L4-service-and-batch | M2 自架基礎設施與 REST API | 鎖定 | 實驗室卡 17 未完成；實驗室卡 18 未完成；實驗室卡 19 未完成；實驗室卡 20 未完成 | 服務重啟時進行中的工作怎麼辦？冪等紀錄放在記憶體裡有什麼問題？ |
| M3-falsification | M3 生成式 AI 協作與否證 | 鎖定 | 實驗室卡 16 未完成；實驗室卡 21 未完成；自己的否證紀錄 0 筆 < 6 | 舉一個 AI 看起來對但其實錯的例子，你怎麼發現的？ |
| M1-verification-suite | M1 數值模擬與物理判斷 | 鎖定 | 課程 01/03 未出貨；課程 01/04 未出貨 | 只有一個網格時你怎麼判斷結果可信？ |

## 敘述預覽（含未解鎖；數字取自目前的 metrics.json）

- **L1-tsunami-sensitivity**（鎖定）：以 COMCOT 淺水方程模式建立台灣海嘯情境實驗：真實地形（ETOPO）、文獻依據的馬尼拉海溝斷層情境，分析地震規模、線性／非線性方程與網格解析度對沿岸最大水位的敏感度。
- **A1-solver**（鎖定）：建置一維淺水方程有限體積（HLL 通量）潰壩模擬器，以 Stoker 解析解驗證：N=400 時 L1 誤差 33.16 m²、觀測收斂階 0.927，總水量守恆至機器精度；並量化乾床前緣落後解析解的程度及其對淹水範圍預報的影響。
- **A2-async-api**（鎖定）：設計非同步模擬服務（FastAPI＋SQLite 工作佇列＋worker）：202／Location 工作模式、RFC 9457 錯誤格式、冪等鍵、輸入上限與 worker 逾時重排，17 個自動化測試涵蓋邊界情境。
- **A3-compose**（鎖定）：以 Docker Compose 部署 API 與 worker（非 root 容器、健康檢查、共用資料卷），並分析單機 SQLite 佇列在 10 倍負載下的瓶頸與替代方案。
- **B1-etl**（鎖定）：建立多來源雨量 ETL（2 種來源、6 站）：統一時區與時雨量區間標記、缺值哨兵與物理範圍檢查、去重與合併規則，拒收紀錄可追溯，輸出可逐位元重現。
- **B2-spatial**（鎖定）：以 TWD97 投影與徐昇式多邊形（Voronoi 裁切至流域邊界）計算面積雨量，處理外圍無界區域與缺測站權重重新正規化；投影來回誤差 1.4e-06 mm。
- **B3-k8s-metrics**（鎖定）：撰寫 Kubernetes 部署設定（資源限制、就緒與存活探針、非 root、固定映像版本）並以 Prometheus 指標監控服務，在 k3d 叢集上部署驗證。
- **C1-ade**（鎖定）：從零實作一維對流-延散有限差分求解器，以 Ogata–Banks 解析解驗證收斂階與守恆，並分析網格 Péclet 數造成的數值擴散。
- **C2-inverse**（鎖定）：從監測井濃度資料反求延散係數，分析觀測窗長與雜訊對參數可辨識性的影響。
- **C3-to-C5-service**（鎖定）：從資料 ETL、模擬 API 到 k3d 自架平台與監控，從零完成一套地下水污染傳輸模擬服務，並進行故障演練。
- **C6-decisions**（鎖定）：撰寫架構決策紀錄（物件儲存選型、self-host 或外包、是否採用 FaaS）與 10 倍容量估算，每項決策列出可推翻條件。
- **L2-own-verification-tools**（鎖定）：自行以 Python 撰寫海嘯模擬的驗證工具並由自動化驗收測試把關：長波走時（梯形積分，對線性變淺解析解驗證）、水位快照最大值與海岸格後處理、觀測收斂階與 Richardson 外插（非單調時拒絕估計），並與 COMCOT 輸出交叉檢查。
- **L3-geodata-etl**（鎖定）：撰寫空間與時間序列資料前處理並以測試驗收：ETOPO 水深裁切與 COMCOT 格式轉換（NaN 與空範圍拒收、網格順序固定）、TWD97（EPSG:3826）座標轉換與距離（中央經線與軸順序檢查）、潮位站資料清理（時區統一為 UTC、哨兵值與超出範圍、衝突紀錄全數拒收並留下原因）。
- **L4-service-and-batch**（鎖定）：將海嘯模擬包成非同步服務並容器化：FastAPI（202／Location 輪詢、RFC 9457 錯誤格式、Idempotency-Key 冪等、失敗工作狀態），非 root 且固定版本的 Docker 映像與健康檢查，有並行上限、單點失敗不拖垮整批的批次排程與結果彙整表。
- **M3-falsification**（鎖定）：建立 AI 產出否證流程（可檢驗預測 → 獨立驗證 → 紀錄），累積 0 筆實例，涵蓋數值格式、套件 API 預設值、部署設定與文獻引用錯誤。
- **M1-verification-suite**（鎖定）：建立數值驗證測試套件：守恆、觀測收斂階、製造解（MMS）、靜水平衡，並以持續整合自動執行。
