# FloodLab — Predict the Flood HW2 互動式網站 PDD

**版本：v1.1｜日期：2026-10-21｜狀態：Code Agent 實作規格｜語言：繁體中文**

## 0. Code Agent 最高優先級指令

依本文件在**指定的既有本機專案資料夾**內開發可重現的 Predict the Flood 多元線性回歸分析管線及互動式網站，參考使用者提供的 `DIC-2-50-startup-main.zip` 課堂專案風格。先檢查本機現況與 Git remote，不可假設資料夾為空，不可刪除或覆蓋使用者現有成果。先完成資料與 Python 模型，再匯出真實結果，再建置靜態互動網站，最後整理報告素材及 GitHub Pages 部署。不得編造模型分數、Kaggle 排名、研究引用、NotebookLM 研究內容或 GPT 對話。

## 1. 開發環境、Git 與部署（v1.1 新增）

| 項目 | 設定 |
|---|---|
| GitHub 帳號 | `AidenXiao0924` |
| **已建立 Repository** | `https://github.com/AidenXiao0924/HW2-Predict-the-Flood` |
| **指定本機專案根目錄** | `C:\Users\AidenXiao\source\HW2-Predict-the-Flood` |
| 預期 remote 名稱 | `origin`，實際需先檢查 |
| 預期預設分支 | `main`，實際需先檢查 |
| 預計 Pages 網址 | `https://aidenxiao0924.github.io/HW2-Predict-the-Flood/`（尚須部署驗證） |
| 部署方式 | GitHub Actions → GitHub Pages，僅發布靜態 `web/` |
| Python | 建議 3.11+；在專案內建立 `.venv` |
| 網站 | HTML/CSS/Vanilla JS + Chart.js，無需伺服器端推論 |

### 1.1 Code Agent 進入專案的必要檢查

1. 在 Windows 執行 `cd "C:\Users\AidenXiao\source\HW2-Predict-the-Flood"`，確認目錄存在；不存在時先詢問使用者，不得自行改在其他目錄開發。
2. 執行 `git status --short --branch`、`git remote -v`、`git branch -a`、`git log -1 --oneline`，檢查既有變更及 remote 是否對應上述 URL。若 remote 不一致，停止並回報。
3. 列出既有專案檔案，辨識 README、workflows、原始碼、使用者自訂設定。任何未提交的變更不得覆蓋或清除。
4. 將 `DIC-2-50-startup-main.zip` 視為**參考程式**，不得在原始 DIC-2 專案目錄直接修改，也不得複製 50-startup 的數值、係數、資料或評估結果。
5. 以 `.gitignore` 排除 `.venv/`、`__pycache__/`、`.pytest_cache/`、必要時 `data/raw/`、機密檔與本機暫存；是否追蹤 Kaggle 原始資料須符合來源條款及使用者決定。
6. 開發可使用獨立功能分支；推送或合併前先展示測試結果與預計變更。**不得執行 `git push --force`、`git reset --hard`、刪除分支、刪除既有檔案或覆蓋遠端歷史**，除非取得使用者明確同意。
7. 部署前確認 Pages 的 Actions 設定、工作流程及發佈來源；網站路徑使用相對路徑，支援 Repository 子路徑。部署成功後檢查 HTTP 200、資產載入及互動功能。
8. 不能存取使用者本機、GitHub 驗證或缺乏權限時，明確列出需要使用者在 VS Code/終端機執行的步驟，不可宣稱已完成部署。

### 1.2 PowerShell 建議命令

```powershell
cd "C:\Users\AidenXiao\source\HW2-Predict-the-Flood"
git status --short --branch
git remote -v
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py --data data/raw/train.csv
cd web
python -m http.server 8000
```

若 PowerShell 禁止啟用虛擬環境，可改用 `.\.venv\Scripts\python.exe` 執行，不必修改全域安全性設定。

## 2. 正式作業需求與資料集

正式依據：使用者提供的 `HW2_ Multiple Linear regression _ iLearning 3.0.pdf` 與 `HW_2_Multiple_Linear_Regression.pdf`。作業要求：Kaggle 10–20 個特徵的資料集（補充材料提出 14–39 的候選範圍）、Linear Regression、Feature Selection、Model Evaluation、包含信賴區間或預測區間的預測圖、CRISP-DM 六階段、GPT 對話 PDF、NotebookLM 網路同主題解法研究摘要至少 100 字、主流或更優解法比較、PDF 報告、學號命名 Python 主程式與 ZIP。GitHub/Colab 連結及 README 是有使用時需提供的補充資訊。互動網站是本專案自訂進階交付，不是作業說明明列的強制網站要求。

- 題目：**Predict the Flood**，Kaggle Playground Series S4E5：`https://www.kaggle.com/competitions/playground-series-s4e5`。
- 官方競賽資料：`train.csv`、`test.csv`、`sample_submission.csv`，實際使用前須核對下載版本與欄位。
- 預測目標：連續型 `FloodProbability`；`id` 是識別碼，禁止當作輸入特徵。
- 預期 20 個特徵：`MonsoonIntensity`, `TopographyDrainage`, `RiverManagement`, `Deforestation`, `Urbanization`, `ClimateChange`, `DamsQuality`, `Siltation`, `AgriculturalPractices`, `Encroachments`, `IneffectiveDisasterPreparedness`, `DrainageSystems`, `CoastalVulnerability`, `Landslides`, `Watersheds`, `DeterioratingInfrastructure`, `PopulationScore`, `WetlandLoss`, `InadequatePlanning`, `PoliticalFactors`。
- 資料來源與授權在 README 與報告中記錄；Kaggle 資料由使用者下載至 `data/raw/`。無資料時顯示明確提示，**不得產生假數據冒充實驗結果**。
- 此競賽目標不能直接視為真實世界的洪水發生機率或實際災害預警；相關性不等於因果。

## 3. 產品目標與驗收標準

1. Python 程式能從真實 Kaggle train.csv 完成 EDA、資料準備、模型訓練、特徵選擇、評估、診斷、預測區間與輸出。
2. 結果可重現，所有前處理及特徵選擇只 fit 訓練資料，最終保留測試集不參與選模。
3. GitHub Pages 靜態網站可正常操作；模型切換、圖表與 What-If 預測均使用 Python 真實匯出結果。
4. 提供 95% 信賴區間或預測區間的圖，明確區分兩者，並呈現 MAE/MSE/RMSE/R² 等指標。
5. 產出可用於 PDF 報告的圖片、表格、研究佔位、CRISP-DM 內容及繳交清單。

## 4. CRISP-DM 六階段

### 4.1 Business Understanding

定義以 20 個數值特徵預測 `FloodProbability` 的迴歸問題，解釋目標、使用者、成功指標、競賽資料限制與非因果性；不得稱作真實防災預警產品。

### 4.2 Data Understanding

分析樣本數、欄位型別、缺失值、重複資料、描述統計、目標分布、各特徵分布、與目標的相關性、特徵相關矩陣及異常值；檢查 `id` 是否唯一，輸出資料來源及欄位 schema。網站提供目標分布、相關熱圖、特徵排序與資料品質摘要。

### 4.3 Data Preparation

固定 `random_state=42`；從有標籤的 train.csv 分出訓練 64%、驗證 16%、最終測試 20%（先 80/20 再從訓練 80% 分出驗證 20%）；也可採訓練集內 CV，但必須全案一致並記錄。`id` 與目標欄排除於特徵。使用 sklearn Pipeline 在訓練 fold 內完成中位數補值與必要標準化，禁止資料洩漏。競賽 `test.csv` 沒有真實目標，不可用來計算 R²。

### 4.4 Modeling

- 基準：`DummyRegressor(strategy='mean')`。
- 必要：全 20 特徵 `LinearRegression`（OLS）。
- 特徵選擇：`SelectKBest(f_regression)` 搭配 OLS，k=1..20；`RFE` 搭配 OLS，至少 k={5,10,15,20}。
- 比較模型：Ridge、Lasso，對 alpha 做訓練集 5-fold KFold CV；正則化前標準化。
- 選模主要依訓練集 CV RMSE，接近時考量特徵數與穩定性；驗證集確認後凍結模型，保留測試集只做一次最終評估。
- 可選：Forward SFS，但不以 2^20 全組合窮舉為預設。
- 保存每個實際訓練模型的 Pipeline、特徵順序、係數、截距、CV、驗證與測試結果；未訓練的模型或 k 不得在前端假裝可選。

### 4.5 Evaluation

指標：MAE、MSE、RMSE、R²、Adjusted R²（`1-(1-R²)*(n-1)/(n-p-1)`；n<=p+1 時 N/A）。視覺化：Actual vs Predicted（含 y=x）、殘差 vs 預測、殘差分布、Q-Q 圖、特徵數與 CV RMSE/R²、模型比較、係數圖。

檢驗五大回歸假設：線性關係、誤差獨立性（Durbin–Watson；非時間資料解釋限制）、同方差性（Breusch–Pagan）、殘差常態性（Q-Q / Jarque–Bera）、多重共線性（VIF）。

**95% 區間：** 對 OLS 使用 statsmodels `get_prediction(...).summary_frame(alpha=0.05)`，區分平均值信賴區間（CI）與單筆觀測預測區間（PI）；網站圖表清楚標示。對 Ridge/Lasso 不得冒用 OLS 解析區間；若需要可用獨立校準資料的 split conformal prediction，標示其假設、校準筆數與適用模型；未實作時顯示「無可用區間」。評估測試集 PI coverage 與平均寬度，但測試集不可用來校準。

Kaggle 排名與分數只在真實提交後展示，否則顯示「未提交」。

### 4.6 Deployment

Python 離線產生 JSON/圖表；前端用匯出的線性係數與正確的 scaler 參數推論，保證與 Python 同樣本預測差異 < 1e-8。對任意新樣本的 OLS PI 如需前端即時計算，必須匯出足夠的設計矩陣共變異數、殘差變異及自由度，使用 Student-t 分位數並測試與 statsmodels 一致。部署 `web/` 至 GitHub Pages，網站相對路徑可在 `/HW2-Predict-the-Flood/` 下運作。

## 5. 互動網站資訊架構

**視覺方向**：參考 DIC-2 50-startup 專案的 Bento Grid、深淺色主題、漸層 KPI 卡、Chart.js、響應式佈局；主文案繁體中文，專有名詞保留英文。名稱 **FloodLab — Predict the Flood**。

### A. Overview
Hero、Kaggle 來源、20 Features、模型介紹、CRISP-DM 導覽、目前模型 KPI（測試 RMSE、R²、MAE、95% PI coverage 若有）、資料限制聲明。

### B. Data Explorer
目標分布、20 特徵相關熱圖、特徵與目標相關排序、缺失值與描述統計；選取特徵顯示其分布與說明。

### C. Feature Selection Lab
SelectKBest/RFE/Lasso 切換；k 控制僅允許實際已訓練值；CV RMSE/R² 對 k 圖、入選特徵 chips、比較表、選模依據說明。

### D. Model Diagnostics
模型切換時同步更新指標、係數、公式、Actual vs Predicted、PI、殘差、Q-Q、VIF、統計檢定；OLS p-value 不得套用到 Ridge/Lasso。

### E. What-If Flood Simulator
20 特徵的滑桿與數字輸入，四組可收合欄位，訓練資料觀測範圍/分位數、訓練中位數預設值、重設/載入樣本/示例；即時顯示原始預測、可用時的 95% PI、分布外警告。不得默默把超出 0–1 的線性預測裁切；貢獻圖使用 `coefficient × (input-reference)`，並能加總回預測值，註明非因果解釋。

### F. CRISP-DM & Report
六階段摘要、資料來源、實驗設定、模型限制、下載指標 CSV/圖表 PNG、可列印報告內容、NotebookLM/GPT 研究狀態、GitHub 與網站連結。下載控制必須可用，不得只做視覺假按鈕。

## 6. JSON 契約與前端一致性

`web/data/model_results.json`：`schema_version`, `dataset`, `seed`, `splits`, `models[]`, `selection_runs[]`, `recommended_model_id`, `generated_at`, `limitations`。

每個 model：`id`, `display_name`, `family`, `features`, `feature_order`, `intercept`, `coefficients`, `scaler`（若有）, `cv_metrics`, `validation_metrics`, `test_metrics`, `diagnostics`, `interval_method`, `interval_parameters`, `prediction_plot_points`。

`web/data/eda.json`：`feature_schema`, `summary_stats`, `missing_counts`, `correlation_matrix`, `target_distribution`, `feature_target_correlations`。

`web/data/prediction_samples.json`：固定 seed 選出的少量真實樣本及相應模型預測；不得包含全量百萬筆資料。資料讀取失敗顯示清楚訊息，不可回退到偽造模型成果。

## 7. 專案結構（以指定本機根目錄為準）

```text
C:\Users\AidenXiao\source\HW2-Predict-the-Flood\
├── README.md
├── .gitignore
├── requirements.txt
├── main.py
├── 7114056XXX_hw2.py        # 用實際學號取代佔位字串
├── src/
│   ├── data.py
│   ├── eda.py
│   ├── feature_selection.py
│   ├── modeling.py
│   ├── evaluation.py
│   ├── intervals.py
│   └── export.py
├── data/raw/                # 手動放置 Kaggle CSV
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── models/
│   └── run_metadata.json
├── web/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── assets/
│   └── data/
│       ├── model_results.json
│       ├── eda.json
│       └── prediction_samples.json
├── report/
│   ├── HW2_report_template.md
│   ├── NotebookLM_research_notes.md
│   ├── NotebookLM_summary_PLACEHOLDER.md
│   └── submission_checklist.md
├── tests/
│   ├── test_data_contract.py
│   ├── test_no_leakage.py
│   ├── test_metrics.py
│   ├── test_prediction_parity.py
│   └── test_intervals.py
└── .github/workflows/deploy.yml
```

建議依賴：pandas、numpy、scikit-learn、scipy、statsmodels、matplotlib、seaborn、joblib、pytest。可在前端以 CDN 或合法授權的本地 Chart.js 檔案提供圖表；若使用 CDN，需記錄版本與網路依賴。

## 8. NotebookLM 研究工作流（v1.1 新增）

作業要求使用 NotebookLM 研究**網路上同主題解法**，在報告中提供至少 100 字摘要，並比較主流或更優解法。Code Agent 需預留研究欄位，但不可代替使用者宣稱已使用 NotebookLM。

### 第一階段：模型訓練前的公開解法研究

1. 使用者建立 NotebookLM 筆記本 `Predict the Flood — Multiple Linear Regression Research`。
2. 匯入可核實的資料來源：Kaggle 競賽頁、Kaggle Code/Discussion 中實際有程式與指標的解法、scikit-learn 官方 Linear Models 與 Feature Selection 文件、可信的統計/CRISP-DM 文獻。記錄每個來源的 URL、作者、日期與主要發現。
3. 使用以下研究 Prompt：

> 我正在完成 Predict the Flood（Kaggle Playground Series S4E5）的 Multiple Linear Regression 作業。請**僅依已匯入來源**整理資料集與評估指標、參賽者實際採用的模型、特徵選擇方式、公開評估結果及各模型的優缺點；比較 Linear Regression、Ridge、Lasso 與來源中實際出現的其他模型。區分來源事實與推論，不得編造分數、排名或不存在的模型。請以繁體中文產生比較表並附來源引用，最後提出對本次 CRISP-DM 作業可採用的改進方向。

### 第二階段：模型完成後的自身結果比較

1. 將 Code Agent 實際輸出的模型比較表、CV 設定、測試指標、特徵選擇結果與分析報告匯入 NotebookLM。
2. 使用以下 Prompt：

> 請依據已匯入的 Predict the Flood 公開研究來源與我的 HW2 實驗結果，分析我的 OLS、SelectKBest、RFE、Ridge、Lasso 與其他公開解法的差異。請比較特徵選擇、準確度、可解釋性、運算成本與限制；不同切分或指標的結果不得直接視為可比。產生：(A) 可放入 PDF 報告的繁體中文 250–350 字研究摘要，(B) 含模型、方法、特徵選擇、評估結果、優點、限制、來源引用的比較表，(C) 我應優先改善的三項實驗。沒有來源支持的結論請標註無法確認。

3. 使用者核對 NotebookLM 引用與摘要，親自完成研究內容；Code Agent 將經確認的文字整合到 `report/` 與最終 PDF。
4. 未完成研究時，在網站與報告明確標示 `NotebookLM 研究摘要：待使用者補入`，不能填入虛構成果。

## 9. PDF 報告與作業繳交

報告結構：封面、摘要、Kaggle 來源、CRISP-DM 六階段、EDA、前處理、特徵選擇、模型比較、MAE/MSE/RMSE/R²/Adjusted R²、含 95% CI 或 PI 預測圖、回歸假設診斷、NotebookLM 研究摘要（至少 100 字，建議 250–350 字）、網路主流或更優解法比較、網站部署連結與截圖、限制、GPT 輔助內容、參考資料及附錄。

所有 ChatGPT 對話由使用者依作業要求匯出 PDF；Agent 提醒操作但不得偽造對話。主程式 `7114056XXX_hw2.py` 或 `.ipynb` 以及壓縮檔 `7114056XXX_hw2.zip` 均須以**實際學號**替換；不要使用佔位字串直接交作業。繳交 ZIP 至少包含 Python 主程式、PDF 報告、GPT 對話 PDF、NotebookLM 研究摘要及必要程式/執行說明。使用 GitHub 時 README 須提供 repo、Pages 連結、環境建置、CRISP-DM、模型結果、限制及重現方式。

## 10. 自動化測試與驗收

- 缺 Kaggle CSV 時有明確錯誤與下載說明，不得生成假成果。
- schema 檢查：20 個輸入特徵、目標、id；id 不進模型。
- 重跑同 seed：特徵選擇及模型指標一致。
- 無資料洩漏：Imputer/Scaler/Selector 在訓練 fold 內 fit。
- MAE/MSE/RMSE/R²/Adjusted R² 使用已知數值單元測試。
- 模型切換同步更新所有 KPI、圖、公式、區間及模擬器；未訓練模型不可選。
- Python vs JS 預測差異 < 1e-8；OLS PI 與 statsmodels 比對；測試 coverage 不能用測試集校準。
- 375px/768px/1440px 版型、鍵盤操作、圖表標籤、深淺主題正常。
- `cd web && python -m http.server 8000` 可運作，所有相對資源在 GitHub Pages 子路徑正常載入。
- 部署後首頁、JS/CSS/JSON、模型切換、What-If 預測與下載功能驗收通過；無 404/console error。
- README、報告與網站的模型數值一致；未提交 Kaggle 時不得顯示排名。

## 11. 開發順序與 Agent 最終回報

**Phase 0 — Git/環境檢查**：確認指定資料夾、repo remote、既有變更、資料集與權限。

**Phase 1 — 資料與模型**：下載指引、EDA、無洩漏訓練管線、OLS/SelectKBest/RFE/Ridge/Lasso、評估、診斷與 PI。

**Phase 2 — 資料契約**：JSON/圖片/表格匯出，Python/JS parity 測試。

**Phase 3 — 網站**：六大區塊、所有互動控制、響應式視覺、真實模型數據。

**Phase 4 — 報告與部署**：CRISP-DM 報告模板、NotebookLM 研究佔位、README、GitHub Actions、Pages 驗收、繳交清單。

最終必須回報：① 專案檔案樹與變更摘要；② 安裝、訓練、本地網站啟動指令；③ 實際模型結果（有資料才列）；④ 測試結果及未通過項目；⑤ 網站功能驗收；⑥ GitHub commit、remote、Pages URL（若實際部署）；⑦ 使用者尚需補入的學號、資料集、NotebookLM 摘要、GPT PDF、Kaggle 提交與 PDF 報告；⑧ 是否有修改任何既有檔案。**未完成不可標示已完成。**
