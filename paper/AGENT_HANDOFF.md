# 論文與實驗交接摘要

更新時間：2026-07-27 01:10（Asia/Taipei）

> 重點：**全部消融實驗完成，且全部分數已重評**。五項成對比較、二十五個維度檢定，**二十四項未達顯著**；
> 唯一例外（全規則注入組可讀性）未通過全研究層級校正，只能列為邊緣觀察。
> **本輪最重要的發現是方法面的**：`gpt-5.6-sol` 在不同日期的評分場次之間會整體漂移——同一批審查文字
> 隔約五日重判，涵蓋度上升 9.23 分。先前記為「批次／部署混淆」的落差，機制其實是這個。因此所有分數已於
> 兩個獨立場次各評一次並取平均，配對之兩組一律於同一場次評分。**效果量小於約 3 分者不可討論。**
> 消融結果已納入 **`paper/論文_v3.33.docx`**（§5.4＋表十一、表十二＋§6.3 第（9）（10）項），v3.32 保留為唯讀來源。
> 實驗端點為 `pr-thinker-2.sdpmlab.org`（Gemma），見第五節。

## 一、目前狀態總覽

- 論文最新版：`paper/論文_v3.33.docx`（新增 §5.4 消融分析、表十一、表十二、§6.3 第（9）（10）項）。
  產生腳本 `paper/_apply_ablation_v3_33.py`，以 `paper/論文_v3.32.docx` 為唯讀來源（勿覆寫 v3.32）。
  **待辦：在 Word 全選按 F9 更新欄位**，校正主目錄 5.4 與表十一、表十二的頁碼快取值。
- **固定三條無關規則注入組：完成。** 44／44 生成 + 44／44 評分（`gpt-5.6-sol`）+ 同部署對照彙整。
  - 生成於 pr-thinker-2（gemma-4-31B、bf16、LoRA、五階段、貪婪、`max_new_tokens=8192`）。
  - 其中 4 案（`copilot_only_code_14/2/3/4`）首夜遇 Cloudflare 525 失敗，已於 2026-07-24 補生成。
    **教訓：`run.log` 出現 `ALL DONE` 不代表全數成功，須逐案驗檔。**
- **同部署停用檢索基準：完成。** 44／44 生成 + 44／44 評分，於**同一** pr-thinker-2（伺服器組態
  雜湊 `467b7a9c…` 一致）、無注入（`extra_rules=[]`）；作為固定無關規則組與全規則注入組的**共同對照**。
- **全規則直接注入組：完成。** 44／44 生成 + 44／44 評分，每案經 `extra_rules` 注入全部 19 條相關規則
  （`direct_rules=19`）、同一 pr-thinker-2、乾淨無失敗；與同部署基準配對後五維均未達顯著（見第二節）。
- **未掛載 LoRA 基礎模型組：完成。** `multi_rag_on` 44／44 + `multi_rag_off` 44／44 生成（同部署連續跑批，
  07-25 07:37 → 07-26 03:36，約 20 小時）+ 88／88 評分；組內成對比較五維均未達顯著（見第二節）。
  全程僅 1 次 Cloudflare 520 重試且自動補回，88 案 `total_summary_result.md` 全部非空。
- **掛載 LoRA 相鄰部署組：完成。** `multi_rag_off` 44／44 生成（07-26 12:44 → 22:24，零失敗）+ 44／44 評分。
  伺服器拿掉 ablation-base overlay 後 `/healthz` 為 `lora_enabled=true`、`rag_corpus=relevant`、
  sha `80489dfc…`，與基礎模型組**逐項相同、僅 LoRA 旗標不同**。`multi_rag_on` 一臂未跑（依指示只做 44 案）。
- **全部八個條件臂已重評兩次**：場次 A（07-26 22:41–23:39）與場次 B（07-26 23:56–07-27 00:47），
  各 352 案、皆 0 失敗。逐案分數檔為 `our_score_gpt56sol_session0726.md` 與 `…0726b.md`，
  正式數值取兩場次平均。
- **研究資料已同步並封存**（見第五節）：`experiment_outputs/Results/` 含全部七個實驗組；
  `reproducibility/scores/` 維持同步（`aggregate_rag_quality.py` 與 `aggregate_irrelevant_quality.py`
  新增 `--score-file` 系列參數以支援重判分數集）；四份文件已全面改寫。

## 二、已定案量化結果（可用於論文）

### 問題偵測比較（多階段 vs 單一提示詞）

| 指標 | 多階段流程 | 單一提示詞 |
|---|---:|---:|
| 參考問題涵蓋率 | 0.592（197／333） | 0.498（166／333） |
| 問題宣稱正確率 | 0.988（474／480） | 0.988（329／333） |
| 描述性調和平均 | 0.740 | 0.663 |

涵蓋率與正確率非同一混淆矩陣；0.740／0.663 只可稱描述性調和平均，非標準二元 F1。

### 五項成對比較（皆 n=44、兩場次平均、Wilcoxon＋Holm）

完整表格（含樣本標準差、勝／同／負、兩場次區間）見
`datas/Research_Data/EXPERIMENT_RESULTS_TABLES.md` 第五至第十節。以下僅列成對平均差與表內 Holm p。

| 比較 | 可讀性 | 建設性 | 正確性 | 涵蓋度 | 完整性 |
|---|---:|---:|---:|---:|---:|
| RAG 開減關（掛載 LoRA） | −0.25 | −0.56 | −0.92 | −1.42 | −1.10 |
| RAG 開減關（基礎模型） | −0.25 | −0.10 | −1.12 | −0.35 | −0.66 |
| 無關規則注入減基準 | −0.18 | −0.15 | +0.98 | −0.11 | −0.15 |
| 全規則直接注入減基準 | **−0.66** | −0.49 | −1.05 | −1.19 | −1.20 |
| 掛載 LoRA 減基礎模型 | +0.00 | −0.30 | −0.53 | −1.05 | −0.52 |

二十五個維度檢定中**二十四項未達校正後統計顯著**。唯一例外為全規則直接注入組的可讀性
（表內 Holm p=0.012，兩場次方向一致：−0.84 與 −0.48，44 案中 25 案較差）；但把五張表共二十五次檢定
視為單一家族施以 Holm 校正後為 **0.060**，未達顯著。**寫論文時列為邊緣觀察，不可寫成發現。**

所有成對平均差絕對值 ≤ 1.42，與裁判場次雜訊同量級（見下）。因此可支持的敘述是「未觀察到可測得的
差異」，**不是**「證明兩組相同」（未做等價檢定，未預設等價界限）。

### 裁判場次漂移（本輪最重要的方法發現）

同一批審查文字、生成端零變動，只換評分場次重判：

| 重判間隔 | 可讀性 | 建設性 | 正確性 | 涵蓋度 | 完整性 |
|---|---:|---:|---:|---:|---:|
| 同日 12 小時（base 組 rag_off） | −0.02 | −0.02 | +0.52 | −0.25 | +0.27 |
| 相隔約五日（07-20 組 rag_off，07-22 00:20 → 07-26 23:00） | +1.02 | +2.68 | +2.84 | **+9.23** | +4.66 |

07-20 組涵蓋度由 75.27 重判為 84.50，**超過**當初被視為乾淨對照的 07-23 基準（82.93）。
先前把這個落差記為「生成批次／部署混淆」，機制判定錯誤；bind mount 導致程式碼變動的推論也不成立
（重判即可重現落差，生成端未動）。

由此確立兩條操作規則：**配對比較之兩組必須於同一評分場次評分**；**效果量須大於兩場次變動幅度（約 3 分）才可討論**。
單一場次的結果會誤導——全規則注入組在場次 A 的涵蓋度是 −2.64、場次 B 是 +0.25。

### 輔助觀察（非結論，但寫論文時須揭露）

- 掛載 LoRA 的審查平均**短 16%**（2,501 對 2,988 位元組，41／44 案較短）。涵蓋度與完整性偏好詳盡輸出，
  故「微調使輸出簡潔」與「微調使涵蓋度略降」在本資料無法區分。
- 全規則注入使審查**長 9%**（2,870 對 2,623），無關規則注入僅長 1%。長度未予控制。
- 基礎模型組與 07-20 組的檢索命中分布相同（25／44 案命中、平均 3.02 篇），故 RAG 無效不可歸因於未觸發。

## 三、待辦

待辦已移到 repo 根目錄的 `progress.md`（原本兩列選作實驗是 #2、#3；原第一列「論文納入 RAG／消融結果」已完成，見 `docs/updates/2026-09.md` U-20260922-02）。本檔只記實驗狀態、定案結果與證據。

## 四、可重複使用的教訓

1. `run.log` 的 `ALL DONE` 只代表迴圈跑完，**不代表每案成功**；Cloudflare 525／520／522 會讓個別案
   errored（目錄留空），必須逐案驗 `total_summary_result.md` 非空。失敗案重跑 driver 即會補（跳過已完成）。
2. **跨評分場次的分數不可直接相比**（本條已修正：原記為「不同批次／部署生成不可比」，機制判定錯誤）。
   07-20 基準相對後續組別的落差，重判同一批**未改動**的審查文字即可重現——涵蓋度 75.27 → 84.50，
   生成端完全沒動。規則是：**配對比較之兩組必須於同一評分場次評分**，且效果量須大於兩場次變動幅度
   （本研究約 3 分）才可討論。同日 12 小時內的重判是安全的（均值變動 ≤ 0.52），跨日則不是。
   生成端的批次／部署當然仍要對齊，但那是另一件事，不是那個落差的成因。
3. 長時工作用分離程序（PowerShell `Start-Process`）；本工作階段的 Claude Code 背景 bash 任務會被回收，
   獨立 OS 程序不受影響，`run.log` 為唯一真實來源。
4. 逾時／斷線後伺服器工作仍會獨立跑完（孤兒工作）；續跑前看 `/healthz` 的 gpu 狀態，重新提交會排隊。
5. 外部 Codex 評分（`gpt-5.6-sol` via codex CLI）曾觸額度上限（使用者可自行重置）；評分前先單案試打。
6. 成對案例用成對統計、多維度處理多重比較；「未達顯著」不等於證明兩組相同。
7. 論文不得出現本機路徑、實驗目錄名、私人主機名或未完成組別的預告文字（研究資料與 handoff 可記）。
8. **對 null 結果提出的解釋要留一組可否證它的對照**。「微調已內化規則」原是四組 null 中最順的說法，
   直到 no-LoRA 組跑出來才發現它被否定；若當時就把該解釋寫進論文，會變成無資料支持的宣稱。
   報告 null 時只寫觀察到什麼、以及哪些解釋已被排除，不要把尚未檢定的機制寫成結論。
9. **LLM-as-a-Judge 的分數要重複量測**。單一場次評分的雜訊足以讓成對差移動 3 分、讓顯著判定翻面：
   全規則注入組的可讀性在場次 A 顯著、場次 B 不顯著；涵蓋度在 A 是 −2.64、B 是 +0.25。至少評兩次取平均，
   並把兩次的差距當成該研究的效果解析度下限一併報告。只評一次就宣稱小效果，等於在報雜訊。
10. **檢查混淆時先找可直接查驗的機制，別停在最順的敘事**。「批次／部署混淆」聽起來合理、也促成了正確的
    補救動作（重跑同部署基準），但機制是錯的；真正的查驗只需要把舊審查重判一次，成本 8 分鐘、不佔 GPU。
    先前還一度推論是 bind mount 讓伺服器程式碼變動所致，同樣被這個查驗排除。

## 五、資料來源、部署與重現入口

- 論文最新版：`paper/論文_v3.33.docx`（唯讀來源 `paper/論文_v3.32.docx` 未修改）
- 固定無關規則組（完成）：`datas/Results/2026-07-22-gemma4-irrelevant-fixed3/`
  （封存：`datas/Research_Data/experiment_outputs/Results/2026-07-22-gemma4-irrelevant-fixed3/`）
- 同部署停用檢索基準（完成）：`datas/Results/2026-07-23-gemma4-ragoff-samedeploy/`
  （封存同名於 `experiment_outputs/Results/`；乾淨彙整 `irrelevant_vs_ragoff_quality_summary.{json,md}`）
- 全規則直接注入組（完成）：`datas/Results/2026-07-24-gemma4-allrules-direct/`
  （封存同名於 `experiment_outputs/Results/`；乾淨彙整 `allrules_vs_ragoff_quality_summary.{json,md}`）
- 未掛載 LoRA 基礎模型組（完成）：`datas/Results/2026-07-25-gemma4-base-nolora/`
- 掛載 LoRA 相鄰部署組（完成）：`datas/Results/2026-07-26-gemma4-lora-matched/`
- **五項正式表（兩場次平均）**：`datas/Results/judge_session_robustness_20260727.md`，
  另完整版見 `datas/Research_Data/EXPERIMENT_RESULTS_TABLES.md` 第四至第十節。
  各組目錄內的 `*_quality_summary.{json,md}` 為單一場次的舊版彙整，僅供追溯，**勿引用**。
- 驅動程式：`scores/gemma_experiment_driver.py`（env：`OUT_ROOT`、`CONDITIONS`、`PRTHINKER_BASE_URL`、
  `EXPECTED_*`、`JOB_MAX_SECS`；conditions 含 `multi_all_rules_direct`（全 19 條相關規則直接注入））
- 評分程式：`scores/codex_judge_rag.py`（`EXP_ROOT`、`CONDITIONS`、`SCORE_FILE`；裁判 `gpt-5.6-sol`、
  effort=medium；`SCORE_FILE` 可另存重判分數而不覆寫原分數；可續跑）
- 彙整程式：`scores/aggregate_rag_quality.py`（RAG 開關，`--score-file`／`--basename`）、
  `scores/aggregate_irrelevant_quality.py`（任一注入組 vs 基準，另有 `--inject-score-file`／
  `--baseline-score-file` 可指定兩組各自的分數檔，用於配對同場次重判的分數集）
- 研究資料封存：`datas/Research_Data/`（`README.md`、`EXPERIMENT_RESULTS_TABLES.md`、`REVIEWER_ISSUES.md`、
  `SNAPSHOT_STATUS.json`、`MANIFEST.sha256`）；重建 manifest：`paper/_build_research_data_manifest.py`

**部署現況**：

- `pr-thinker-2.sdpmlab.org` → `google/gemma-4-31B-it`，**本輪 Gemma 實驗端點**。部署狀態隨消融切換，
  以 `/healthz` 為準：先前 LoRA on／rag_corpus=irrelevant（sha `467b7a9c…`）；2026-07-25 起改為
  `lora_enabled=false`／rag_corpus=relevant（sha `80489dfc…`）跑 no-LoRA 基礎模型組
  （overlay `docker/docker-compose.ablation-base.yml`）。**2026-07-26 12:00 前後拿掉該 overlay 復原為
  `lora_enabled=true`／rag_corpus=relevant（sha `80489dfc…` 不變）**，跑掛載 LoRA 相鄰部署組；
  該組已於 07-26 22:24 跑完，**目前仍停在此組態**（即正式 LoRA 服務組態）。
  `/healthz` **不回報** `PRTHINKER_QUANT` 與主機端 repo 版本，故它不足以證明兩次執行的伺服器狀態完全相同；
  往後切換部署時應一併記錄 `docker inspect gemma4-server` 的環境變數與主機 `git rev-parse HEAD`。
- `pr-thinker.sdpmlab.org` → `Qwen/Qwen3-Coder-30B-A3B-Instruct`（前代 30B）。
  程式碼知識圖譜視覺化在 **`https://pr-thinker.sdpmlab.org/kg/`**（僅此台；pr-thinker-2 為 404）。
- 兩台經 Cloudflare，需瀏覽器 User-Agent；偶見 5xx，驅動已有重試；端點清單見各自 `/openapi.json`
  （無知識圖譜 API 路由，`/kg/` 由主機前端靜態服務）。

## 六、指令備查（各組皆已完成，不需執行；僅供未來重跑參考）

同部署停用檢索基準的生成：

```powershell
$env:OUT_ROOT='datas/Results/2026-07-23-gemma4-ragoff-samedeploy'
$env:CONDITIONS='multi_rag_off'; $env:PRTHINKER_BASE_URL='https://pr-thinker-2.sdpmlab.org'
$env:EXPECTED_LORA_ENABLED='true'; $env:EXPECTED_RAG_MODE='retrieval'; $env:EXPECTED_RAG_CORPUS='irrelevant'
$env:JOB_MAX_SECS='3600'
.\.venv\Scripts\python.exe scores\gemma_experiment_driver.py
```

重判一組並另存分數檔，再以兩組同場次的分數配對（評分可續跑；先單案試打再開全批）：

```powershell
$env:EXP_ROOT='datas\Results\2026-07-25-gemma4-base-nolora'
$env:CONDITIONS='multi_rag_on,multi_rag_off'
$env:SCORE_FILE='our_score_gpt56sol_session0726.md'
.\.venv\Scripts\python.exe scores\codex_judge_rag.py
.\.venv\Scripts\python.exe scores\aggregate_rag_quality.py `
    datas\Results\2026-07-25-gemma4-base-nolora `
    --score-file our_score_gpt56sol_session0726.md --basename rag_on_off_session0726
```

跨組配對（兩組各指定分數檔）：

```powershell
.\.venv\Scripts\python.exe scores\aggregate_irrelevant_quality.py `
    datas\Results\2026-07-26-gemma4-lora-matched\multi_rag_off `
    datas\Results\2026-07-25-gemma4-base-nolora\multi_rag_off `
    --out datas\Results\2026-07-26-gemma4-lora-matched `
    --basename lora_vs_base --inject-label "掛載 LoRA" --baseline-label "基礎模型" `
    --inject-score-file our_score_gpt56sol_session0726.md `
    --baseline-score-file our_score_gpt56sol_session0726.md
```
