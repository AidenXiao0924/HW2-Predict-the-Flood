# Codex Development Log

> 專案：HW2 — Predict the Flood  
> 課程：物聯網應用與資料分析  
> 本文件只記錄實際執行結果；Codex 原始對話由使用者另行匯出。

## Phase 0 — 環境建置與最終驗收

- 執行日期：2026-10-21（Asia/Taipei）
- 狀態：**條件式未通過**
- 未開始模型訓練、正式網站修改、Git commit 或 Git push。

### 本階段目標

1. 重新檢查指定本機專案與 Git 狀態。
2. 完整閱讀 `PDD.md` v1.1 與 `references/DIC-2-50-startup-main.zip`。
3. 驗證 Kaggle CSV schema、欄位與資料筆數。
4. 建立 Python 3.11 `.venv`、依 PDD 建立 `requirements.txt` 並安裝套件。
5. 建立安全的 `.gitignore`，執行套件 import smoke test。
6. 判定是否符合進入 Phase 1 的條件。

### 使用者需求與本次技術決策

- 所有正式變更只放在 `C:\Users\AidenXiao\source\HW2-Predict-the-Flood`。
- Kaggle 原始 CSV 在公開條款及提交策略確認前一律忽略，不加入 Git。
- 參考專案只在系統暫存目錄解壓檢視，不修改 ZIP 或原始參考內容。
- 因 Windows `py` launcher 無法偵測 Python，本專案使用可正常執行的 `python -m venv .venv`，建立結果仍為 Python 3.11.9。
- 依 PDD 所列直接依賴建立具相容上限的 `requirements.txt`；因套件來源無法連線，尚不能以實際安裝版本鎖定 exact versions。
- 網路阻塞時不借用或硬拷貝其他專案的 virtual environment，以避免不可重現及路徑污染。

### PDD v1.1 審查

- 已完整閱讀根目錄 `PDD.md`，檔案大小 18,623 bytes，版本標示為 v1.1、日期 2026-10-21。
- 規格明確要求：CRISP-DM 六階段、固定 `random_state=42`、64/16/20 labeled-data split、無資料洩漏 Pipeline、Dummy baseline、全 20 特徵 OLS、SelectKBest、RFE、Ridge、Lasso、完整指標、五大假設診斷、OLS CI/PI、前後端 parity、靜態 GitHub Pages 與 NotebookLM placeholder。
- 本階段未發現無法實作的架構衝突；需在後續特別遵守的風險如下：
  1. Kaggle `test.csv` 無目標，只能用於 inference/submission，不能計算 R²。
  2. OLS 解析 CI/PI 不得套用到 Ridge/Lasso。
  3. 特徵選擇、imputation、scaling 與 alpha tuning 必須只 fit training fold。
  4. 前端若即時計算 OLS PI，需匯出設計矩陣共變異數、殘差變異及自由度，不可只用係數臆造區間。
  5. 網站不得將線性預測默默裁切至 0–1。
  6. PDD 範例命令使用 `py -3`，但本機 launcher 不可用；本專案需改用 `.\.venv\Scripts\python.exe` 或 `python`。
  7. 實際學號尚未提供，後續不可直接提交 `7114056XXX_hw2.py` 佔位名稱。

### Git 檢查

| 項目 | 實際結果 |
| --- | --- |
| Repository | 已存在 `.git` |
| Branch | `main` |
| Commit | 尚無任何 commit |
| Upstream | 顯示 `origin/main [gone]`；遠端目前沒有可用的追蹤 ref |
| Remote | `origin` fetch/push 均為 `https://github.com/AidenXiao0924/HW2-Predict-the-Flood.git` |
| 初始 status | `PDD.md`、`data/`、`references/` 未追蹤 |
| 驗收時 status | `.gitignore`、`PDD.md`、`docs/`、`references/`、`requirements.txt` 未追蹤；raw CSV 與 `.venv` 已被忽略 |
| 遠端連線驗證 | `git ls-remote --heads origin` 失敗：執行環境無法解析 `github.com` |
| Commit / push | 未執行 |

### Kaggle 資料驗證

使用 Python 3.11 標準函式庫逐列讀取完整 CSV，沒有用抽樣筆數代替總筆數。三個檔案均可解析、所有欄位均為數值、無空值、`id` 唯一。

| 檔案 | 資料列 | 欄位數 | 目標欄 | 缺值 | SHA-256 |
| --- | ---: | ---: | --- | ---: | --- |
| `train.csv` | 1,117,957 | 22 | 有 | 0 | `6c9adeacec0537306a80b957a69e57bf6d389e3c02c1ff33ca0a7dcb5a9b30fb` |
| `test.csv` | 745,305 | 21 | 無 | 0 | `9b3795c7d6ea60d1d55746395ab6aaff7b61fd0451917a14cc9d54585a6877d1` |
| `sample_submission.csv` | 745,305 | 2 | 有，範例值均為 0.5 | 0 | `3c99b1941471ebaef63b1acfea00b80900d4a752743ed43df597c6e2d6ffb03e` |

#### Schema 結論

- `train.csv`：`id` + PDD 指定的 20 個特徵 + `FloodProbability`，完全相符。
- `test.csv`：`id` + 相同 20 個特徵，完全相符且沒有 `FloodProbability`。
- `sample_submission.csv`：`id`, `FloodProbability`。
- train `id` 範圍為 0–1,117,956；test/submission 為 1,117,957–1,863,261，且 test 與 submission 列數一致。
- training target 實際範圍為 0.285–0.725。
- 20 個特徵均為非負整數型資料；完整 dtype 將在 pandas 成功安裝後再次以 dataframe contract test 驗證。

### 參考專案審查

- `references/DIC-2-50-startup-main.zip` 存在，大小 1,379,606 bytes。
- ZIP 共有 17 個 entries，包含 `README.md`、`main.py`、`index.html`、`style.css`、`app.js`、`model_data.js`、本地 `chart.min.js`、資料與圖片資產。
- 已讀取 README 與 Python 程式，並檢視 HTML sections、JavaScript event/chart 結構及 CSS theme/responsive 結構。
- 可借鏡項目：Bento Grid、深淺主題、漸層 KPI、Chart.js、本地 Chart.js fallback、feature stepper、What-If controls、responsive breakpoints。
- 不可沿用項目：50 Startups 原始資料、模型數值、靜態 KPI、係數、區間與結論。
- 發現參考程式自身有 display/train feature 名稱不一致的風險（k=5 顯示欄與實際訓練欄不同），因此本專案必須由同一份模型 metadata 生成畫面與報告，不能手工維護兩套名稱或數值。
- 參考程式使用單次 80/20 holdout 並以 test set 選最佳 k，不符合本 PDD 的訓練內 CV、validation 選模與 final test 一次評估要求；只能參考視覺與互動，不能照搬建模流程。

### Python 環境與依賴

- 已建立：`.venv`
- `.venv` Python：3.11.9
- `.venv` pip：24.0
- 已建立 `requirements.txt`，直接依賴：
  - numpy
  - pandas
  - scipy
  - scikit-learn
  - statsmodels
  - joblib
  - matplotlib
  - seaborn
  - pytest
- 安裝命令：`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- 安裝結果：**失敗**。執行環境無法解析套件索引主機；pip 對 `/simple/pip/` 與 `/simple/numpy/` 重試後回報無可用 distribution。這是網路/DNS 存取限制，不是 requirements 版本衝突。
- pip cache 沒有可用的本地 wheels；因此未採用不可靠的跨專案 site-packages 複製。

### Import smoke test

在新建 `.venv` 中測試下列 imports：

| Module | 結果 |
| --- | --- |
| numpy | FAIL — 未安裝 |
| pandas | FAIL — 未安裝 |
| scipy | FAIL — 未安裝 |
| sklearn | FAIL — 未安裝 |
| statsmodels | FAIL — 未安裝 |
| matplotlib | FAIL — 未安裝 |
| seaborn | FAIL — 未安裝 |
| joblib | FAIL — 未安裝 |
| pytest | FAIL — 未安裝 |

`pip check` 回報沒有 broken requirements，原因是目前環境只有 pip，尚未有待檢查的專案套件；此結果不代表依賴已安裝。

### `.gitignore` 驗證

已新增規則涵蓋：

- `.venv/` 與其他 virtual environment 名稱。
- Python bytecode、pytest/mypy/ruff/coverage cache。
- build、distribution、notebook、IDE 與 OS 暫存檔。
- `.env*`（保留 `.env.example`）、credentials、secrets、`kaggle.json`、PEM/key。
- `data/raw/*`，並允許未來追蹤 `data/raw/.gitkeep`。
- 本機模型 binaries 與 cache。

已用 `git check-ignore -v` 確認 `.venv`、`train.csv`、`test.csv`、`sample_submission.csv` 均命中預期規則。

### 本階段建立或修改的檔案

- 新增：`.gitignore`
- 新增：`requirements.txt`
- 新增：`docs/CODEX_DEVELOPMENT_LOG.md`
- 新增且被忽略：`.venv/`
- 未修改：`PDD.md`、三個 Kaggle CSV、參考 ZIP。

### 錯誤與修正紀錄

1. 先前 Phase 0 建立的 log 不在此次重新檢查的工作樹中；本次依當前真實狀態重建，未偽造消失原因。
2. `py` launcher 找不到 Python：改以 PATH 中的 Python 3.11.9 執行 `python -m venv .venv`，虛擬環境建立成功。
3. pip 無法連線套件索引：保留 `.venv` 與 requirements，記錄完整錯誤；需在可連線 PyPI 或有內部 mirror/wheelhouse 的使用者終端完成安裝。
4. GitHub 遠端 URL 正確但無法線上查詢：記錄 DNS 阻塞，未宣稱遠端 repository 狀態已驗證。

### 模型實驗結果

- 本階段未訓練任何模型，無模型分數、係數、預測或圖表。

### Git Commit 與部署狀態

- Commit：未執行；repository 尚無 commit。
- Push：未執行。
- GitHub Pages：未修改、未部署、未驗證。

### Phase 0 進入 Phase 1 Gate

目前判定：**尚未符合進入 Phase 1 的全部條件**。

已通過：

- 正確專案路徑。
- Git remote URL 與 branch 名稱。
- PDD v1.1 完整閱讀。
- 參考專案可讀且已審查。
- Kaggle 三個檔案存在、完整可解析、schema/筆數/缺值/id 驗證通過。
- Python 3.11 `.venv` 建立成功。
- `requirements.txt` 與安全 `.gitignore` 已建立。
- Kaggle raw data 與 `.venv` ignore 驗證通過。

未通過／阻塞：

- 必要 Python 套件尚未安裝。
- Import smoke test 尚未通過。
- GitHub 遠端 heads 無法由目前環境連線確認。

### 使用者可在正常網路的 PowerShell 執行

```powershell
cd "C:\Users\AidenXiao\source\HW2-Predict-the-Flood"
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

完成後應重新執行 import smoke test，記錄實際版本並視需要將 `requirements.txt` 固定為 exact versions。通過後才能開始 Phase 1 的 pandas schema contract、EDA 與模型 pipeline。

## 完整實作與交付建置

- 執行日期：2026-10-21（Asia/Taipei）
- 使用者確認套件安裝問題已排除；import smoke test 實測全部通過。
- 實際版本已固定於 `requirements.txt`：numpy 2.4.6、pandas 2.3.3、scipy 1.17.1、scikit-learn 1.9.1、statsmodels 0.15.0、matplotlib 3.11.2、seaborn 0.13.2、joblib 1.6.0、pytest 9.1.1。

### 重要技術決策

- 有標籤資料依 seed 42 分為 64% training、16% validation、20% final holdout。
- 為控制百萬筆資料的運算成本，35 個候選設定在 training-only 固定 200,000-row sample 上執行 5-fold CV；推薦模型凍結後以完整 80% development data 重訓，final test 只評估一次。
- 比較 Dummy、OLS、SelectKBest k=1..20、RFE k={5,10,15,20}、5 個 Ridge alpha、4 個 Lasso alpha。
- statsmodels 全特徵 OLS 作為統計推論模型，提供 CI/PI、BP、JB、DW 與 VIF；Ridge 不冒用 OLS 解析區間。
- 網站只載入 compact JSON/CSV，不發布百萬筆 Kaggle 原始資料；What-If 使用匯出的 raw-scale Ridge 係數。

### 實際模型結果

- CV 推薦模型：Ridge，alpha=10。
- Final holdout：MAE 0.0157925、MSE 0.000403207、RMSE 0.0200800、R² 0.844877、Adjusted R² 0.844863。
- 全特徵 OLS：RMSE 0.0200800、R² 0.844877，與 Ridge 幾乎相同。
- OLS 95% prediction interval：coverage 94.61%，平均寬度 0.07877。
- Durbin–Watson 1.99885；Breusch–Pagan 與 Jarque–Bera p < 0.001；最大 feature VIF 1.00367。
- 大樣本使異方差與常態性檢定對微小偏離非常敏感，報告搭配殘差圖與 Q-Q plot 解讀。

### 建立內容

- Python：`main.py`、`hw2.py`、`src/floodlab/` 分析套件。
- 真實產物：`outputs/figures/`、`outputs/tables/`、`outputs/run_metadata.json`、recommended model。
- 靜態網站：`web/index.html`、`style.css`、`app.js`、本地 Chart.js、JSON/CSV 與診斷圖。
- 報告：CRISP-DM 報告素材、NotebookLM 研究佔位、研究筆記表與繳交清單。
- QA：schema、metrics、Pipeline、interval、prediction parity、web contract 共 11 tests。
- 部署：`.github/workflows/deploy.yml` 發布 `web/` 至 GitHub Pages。

### 錯誤與修正

- 第一輪完成 35 個候選後，NumPy 2.x 對 DummyRegressor 二維常數的 scalar conversion 拒絕；改以 `np.ravel(...)[0]` 序列化後重跑成功。
- 修正 model selector change listener 的註冊位置，避免每次切換重複累積 handler。
- 本執行環境禁止 loopback socket，in-app browser 也無法連到 host localhost；因此無法完成實際瀏覽器截圖驗收。已完成 Node 語法檢查、JSON/資產 contract 與 pytest；使用者本機仍應執行一次視覺 smoke test。

### 測試結果

- `python -m compileall`：PASS。
- `node --check web/app.js`：PASS。
- `pytest -q`：11 passed in 2.27s。
- Python vs exported coefficient prediction parity：最大誤差 < 1e-8。
- Kaggle raw CSV 與 `.venv` 仍受 `.gitignore` 排除。

### 尚待使用者處理

- 提供實際學號並重新命名 `hw2.py` 與 ZIP。
- 完成 NotebookLM 摘要、來源核對與 GPT 對話 PDF。
- 排版並輸出最終 PDF 報告。
- 本機瀏覽器視覺驗收。
- GitHub Pages Settings 選擇 GitHub Actions；若本環境仍無網路，需由使用者執行 push。

### Git 狀態補充

- 已執行 `git add --all`，所有正式交付檔案均已 staged；`.venv` 與 Kaggle raw CSV 未被加入。
- `git commit -m "Build FloodLab regression analysis and dashboard"` 失敗，因 repository 與全域環境均未設定 `user.name` / `user.email`。
- 未擅自設定或猜測使用者的提交者 email；因此沒有 commit SHA，也未執行 push／部署。

### GitHub Pages 部署修正

- 首次 commit `6afb8c0` 已由 `AidenXiao0924` 推送至 `origin/main`；本機 HEAD 與 origin tracking ref 一致。
- GitHub Actions run `39591106424` 在 `actions/configure-pages@v5` 失敗，錯誤為 Pages site `Not Found`，不是測試或網站建置失敗。
- 依 GitHub annotation 建議，為 `configure-pages` 加入 `enablement: true`，讓 workflow 在既有 Pages/Actions 權限下完成 site enablement。

### 學號與 README 更新

- 使用者提供實際學號 `5115056040`。
- 將繳交入口 `hw2.py` 重新命名為 `5115056040_hw2.py`，並同步更新 README、報告模板與繳交清單。
- 使用者將網站截圖存為 `assets/dashboard_preview.png`；已檢查圖片內容並加入 README 的可點擊網站預覽。
