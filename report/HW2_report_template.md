# Predict the Flood — Multiple Linear Regression HW2 報告素材

> 本文件由實際程式輸出整理，可直接作為最終 PDF 報告骨架。提交前請補上姓名、學號、NotebookLM 摘要、GPT 對話 PDF 資訊與網站截圖。

## 摘要

本研究使用 Kaggle Playground Series S4E5「Predict the Flood」資料集，以 20 個數值特徵預測連續目標 `FloodProbability`。資料共 1,117,957 筆有標籤樣本，依固定亂數種子 42 分為 64% training、16% validation 與 20% final holdout test。實驗比較 Multiple Linear Regression、SelectKBest、RFE、Ridge 與 Lasso，候選模型使用 training-only 200,000 筆固定抽樣進行 5-fold cross-validation，以兼顧百萬筆資料的運算成本與可重現性。CV 選出的 Ridge（alpha=10）在 final test 的 RMSE 為 0.020080、MAE 為 0.015793、R² 為 0.844877、Adjusted R² 為 0.844863。OLS 的測試表現幾乎相同，並提供可解釋係數、殘差診斷與 95% 信賴／預測區間。結果僅代表競賽資料中的統計關聯，不應解讀為真實洪水預警或因果效果。

## 1. Business Understanding

- 問題：以 20 個數值特徵預測 `FloodProbability`。
- 成功標準：以 CV RMSE 為主要選模依據，同時報告 MAE、MSE、R² 與 Adjusted R²。
- 限制：競賽合成／表格資料不能直接視為現實世界洪水風險；模型不提供因果推論。

## 2. Data Understanding

- train.csv：1,117,957 rows × 22 columns。
- 20 個輸入特徵、`id`、`FloodProbability`。
- 缺失值 0；`id` 無重複。
- target 範圍 0.285–0.725。
- 圖表：`outputs/figures/target_distribution.png`、`correlation_heatmap.png`、`feature_target_correlations.png`。

## 3. Data Preparation

- `id` 與 target 不進入特徵矩陣。
- 固定 `random_state=42`，64/16/20 切分。
- SimpleImputer、StandardScaler、SelectKBest、RFE 均置於 sklearn Pipeline；CV fold 內 fit，避免資料洩漏。
- 官方 competition `test.csv` 無真實 target，不用於本報告的 R² 評估。

## 4. Modeling

- Baseline：DummyRegressor(mean)。
- OLS：全 20 特徵 LinearRegression。
- SelectKBest：f_regression，k=1..20。
- RFE：k=5、10、15、20。
- Ridge：alpha=0.01、0.1、1、10、100。
- Lasso：alpha=0.0001、0.001、0.005、0.01。
- 5-fold CV 使用固定 training-only 200,000-row sample；選定模型後以完整 80% development data 重訓。

## 5. Evaluation

### 推薦模型 final holdout

| Model | MAE | MSE | RMSE | R² | Adjusted R² |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ridge, alpha=10 | 0.0157925 | 0.000403207 | 0.0200800 | 0.844877 | 0.844863 |

### OLS final holdout

| MAE | MSE | RMSE | R² | Adjusted R² |
| ---: | ---: | ---: | ---: | ---: |
| 0.0157925 | 0.000403207 | 0.0200800 | 0.844877 | 0.844863 |

完整模型比較：`outputs/tables/model_comparison.csv`。

### 回歸假設與殘差診斷

- Durbin–Watson：1.99885，未見明顯一階殘差自相關；但資料並非時間序列，解讀有限。
- Breusch–Pagan p < 0.001：拒絕同方差假設。樣本極大會放大微小偏離，應搭配 residual plot 解讀。
- Jarque–Bera p < 0.001：殘差不完全常態；skewness 0.6946、excess kurtosis 1.0898。
- 最大 feature VIF：1.00367，未見明顯多重共線性。
- OLS 95% prediction interval coverage：94.61%；平均寬度 0.07877。
- 圖表：`residuals_vs_predicted.png`、`residual_qq.png`、`ols_prediction_intervals.png`。

## 6. Deployment

- Python 產出 compact JSON，網站不下載百萬筆原始 CSV。
- What-If simulator 使用匯出的 Ridge 原始尺度係數計算。
- Ridge 不顯示冒用的 OLS 解析區間；95% CI/PI 位於 OLS diagnostics。
- GitHub Pages 發布 `web/`，所有資產使用相對路徑。

## 7. NotebookLM 研究摘要

**待使用者在 NotebookLM 完成公開解法研究後貼入至少 100 字摘要，建議 250–350 字，並保留來源引用。**

## 8. GPT 協助說明

GPT/Codex 協助環境檢查、程式架構、資料驗證、模型管線、測試、網站與報告素材。模型結果均由本機 Python 實際執行；完整原始對話由使用者另行匯出為 PDF。

## 9. 限制

- CV 使用 training-only 固定抽樣以降低運算成本。
- 線性模型無法表達複雜非線性互動。
- BP/JB 檢定在百萬筆樣本下對微小偏離非常敏感。
- Kaggle competition test 未提交，沒有可宣稱的 Kaggle score 或排名。
