"""Build the final HW2 PDF from verified project outputs."""
from pathlib import Path
import csv
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, ListFlowable, ListItem
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "5115056040_hw2.pdf"
FIG = ROOT / "outputs" / "figures"
ASSET = ROOT / "assets" / "dashboard_preview.png"

FONT = r"C:\Windows\Fonts\msjh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msjhbd.ttc"
pdfmetrics.registerFont(TTFont("CJK", FONT, subfontIndex=0))
pdfmetrics.registerFont(TTFont("CJK-Bold", FONT_BOLD, subfontIndex=0))

NAVY = colors.HexColor("#08212C")
TEAL = colors.HexColor("#18BFC1")
CYAN = colors.HexColor("#21A9D6")
INK = colors.HexColor("#21313C")
MUTED = colors.HexColor("#60717E")
PALE = colors.HexColor("#EAF7F7")
LINE = colors.HexColor("#C8D8DD")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="BodyCJK", fontName="CJK", fontSize=9.2, leading=14, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallCJK", fontName="CJK", fontSize=7.4, leading=10.5, textColor=INK))
styles.add(ParagraphStyle(name="HeaderCJK", fontName="CJK-Bold", fontSize=7.4, leading=10.5, textColor=colors.white))
styles.add(ParagraphStyle(name="Note", fontName="CJK", fontSize=8, leading=12, textColor=MUTED, backColor=PALE, borderPadding=7, spaceBefore=5, spaceAfter=8))
styles.add(ParagraphStyle(name="H1CJK", fontName="CJK-Bold", fontSize=18, leading=23, textColor=NAVY, spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name="H2CJK", fontName="CJK-Bold", fontSize=13, leading=18, textColor=NAVY, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="H3CJK", fontName="CJK-Bold", fontSize=10.5, leading=15, textColor=CYAN, spaceBefore=5, spaceAfter=3))
styles.add(ParagraphStyle(name="TitleCJK", fontName="CJK-Bold", fontSize=26, leading=34, alignment=TA_CENTER, textColor=NAVY))
styles.add(ParagraphStyle(name="SubTitleCJK", fontName="CJK", fontSize=12, leading=18, alignment=TA_CENTER, textColor=MUTED))

def p(text, style="BodyCJK"):
    return Paragraph(text, styles[style])

def bullet(items):
    return ListFlowable([ListItem(p(x), leftIndent=8) for x in items], bulletType="bullet", leftIndent=17, bulletFontName="CJK", bulletFontSize=6, spaceAfter=5)

def table(data, widths, header=True, font=7.3):
    cells = []
    for row_index, row in enumerate(data):
        style = "HeaderCJK" if header and row_index == 0 else "SmallCJK"
        cells.append([p(str(c), style) for c in row])
    t = Table(cells, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("GRID", (0,0), (-1,-1), 0.35, LINE),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]
    if header:
        commands += [("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white)]
    for r in range(1 if header else 0, len(data)):
        if r % 2 == 0:
            commands.append(("BACKGROUND", (0,r), (-1,r), colors.HexColor("#F5F9FA")))
    t.setStyle(TableStyle(commands))
    return t

def fig(path, caption, width=16.5*cm):
    im = Image(str(path))
    im._restrictSize(width, 10.8*cm)
    return KeepTogether([im, Spacer(1, 3), p(caption, "SmallCJK"), Spacer(1, 6)])

def page_decor(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
    canvas.line(1.7*cm, 1.45*cm, w-1.7*cm, 1.45*cm)
    canvas.setFont("CJK", 7.5); canvas.setFillColor(MUTED)
    canvas.drawString(1.7*cm, 0.95*cm, "物聯網應用與資料分析 HW2 · Predict the Flood")
    canvas.drawRightString(w-1.7*cm, 0.95*cm, f"第 {doc.page} 頁")
    canvas.restoreState()

def cover(canvas, doc):
    canvas.saveState(); w,h=A4
    canvas.setFillColor(NAVY); canvas.rect(0,0,w,h,fill=1,stroke=0)
    canvas.setFillColor(TEAL); canvas.rect(0,h-1.0*cm,w,1.0*cm,fill=1,stroke=0)
    canvas.restoreState()

doc = BaseDocTemplate(str(OUT), pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm, topMargin=1.55*cm, bottomMargin=1.75*cm,
                      title="Predict the Flood - Multiple Linear Regression HW2", author="蕭程勻（學號 5115056040）")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=page_decor)])

S=[]
# Cover is built as a regular page with dark blocks simulated using a full-width table.
S += [Spacer(1, 1.6*cm), p("FLOODLAB · PREDICT THE FLOOD", "SubTitleCJK"), Spacer(1, 1.1*cm),
      p("多元線性回歸、特徵選擇<br/>與洪水機率預測", "TitleCJK"), Spacer(1, 0.8*cm),
      p("Kaggle Playground Series S4E5 · HW2 最終報告", "SubTitleCJK"), Spacer(1, 1.2*cm),
      table([["課程", "物聯網應用與資料分析"], ["學號", "5115056040"], ["姓名", "蕭程勻"], ["日期", "2026-10-21"]], [4*cm, 10*cm], header=False),
      Spacer(1, 1.2*cm), p("Repository", "H3CJK"), p("https://github.com/AidenXiao0924/HW2-Predict-the-Flood"),
      p("GitHub Pages", "H3CJK"), p("https://aidenxiao0924.github.io/HW2-Predict-the-Flood/"),
      Spacer(1, 1*cm), p("本報告所有模型分數與圖表均來自專案實際程式執行；未提交 Kaggle leaderboard，故不宣稱競賽排名。", "Note"), PageBreak()]

S += [p("摘要", "H1CJK"), p("本研究使用 Kaggle Playground Series S4E5「Predict the Flood」資料集，以 20 個數值特徵預測連續目標 FloodProbability。資料共 1,117,957 筆有標籤樣本，以固定亂數種子 42 分成 64% training、16% validation 與 20% final holdout。候選模型在 training-only 固定 200,000 筆樣本上進行 5-fold CV，比較 OLS、SelectKBest、RFE、Ridge 與 Lasso。CV 選出的 Ridge（alpha=10）在 final holdout 的 RMSE 為 0.020080、MAE 為 0.015793、R² 為 0.844877、Adjusted R² 為 0.844863。全特徵 OLS 表現幾乎相同，並另外用於回歸假設診斷與 95% 信賴／預測區間。研究結果是競賽資料中的統計關聯，不代表真實洪水預警或因果效果。"),
      p("關鍵字：Multiple Linear Regression、Ridge、Feature Selection、CRISP-DM、Prediction Interval", "Note"),
      p("實驗設計一覽", "H2CJK"), table([["項目","設定"],["資料","train.csv：1,117,957 × 22；20 features + id + target"],["切分","64% training / 16% validation / 20% final holdout"],["選模","training-only 200,000 rows、5-fold CV、CV RMSE"],["最終重訓","完整 80% development data"],["最佳模型","Ridge（alpha=10）"]], [4.2*cm,12.2*cm]), PageBreak()]

S += [p("1. CRISP-DM：Business Understanding", "H1CJK"),
      p("目標是以資料中的 20 個數值欄位預測 FloodProbability。成功標準以 CV RMSE 為主要選模依據，並完整報告 MAE、MSE、RMSE、R² 與 Adjusted R²。此資料是 Kaggle Playground 競賽資料，目標名稱雖含 probability，仍不可直接當成現實世界校準過的洪水機率。模型係數只表示關聯，不構成因果推論。"),
      p("2. CRISP-DM：Data Understanding", "H1CJK"),
      bullet(["train.csv 共 1,117,957 筆、22 欄；competition test 共 745,305 筆。", "20 個輸入特徵皆為數值型；另有唯一識別碼 id 與目標 FloodProbability。", "本次檢查無缺失值；target 範圍 0.285 至 0.725，中位數 0.505。", "單一特徵與目標的相關係數約 0.178 至 0.190，訊號分散在多個特徵。"]),
      fig(FIG/"target_distribution.png", "圖 1　FloodProbability 分布（由真實 train.csv 產生）", 14.5*cm), PageBreak()]

features=["MonsoonIntensity","TopographyDrainage","RiverManagement","Deforestation","Urbanization","ClimateChange","DamsQuality","Siltation","AgriculturalPractices","Encroachments","IneffectiveDisasterPreparedness","DrainageSystems","CoastalVulnerability","Landslides","Watersheds","DeterioratingInfrastructure","PopulationScore","WetlandLoss","InadequatePlanning","PoliticalFactors"]
feature_rows=[[str(i+1), features[i], str(i+11), features[i+10]] for i in range(10)]
S += [p("2.1 二十個輸入特徵", "H2CJK"), table([["#","特徵","#","特徵"]]+feature_rows,[0.7*cm,7.2*cm,0.7*cm,7.2*cm]),
      p("id 僅用於識別，不進入模型；FloodProbability 是預測目標。欄位名稱代表競賽設計的概念分數，報告不將其重新解釋為實際量測單位。", "Note"),
      fig(FIG/"feature_target_correlations.png", "圖 2　各特徵與目標的 Pearson 相關排序", 15*cm), PageBreak(),
      p("2.2 特徵相關結構", "H2CJK"), fig(FIG/"correlation_heatmap.png", "圖 3　20 個特徵與目標的相關矩陣", 16.2*cm),
      p("各特徵 VIF 最大值為 1.00367，未見明顯多重共線性。然而 VIF 低不代表誤差同方差或常態性成立，仍須分別診斷。", "Note"), PageBreak()]

S += [p("3. CRISP-DM：Data Preparation", "H1CJK"),
      bullet(["以 random_state=42 固定結果；先保留 20% final holdout，再把其餘資料分成 64% training 與 16% validation。", "id 與 target 從特徵矩陣排除；官方 competition test 沒有真實 target，不用於計算 R²。", "SimpleImputer、StandardScaler、SelectKBest 與 RFE 放入 sklearn Pipeline，僅在各 training fold 內 fit，避免資料洩漏。", "候選模型的 5-fold CV 使用 training-only 固定 200,000 筆抽樣；選模後以完整 80% development data 重訓，final holdout 只作最後一次評估。"]),
      p("4. CRISP-DM：Modeling", "H1CJK"),
      table([["模型","設定","目的"],["Dummy Mean","平均值預測","無資訊基準"],["OLS","全部 20 特徵","主要線性回歸與統計診斷"],["SelectKBest + OLS","f_regression，k=1..20","單變量篩選"],["RFE + OLS","k=5、10、15、20","遞迴消除特徵"],["Ridge","alpha=0.01、0.1、1、10、100","L2 正則化"],["Lasso","alpha=0.0001、0.001、0.005、0.01","L1 正則化與稀疏化"]],[4*cm,6.2*cm,6.1*cm]),
      p("Ridge 的 L2 懲罰可縮小並穩定係數，但本資料 VIF 原本已很低，因此 Ridge 與 OLS 預測幾乎一致。OLS 的 p-value、VIF 與解析式區間不能直接套用到 Ridge。", "Note"), PageBreak()]

comparison=[["模型","特徵數","CV RMSE","Validation RMSE"],["Ridge alpha=10","20","0.0200766","0.0200757"],["OLS all","20","0.0200766","0.0200757"],["SelectKBest k=20","20","0.0200766","0.0200757"],["RFE k=20","20","0.0200766","0.0200757"],["Lasso alpha=0.0001","20","0.0200828","0.0200856"],["SelectKBest k=10","10","0.0402423","0.0403162"],["RFE k=10","10","0.0403996","0.0403864"],["Dummy Mean","0","0.0510754","0.0510959"]]
S += [p("4.1 特徵選擇與交叉驗證比較", "H2CJK"), table(comparison,[5.2*cm,2.4*cm,4.2*cm,4.2*cm]),
      p("全 20 特徵模型的 CV RMSE 最低且彼此極接近。SelectKBest 或 RFE 減至 10 個特徵時，CV RMSE 約增加到 0.040；表示訊號分散於多個欄位。Ridge alpha=10 以最小的 CV RMSE 被選中，差距非常小，實務上應解讀為與 OLS 同一表現層級。", "BodyCJK"),
      fig(FIG/"cv_feature_count.png", "圖 4　特徵數與交叉驗證表現", 15.5*cm), PageBreak(),
      fig(FIG/"model_comparison.png", "圖 5　候選模型比較（同一 CV 設定）", 15.8*cm),
      fig(FIG/"coefficients.png", "圖 6　全特徵線性模型係數", 15.8*cm), PageBreak()]

S += [p("5. CRISP-DM：Evaluation", "H1CJK"),
      p("推薦模型 Ridge（alpha=10）與全 20 特徵 OLS 的 final holdout 結果如下。兩者差異小於顯示位數；最終推薦 Ridge 是依事先設定的 CV RMSE 規則，而非使用 holdout 反覆挑選。"),
      table([["模型","MAE","MSE","RMSE","R²","Adjusted R²"],["Ridge alpha=10","0.0157925","0.000403207","0.0200800","0.844877","0.844863"],["OLS all","0.0157925","0.000403207","0.0200800","0.844877","0.844863"]],[3.3*cm,2.6*cm,3.0*cm,2.7*cm,2.4*cm,2.7*cm]),
      p("指標定義", "H2CJK"),
      bullet(["MAE：平均絕對誤差，與 target 同尺度。", "MSE：平方誤差平均，對大誤差較敏感。", "RMSE：MSE 開根號，回到 target 尺度；本專案用於 CV 選模。", "R²：模型相對於平均值基準所解釋的變異比例。", "Adjusted R²：依樣本數 n 與特徵數 p 修正 R²，公式為 1-(1-R²)(n-1)/(n-p-1)。"]),
      p("5.1 OLS 回歸假設與殘差診斷", "H2CJK"),
      table([["檢查","實際結果","解讀"],["線性／殘差圖","見圖 7","殘差整體以 0 為中心，但仍需搭配異質變異檢定"],["Durbin-Watson","1.99885","未見明顯一階自相關；資料非時間序列，解讀有限"],["Breusch-Pagan","p < 0.001","拒絕同方差；大樣本會放大微小偏離"],["Jarque-Bera","p < 0.001","殘差不完全常態；skew=0.6946、excess kurtosis=1.0898"],["VIF","max=1.00367","未見明顯多重共線性"]],[3.3*cm,3.4*cm,9.5*cm]), PageBreak(),
      fig(FIG/"residuals_vs_predicted.png", "圖 7　OLS 殘差對預測值", 16*cm),
      fig(FIG/"residual_qq.png", "圖 8　OLS 殘差 Q-Q 圖", 15.3*cm), PageBreak()]

S += [p("5.2 OLS 95% 信賴區間與預測區間", "H2CJK"),
      p("statsmodels OLS 的平均反應 95% 信賴區間（confidence interval, CI）描述在指定特徵下平均預測值的不確定性；單筆觀測 95% 預測區間（prediction interval, PI）還包含個別誤差，因此較寬。本次 final holdout 的 PI coverage 為 94.61%，平均寬度為 0.07877。該區間只屬於 OLS 診斷，未冒用為 Ridge 的解析區間。"),
      fig(FIG/"ols_prediction_intervals.png", "圖 9　OLS 預測值、95% 平均反應信賴區間與單筆預測區間", 16.4*cm),
      p("限制：coverage 是特定資料切分上的經驗比例；BP 與 JB 檢定顯示理想假設並未完全成立，因此區間應視為課堂上的 OLS 推論示範，而非現實災害風險保證。", "Note"), PageBreak()]

S += [p("6. CRISP-DM：Deployment", "H1CJK"),
      bullet(["Python 將模型係數、評估結果、圖表點與少量真實樣本匯出為 compact JSON/CSV；網站不下載百萬筆原始資料。", "What-If simulator 使用 Ridge 匯出的原始尺度係數計算，並以自動化測試確認 Python/JavaScript 預測一致。", "網站以 HTML/CSS/Vanilla JavaScript 與 Chart.js 建置，由 GitHub Actions 發布 web/ 至 GitHub Pages。", "Ridge 頁面不顯示 OLS 的解析式 CI/PI；區間只呈現在 OLS diagnostics。"]),
      fig(ASSET, "圖 10　FloodLab GitHub Pages Dashboard 首頁截圖", 16.7*cm),
      p("Repository：https://github.com/AidenXiao0924/HW2-Predict-the-Flood"),
      p("Pages：https://aidenxiao0924.github.io/HW2-Predict-the-Flood/"), PageBreak()]

summary="本研究以 NotebookLM 彙整 Kaggle Playground Series S4E5「Predict the Flood」的公開解法，並與本次 HW2 實驗分開討論。本次實驗使用 1,117,957 筆有標籤資料與 20 個數值特徵，在固定 random_state=42 的 64/16/20 切分下，比較 OLS、SelectKBest、RFE、Ridge 與 Lasso；模型以 training-only 的 200,000 筆樣本進行 5-fold CV，最後由 Ridge（alpha=10）在獨立 holdout 得到 R² 0.844877、RMSE 0.020080 [1,2]。OLS 的預測表現近似，另用於 VIF、殘差檢定及 95% 平均反應信賴區間與單筆觀測預測區間；這些統計推論不應視為 Ridge 的解析結果 [1]。外部資料指出，Linear Regression 與 CatBoost 在原始特徵上的表現接近 [3,4]，另有研究報告神經迴歸及競賽高分方案可達較高分數 [5,6]。然而外部結果可能來自不同 CV、holdout 或 Kaggle leaderboard，不能與本次 holdout 分數直接排序。列級統計特徵、非線性模型與 ensemble 是合理的後續實驗方向 [7,8]，但現有資料不足以斷言單一技巧就是領先成績的唯一原因。此比較著重方法、成本與可解釋性，不把異質評估數字當成同一競賽名次。整體而言，本次線性模型提供可重現、低成本且具統計解釋性的課堂基準；若追求競賽分數，仍需在一致驗證設計下另行測試特徵工程與複雜模型。"
S += [p("7. NotebookLM 研究摘要", "H1CJK"), p("（經整理與校訂；原始匯出檔另行保留）", "Note"), p(summary),
      p("7.1 外部方法比較", "H2CJK"),
      table([["方法／來源","來源報告內容","與本次 Ridge 的正確比較方式"],["Linear / CatBoost [3,4]","外部測試或 CV 約 0.845，CatBoost略高","設定不同，只能說明兩類模型在公開實作中接近"],["NIAQUE [5]","外部研究報告 S4E5 R² 0.867","不是本次 holdout；可視為高成本非線性候選"],["AutoGluon / ensemble [6]","彙整頁記錄領先 S4E5 方案","不能由彙整頁單獨歸因於某一特徵技巧"],["Row statistics / boosting [7,8]","公開指南與實作建議的方向","需在相同 folds 中作消融實驗後才能下結論"]],[4.1*cm,5.9*cm,6.4*cm]),
      p("研究結論", "H2CJK"),
      bullet(["本次 OLS/Ridge 是低成本、可重現且符合課堂多元線性回歸要求的強基準。", "外部 leaderboard、CV 與本次 holdout 不可直接比較，也不能由數字差異宣稱統計顯著。", "後續可在相同 Pipeline 與 folds 中加入 row sum/mean/std、GBDT 或 ensemble，再做消融比較。", "OLS 診斷與 CI/PI 屬於 OLS；Ridge 正則化不等同於 OLS 統計推論。"]), PageBreak()]

refs=["[1] 本專案 HW2_report_template.md：本次實驗設定、模型結果與 OLS 診斷。","[2] 本專案 README.md：資料切分、部署方式與研究限制。","[3] Suraj Wate, Regression with a Flood Prediction Dataset. https://surajwate.com/blog/regression-with-a-flood-prediction-dataset/","[4] Suraj Wate, S4E5-Flood-Prediction-Dataset. https://github.com/surajwate/S4E5-Flood-Prediction-Dataset","[5] B. N. Oreshkin, S. Tavker, D. Efimov, Probabilistic Pretraining for Neural Regression. https://arxiv.org/abs/2508.16355v1","[6] AutoGluon AWESOME.md (Gitee mirror), S4E5 solution index. https://gitee.com/mirrors/autogluon/blob/master/AWESOME.md","[7] S. Tiwari, From Baseline to Top 10%: A Practical Kaggle Competition Playbook. https://uselessai.in/from-baseline-to-top-10-a-practical-kaggle-competition-playbook-702d1d9394f8","[8] KartikeyBartwal, Flood-Estimation-Kaggle-Competition. https://github.com/KartikeyBartwal/Flood-Estimation-Kaggle-Competition","[9] Udacity, Cross Validation in Machine Learning: Techniques and Best Practices. https://www.udacity.com/blog/cross-validation-in-machine-learning-techniques-and-best-practices/"]
S += [p("8. GPT 輔助內容", "H1CJK"),
      p("GPT/Codex 協助環境檢查、程式架構、資料驗證、模型 Pipeline、測試、互動網站、NotebookLM 文字校訂與報告排版。模型分數、表格與圖表均由本機 Python 對真實 Kaggle CSV 實際執行產生。GPT 未代替使用者宣稱完成 NotebookLM 研究，也未虛構 Kaggle 提交、排名或對話紀錄。"),
      p("9. 限制與結論", "H1CJK"),
      bullet(["CV 使用 training-only 固定 200,000 筆抽樣以控制運算成本；最終模型仍以完整 80% development data 重訓。", "線性模型不能捕捉所有非線性與交互作用。", "BP/JB 在百萬級樣本下對微小偏離敏感，應搭配圖形與實務差異解讀。", "官方 competition test 無標籤且本專案未提交 Kaggle，因此沒有可宣稱的 leaderboard 分數或排名。"]),
      p("本次結果顯示，20 個特徵共同提供近似線性累加訊號。Ridge 與 OLS 均得到約 0.8449 的 holdout R²；特徵大幅刪減會明顯降低預測力。Ridge 適合作為穩定部署模型，OLS 則提供本課程要求的統計診斷與區間估計。", "BodyCJK"),
      p("參考資料", "H1CJK")] + [p(x, "SmallCJK") for x in refs] + [PageBreak(),
      p("附錄 A：重現方式與檔案說明", "H1CJK"),
      p("環境與執行", "H2CJK"), p("python -m venv .venv<br/>.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt<br/>.\\.venv\\Scripts\\python.exe main.py<br/>.\\.venv\\Scripts\\python.exe -m pytest -q"),
      p("主要檔案", "H2CJK"), bullet(["5115056040_hw2.py：學號命名的作業入口。", "main.py 與 src/：完整可重現分析程式。", "outputs/figures/ 與 outputs/tables/：本報告使用的真實輸出。", "report/predict_the_flood_hw2_report.md：原始 NotebookLM 匯出。", "report/predict_the_flood_hw2_report_edited.md：經整理與校訂版本。", "5115056040_hw2.pdf：本正式報告。"]),
      p("自動化驗收", "H2CJK"), p("專案測試涵蓋 schema、metrics、Pipeline leakage guard、Python/JavaScript prediction parity、interval contract 與網站必要資產。正式打包前再次執行 pytest，並檢查 PDF 可開啟、頁數、圖片清晰度與 ZIP 清單。")]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(S)
print(OUT)
