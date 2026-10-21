# Kaggle Predict the Flood (S4E5) 文獻研究與解法分析報告 - 校訂版

> NotebookLM 研究摘要（經整理與校訂）  
> 原始 NotebookLM 匯出保留於 `report/predict_the_flood_hw2_report.md`，本檔僅修正文義、引用與可比性說明。

## A. NotebookLM 研究摘要（經整理與校訂）

本研究以 NotebookLM 彙整 Kaggle Playground Series S4E5「Predict the Flood」的公開解法，並與本次 HW2 實驗分開討論。本次實驗使用 1,117,957 筆有標籤資料與 20 個數值特徵，在固定 `random_state=42` 的 64/16/20 切分下，比較 OLS、SelectKBest、RFE、Ridge 與 Lasso；模型以 training-only 的 200,000 筆樣本進行 5-fold CV，最後由 Ridge（alpha=10）在獨立 holdout 得到 R² 0.844877、RMSE 0.020080 [1,2]。OLS 的預測表現近似，另用於 VIF、殘差檢定及 95% 平均反應信賴區間與單筆觀測預測區間；這些統計推論不應視為 Ridge 的解析結果 [1]。外部資料指出，Linear Regression 與 CatBoost 在原始特徵上的表現接近 [3,4]，另有研究報告神經迴歸及競賽高分方案可達較高分數 [5,6]。然而外部結果可能來自不同 CV、holdout 或 Kaggle leaderboard，不能與本次 holdout 分數直接排序。列級統計特徵、非線性模型與 ensemble 是合理的後續實驗方向 [7,8]，但現有資料不足以斷言單一技巧就是領先成績的唯一原因。此比較著重方法、成本與可解釋性，不把異質評估數字當成同一競賽名次。整體而言，本次線性模型提供可重現、低成本且具統計解釋性的課堂基準；若追求競賽分數，仍需在一致驗證設計下另行測試特徵工程與複雜模型。

## B. 主流解法比較

> 注意：本次實驗的 CV、validation、final holdout 與外部來源的 CV 或 Kaggle leaderboard 所使用的樣本及流程不同。下表保留來源所報告的數值，但僅供方法層次比較，不作為嚴格的高低排名。

| 方法 | 結果來源與設定 | 優點 | 限制與本次實驗的關係 |
|---|---|---|---|
| Ridge（alpha=10） | 本次實驗：final holdout R² 0.844877、RMSE 0.020080 [1,2] | 係數穩定、訓練快速、可重現 | 本次選定模型；分數只代表本次固定切分 |
| OLS / Linear Regression | 本次 holdout 幾乎與 Ridge 相同；Suraj Wate 報告 CV/測試約 0.845 [1,3] | 可解釋係數，可作 VIF、殘差診斷與解析式 CI/PI | OLS 的 VIF、檢定和 CI/PI 不屬於 Ridge；外部切分不可直接比較 |
| SelectKBest / RFE + OLS | 本次以 k=1..20 與 k={5,10,15,20} 比較 [1] | 可檢查減少特徵後的精度成本 | 本資料 20 特徵皆有訊號，減少至 10 個特徵使 CV RMSE 明顯上升 |
| Lasso | 本次比較 alpha=0.0001、0.001、0.005、0.01 [1] | L1 可產生稀疏係數 | 懲罰增強時偏差上升；不可將係數顯著性比照 OLS |
| CatBoost | Suraj Wate 報告其結果略高於 Linear Regression [3,4] | 能處理非線性與互動 | 訓練成本較高；外部 CV/測試與本次 holdout 不直接可比 |
| XGBoost / LightGBM / Tabular foundation models | Oreshkin 等人的研究彙整多種 S4E5 結果 [5] | 提供非線性或預訓練表格模型的比較 | 評估設定與資源需求不同，不能據此推論在本次切分必然優於或劣於 Ridge |
| NIAQUE | 外部研究報告 S4E5 R² 0.867 [5] | 可學習高階非線性結構 | 架構與預訓練成本高；該外部數字不是本次 holdout 結果 |
| AutoGluon / ensemble | AutoGluon 彙整頁記錄 S4E5 領先方案 [6] | 自動組合多模型，可能提高競賽表現 | 可解釋性與部署複雜度較高；來源不足以確認各單項技巧的獨立貢獻 |
| 列級統計特徵、Boosting 與神經網路 | 競賽指南與公開實作提供可嘗試方向 [7,8] | 可加入 sum、mean、std 或非線性互動 | 是合理假設而非本次已驗證結論，必須在相同 CV 設計下重做消融實驗 |

## C. 研究結論與改進建議

1. **本次作業結論**：全 20 特徵的 OLS 與 Ridge 表現幾乎相同；Ridge（alpha=10）依 CV RMSE 被選為部署模型。SelectKBest 與 RFE 顯示大幅刪減特徵會降低準確度，Lasso 則呈現正則化強度增加時的偏差成本 [1,2]。
2. **統計診斷的歸屬**：VIF、Durbin-Watson、Breusch-Pagan、Jarque-Bera，以及 statsmodels 產生的 95% CI/PI 均針對 OLS。Ridge 的 L2 正則化用於穩定係數，但不等同於通過 OLS 假設檢定，也未在本專案中提供相同解析式區間。
3. **外部研究的解讀**：公開資料顯示 CatBoost、神經迴歸與 AutoML/ensemble 可能取得更高的外部評估分數 [3,5,6]，但因切分、訓練流程與 leaderboard 條件不同，只能作為候選方向，不能與本次 holdout 直接計算差距或宣稱顯著優越。
4. **後續優先項目**：在相同 fold 內加入列級統計與交互項，測試 CatBoost/GBDT，再以一致的 5-fold CV 做消融比較；所有前處理必須留在 Pipeline 內避免資料洩漏 [7,8,9]。

## D. 參考資料與來源對照

[1] 本專案 `report/HW2_report_template.md`，本次實驗設定、模型結果與 OLS 診斷。  
[2] 本專案 `README.md`，資料切分、部署方式與研究限制。  
[3] Suraj Wate, “Regression with a Flood Prediction Dataset.” https://surajwate.com/blog/regression-with-a-flood-prediction-dataset/  
[4] Suraj Wate, “S4E5-Flood-Prediction-Dataset.” https://github.com/surajwate/S4E5-Flood-Prediction-Dataset  
[5] Boris N. Oreshkin, Shiv Tavker, Dmitry Efimov, “Probabilistic Pretraining for Neural Regression.” https://arxiv.org/abs/2508.16355v1  
[6] AutoGluon AWESOME.md（Gitee mirror），S4E5 solution index. https://gitee.com/mirrors/autogluon/blob/master/AWESOME.md  
[7] Sudhanshu Tiwari, “From Baseline to Top 10%: A Practical Kaggle Competition Playbook.” https://uselessai.in/from-baseline-to-top-10-a-practical-kaggle-competition-playbook-702d1d9394f8  
[8] KartikeyBartwal, “Flood-Estimation-Kaggle-Competition.” https://github.com/KartikeyBartwal/Flood-Estimation-Kaggle-Competition  
[9] Udacity, “Cross Validation in Machine Learning: Techniques and Best Practices.” https://www.udacity.com/blog/cross-validation-in-machine-learning-techniques-and-best-practices/

未保留原始匯出中缺少完整 URL 或不能直接支持正文的來源；來源 [1]、[2] 是本次實驗內部文件，不是外部研究證據。
