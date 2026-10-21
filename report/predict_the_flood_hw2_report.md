# Kaggle Predict the Flood (S4E5) 文獻研究與解法分析報告

**課程名稱**：物聯網應用與資料分析 HW2：Multiple Linear Regression  
**研究題目**：Kaggle Predict the Flood (Playground Series Season 4 Episode 5)  

---

## 一、NotebookLM 研究摘要

**本研究旨在探討 Kaggle Playground Series S4E5「Predict the Flood」競賽資料集之洪水機率預測解法，並評估多元線性回歸模型之適用性與限制 [1, 2]。** 資料集包含 1,117,957 筆樣本與 20 個數值特徵，目標為預測連續變數 `FloodProbability` [1]。

---

## 二、主流解法比較表

*註：不同實驗之資料切分方式、驗證集與評估指標（如 Holdout Test vs. Kaggle Private Leaderboard）可能有所差異，數值無法直接視為完全可比之絕對基準。*

| 模型名稱 | 來源或作者 | 特徵選擇或特徵工程方法 | 模型評估結果 | 優點 | 限制 | 與我的 Ridge 模型之比較 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ridge Regression (alpha=10)** | **HW2 本次實驗 [1, 2]** | 全 20 特徵，Pipeline 內含 SimpleImputer 與 StandardScaler | Holdout Test:<br>R² = **0.844877**<br>RMSE = **0.020080** | 訓練極快、具推廣穩定性，能防止多重共線性 | 無法捕捉複雜非線性特徵互動 | **本研究之評估基準**。可解釋性高，但未引入非線性工程。 |
| **OLS / Linear Regression** | Suraj Wate [3] / codingdidi [9] / HW2 報告 [1] | 原始 20 特徵，僅作 StandardScaler 標準化 | CV / Holdout R² ≈ **0.8443–0.8449** | 運算速度極快（<1秒/Fold），提供完整殘差診斷與預測區間 | 對異常值較敏感，缺乏 L2 正則化約束 | 表現與 Ridge 幾乎相同，OLS 95% 預測區間涵蓋率達 94.61% [1]。 |
| **CatBoost Regressor** | Suraj Wate [3, 4] / arXiv (Oreshkin et al.) [5] | 原始 20 特徵，5-Fold CV | Kaggle Private R² = **0.845**<br>(Suraj Wate CV R² = 0.846 [3]) | 表現略優於線性模型，抗過擬合能力強 | 訓練耗時（約 50 秒/Fold），邊際提升效益有限 | 於原始特徵下略高於我的 Ridge（R² 差距約 0.001），但計算成本高出數十倍。 |
| **XGBoost Regressor** | Sayed / siukeitin / arXiv 論文 [5] | 原始 20 特徵 | Kaggle Private R² = **0.842** (Rank 2304) [5] | 具備 L1/L2 正則化，特徵重要性評估方便 | 預設參數於此資料集表現略低於 CatBoost | 效能略低於我的 Ridge 模型，顯示單純樹模型在原始特徵上未顯現優勢。 |
| **LightGBM Regressor** | dataWr3cker / Masoudi / arXiv 論文 [5] | 原始 20 特徵 | Kaggle Private R² = **0.766** (Rank 2557) [5] | 直方圖分桶，大資料集訓練速度極快 | 葉片生長（Leaf-wise）在未調參時容易於此資料集過擬合 | 表現明顯低於我的 Ridge 模型（R² 0.8449 vs 0.766），需仔細調校 num_leaves。 |
| **TabDPT & TabPFN** | arXiv 論文 (Oreshkin et al.) [5] | 原始特徵（TabPFN 需降採樣至 10k 筆） | TabDPT R² = **0.804**<br>TabPFN R² = **0.431** [5] | 表格資料基底預訓練模型，免手動調參 | 記憶體與 Context Size 受限，大資料集嚴重退化 | 表現大幅低於我的 Ridge 模型，證明大型表格基底模型在百萬級資料量下擴展性較差。 |
| **NIAQUE (Deep Neural Regression)** | arXiv 論文 (Oreshkin et al.) [5] | 全域預訓練 + 微調，不需手動特徵工程 | NIAQUE-Pretrain R² = **0.867** (Rank 935) [5] | 具備動態分位數估計與強大跨資料集遷移能力 | 架構複雜，需 GPU 資源進行長時預訓練 | 表現顯著優於我的 Ridge 模型（R² 0.867 vs 0.8449），展現神經網路擷取高階特徵之潛力。 |
| **Kaggle 頂尖解法 / AutoGluon** | Alexandre Daubas [6] / Heller / Aldparis | **列統計量特徵工程**（Row sum/mean）+ 多模型 Ensemble [6, 7] | Kaggle Private R² = **0.869** (Rank 1) [5, 6] | 結合特徵互動與 AutoML（AutoGluon）堆疊，精準度最高 | 可解釋性低、部署複雜度高 | 顯著優於我的 Ridge 模型。證明關鍵突破來自「列級特徵工程」而非僅靠單一模型。 |
| **AdaBoost & Neural Net (Keras Tuner)** | KartikeyBartwal [8] | 數據清理與特徵工程 [8] | *來源未提供具體數據* | 提供神經網路調參與 Boosting 實驗腳本 | *來源未提供* | *來源未提供定量分數無法比較*。 |

---

## 三、研究結論與改進建議

### 1. 選用 Multiple Linear Regression、Ridge 與特徵選擇之合理性
在 Predict the Flood 資料集中，20 個數值特徵在未經過非線性轉換前，其與目標變數間展現出強烈的線性累加特性 [1, 3]。**實驗證明，簡單的線性回歸與 Ridge 模型能在不到 1 秒的運算時間內達到 R² 0.8449 [1, 3]。** 相較於耗時且易過擬合的複雜模型，Ridge 回歸不僅能有效穩定特徵係數，還能提供完整的回歸診斷（如 VIF、Durbin-Watson）與 OLS 95% 預測區間（涵蓋率達 94.61%）[1]，作為學術報告與實務 Baseline 具有極高合理的推論價值。

### 2. 值得學習的 Kaggle 競賽技術
分析頂尖解法發現，單靠單一模型調參無法突破 R² 0.845 的瓶頸 [3, 5]。**最關鍵的突破來自「列級特徵工程」（Row-wise feature engineering），例如計算每筆樣本 20 個特徵的總和、平均值與標準差 [7]。** 此外，結合 GBDT（CatBoost/XGBoost）、AutoGluon 與預訓練神經網路（如 NIAQUE）的多樣化模型堆疊（Stacking/Blending），也是將 R² 提升至 0.867–0.869 的核心關鍵 [5, 6, 7]。

### 3. 未來改善方向
- **預測準確度**：構建跨特徵的列統計量（Row summary statistics）與交互項 [7]，並引進 CatBoost 與 LightGBM 進行 Blending [3, 10]。
- **模型穩定性**：建立嚴格的 5-Fold Cross-Validation 管道，並將所有預處理鎖定於 Fold 內部以杜絕資料洩漏 [4, 11]。
- **可解釋性**：搭配 SHAP 值的特徵歸因分析與回歸預測區間 [1]，在提升預測能力的同時保持模型的透明度與信任度。

---

## 四、參考資料與來源對照表

[1] **`HW2_report_template.md`**
* **作者 / 發布單位**：本作業作者（學號：5115056040）
* **原始網址 URL**：未提供原始網址（本機專案 Markdown 文件 ）
* **來源類型**：學生課程報告素材 (Markdown Template)
* **支持之具體內容**：支持 HW2 實驗數據設定（1,117,957 筆資料、20 個數值特徵）、最佳模型 Ridge (alpha=10) Holdout 評估結果（MAE 0.015793, RMSE 0.020080, R² 0.844877）、OLS 95% 預測區間涵蓋率（94.61%）及殘差診斷結果。

[2] **`README.md`**
* **作者 / 發布單位**：本作業作者（AidenXiao0924 / 學號：5115056040）
* **原始網址 URL**：未提供原始網址（本機專案 Markdown 文件 ）
* **來源類型**：學生專案說明文件 (Markdown README)
* **支持之具體內容**：支持專案架構（64/16/20 切分、CRISP-DM 流程）、GitHub Pages Dashboard 部署與研究限制（未提交 Kaggle 競賽、無官方排名）。

[3] **`Regression with a Flood Prediction Dataset - Suraj Wate`**
* **作者 / 發布單位**：Suraj Wate
* **原始網址 URL**：https://surajwate.com/blog/regression-with-a-flood-prediction-dataset/
* **來源類型**：技術部落格文章 (Blog Post)
* **支持之具體內容**：支持在原始 20 個特徵上 CatBoost (R² 0.8456 / CV 0.846) 與 Linear Regression (R² 0.8443 / CV 0.845) 準確度極為接近之結論，以及線性回歸訓練速度快數十倍（<1 秒/Fold vs ~50 秒/Fold）的運算效率對比。

[4] **`surajwate/S4E5-Flood-Prediction-Dataset - GitHub`**
* **作者 / 發布單位**：Suraj Wate
* **原始網址 URL**：https://github.com/surajwate/S4E5-Flood-Prediction-Dataset
* **來源類型**：GitHub 程式碼儲存庫 (GitHub Repository)
* **支持之具體內容**：支持 Kaggle S4E5 的專案架構（Stratified K-Fold）、`model_dispatcher.py` 與 10 種模型之 5-Fold 交叉驗證日誌。

[5] **`Probabilistic Pretraining for Neural Regression - arXiv`**
* **作者 / 發布單位**：Boris N. Oreshkin, Shiv Tavker, Dmitry Efimov (Amazon / arXiv)
* **原始網址 URL**：https://arxiv.org/abs/2508.16355v1
* **來源類型**：學術預印本論文 (arXiv Research Paper)
* **支持之具體內容**：支持 NIAQUE 預訓練神經網路於 S4E5 達到 R² 0.867 (Rank 935)；提供原始特徵下 GBDT/Neural 基線數字（CatBoost R² 0.845, XGBoost R² 0.842, LightGBM R² 0.766, TabNet R² 0.842, TabDPT R² 0.804, TabPFN R² 0.431），以及優勝解法達到 R² 0.869 之競賽數據。

[6] **`AWESOME.md · Gitee 极速下载/autogluon`**
* **作者 / 發布單位**：AutoGluon 開源團隊 (Nick Erickson 等) / Gitee 鏡像
* **原始網址 URL**：https://gitee.com/mirrors/autogluon/blob/master/AWESOME.md
* **來源類型**：開源軟體官方文件 / Kaggle 解法彙整 (GitHub/Gitee Repository Doc)
* **支持之具體內容**：支持 Kaggle Playground Series S4E5 第一名冠軍解法 Alexandre Daubas (`adaubas`) 使用 AutoGluon (v1.1 Tabular) 取得 Rank 1/2788 (R² ≈ 0.869) 之官方紀錄。

[7] **`From Baseline to Top 10%: A Practical Kaggle Competition Playbook - UselessAI.in`**
* **作者 / 發布單位**：Sudhanshu Tiwari / UselessAI.in
* **原始網址 URL**：https://uselessai.in/from-baseline-to-top-10-a-practical-kaggle-competition-playbook-702d1d9394f8
* **來源類型**：技術部落格 / Kaggle 競賽指南 (Technical Blog / Playbook)
* **支持之具體內容**：支持「列級特徵工程」（Row-wise feature engineering、統計量與交叉項）、多模型 Blending/Stacking 與 Optuna 超參數調參等突破表格資料效能瓶頸的核心技術。

[8] **`KartikeyBartwal/Flood-Estimation-Kaggle-Competition - GitHub`**
* **作者 / 發布單位**：KartikeyBartwal
* **原始網址 URL**：https://github.com/KartikeyBartwal/Flood-Estimation-Kaggle-Competition
* **來源類型**：GitHub 程式碼儲存庫 (GitHub Repository)
* **支持之具體內容**：支持參賽者使用 AdaBoost 與 Keras Tuner 進行神經網路超參數調整、R² 評估指標設定與特徵預處理之實作方式。

[9] **`Win Kaggle's Flood Prediction Challenge (Complete Solution)`**
* **作者 / 發布單位**：codingdidi (YouTube Channel)
* **原始網址 URL**：未提供原始網址（YouTube 影片標題，網址未於文本中標明）
* **來源類型**：YouTube 技術教學影片 (YouTube Tutorial Video)
* **支持之具體內容**：支持 Kaggle S4E5 初階段 Linear Regression Baseline 實作（R² ≈ 0.84），包含 Pandas 資料載入、特徵與目標變數分離、Train/Test Split 與評估流程。

[10] **`Ensemble Methods - Boosting (XGBoost, LightGBM, CatBoost) | AI and Machine Learning Tutorial`**
* **作者 / 發布單位**：Modern Age Coders
* **原始網址 URL**：https://learn.modernagecoders.com/resources/ai-and-machine-learning/ensemble-methods-and-boosting
* **來源類型**：技術教學文章 (Educational Tutorial)
* **支持之具體內容**：支持 Boosting 演算法（XGBoost, LightGBM, CatBoost）之理論機制（Leaf-wise vs Depth-wise、Histogram-based、Ordered Boosting）與特徵重要性（Feature Importance）解析。

[11] **`Cross Validation in Machine Learning: Techniques and Best Practices - Udacity`**
* **作者 / 發布單位**：Udacity (Moamen Abdelkawy)
* **原始網址 URL**：https://www.udacity.com/blog/cross-validation-in-machine-learning-techniques-and-best-practices/
* **來源類型**：技術部落格 / 教學指南 (Udacity Blog)
* **支持之具體內容**：支持交叉驗證（K-Fold, Stratified K-Fold）原理、避免資料洩漏（Data Leakage）的 Pipeline 封裝規範與模型泛化能力評估之合理性。

[12] **`Kaggle Solutions - Farid Rashidi`**
* **作者 / 發布單位**：Farid Rashidi
* **原始網址 URL**：https://www.kaggle.com/
* **來源類型**：競賽解法檔案庫 (Competition Solutions Archive)
* **支持之具體內容**：支持 Kaggle 各類競賽（包含 Playground Series S4E5）獲勝 Writeup 與討論區解法索引之參考依據。
