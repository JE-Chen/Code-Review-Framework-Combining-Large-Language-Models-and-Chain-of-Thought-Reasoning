# 程式審核：prthinker

## 審核者

審核者＝工作區程式審核；日期＝2026-10-22；對象＝`Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning`（prthinker）；結論＝需修正。

## 審核規範

共通規範在工作區 repo [JE-Chen/Codes](https://github.com/JE-Chen/Codes) 的 `docs/code-review-standard.md`。下面留下 2026-10-22 這次審核所用的條款，讓審核紀錄的依據對得上那一次。之後的審核以工作區那份為準。本專案更嚴的條款仍以本節與本專案的 `CLAUDE.md` 為準。

1. 設計：策略、工廠、範本方法、登錄、倉儲與依賴注入維持現有分層；不把傳輸、管線與平台寫在一起。
2. 可讀性：認知複雜度 ≤ 15、函式 ≤ 80 行、巢狀 ≤ 4、參數 ≤ 7、行寬 ≤ 120；專案更嚴者從嚴（Lizard 圈複雜度 ≤ 8、函式 NLOC ≤ 50、檔案 ≤ 1000 行）。
3. 錯誤處理：禁止裸 `except:`；`except Exception` 必須註明為何可吞；邊界錯誤要往上送或記日誌。
4. 死碼：不留註解掉的程式、未使用匯入，或文件宣稱會呼叫但執行路徑沒有的安全控制，除非標成未接上。
5. 型別與 docstring：公開函式應有型別與單行摘要（D212）。
6. 安全：外部輸入進模型或工具前要驗證；禁止對不受信任資料 `eval` / `exec` / `pickle`；`yaml` 只用 `safe_load`；子程序只用參數陣列；金鑰只來自環境變數；路徑拒絕 `..` 與絕對路徑；外送 URL 限 https；不把金鑰寫進日誌或文件。
7. 測試：行為變更要有對應測試。本次只審原始碼，不跑測試。
8. 效能：runner 僅 `httpx`、`pydantic`、`PyYAML`；重型模型匯入保持延遲。
9. 跨專案：`architecture.md` §6 的 PyBreeze 契約（子命令、旗標、`PRTHINKER_*` 變數、`_build_parser` / `_build_config`）不得建議改名。
10. 文件同步：行為與 `architecture.md`、`CLAUDE.md`、README 不一致時要記下來。

嚴重度：缺陷＝未關閉且會造成錯誤送出、越權寫入或未授權使用；建議＝應修但預設路徑不會立刻損害；備註＝已核對、無須改碼。通過＝無未關閉缺陷；有條件通過＝無立即損害；需修正＝有未關閉缺陷。

## 審核紀錄

### 方法

讀 `architecture.md`、`CLAUDE.md` 的安全、網路與 §6 相關段落，以及 `progress.md` 前 80 行。只審 `prthinker/` 與 `codes/` 的 `.py`（排除 `tests/`、`__pycache__`）。搜尋 `eval(`、`exec(`、`shell=True`、`pickle`、`yaml.load`、`verify=False`、裸 `except:`、`subprocess`。每則發現都先讀過對應原始碼。未跑測試、未呼叫模型、未讀 `datas/` 論文資料。

### 發現

#### CR-01

- 嚴重度：缺陷
- 位置：`prthinker/cli.py` 第 98–111 行；`prthinker/cli_parser.py` 第 61–80 行與第 101–108 行；`prthinker/repo_config.py` 第 6–13 行與第 248–262 行；`prthinker/cli_parser_provider_groups.py` 第 16–45、128–167 行
- 說明：文件寫的優先順序是套件預設、YAML、環境變數、命令列，愈後愈高。實作卻先把環境變數烤進 `add_argument(default=...)`，再由 `_apply_repo_defaults` 的 `set_defaults` 整表覆蓋。命令列旗標仍較高，但只放在環境變數裡的 `PRTHINKER_BACKEND`、`PRTHINKER_REMOTE_URL`、`PRTHINKER_OPENAI_BASE_URL`、`PRTHINKER_ANTHROPIC_BASE_URL` 等會輸給工作目錄的 `.prthinker.yaml`。YAML 不收金鑰（`extra=forbid`），金鑰仍從環境變數進入 `Authorization`，因此一份被審查的 YAML 可以把 diff 與 bearer 送到自己寫的 `remote.url` 或供應商 `base_url`。`rag.rules_dir` 同樣可被 YAML 指到任意目錄，`load_rules_dir` 會把其下所有 `.md` 送進提示。另外 `main()` 的預解析把 `--config` 預設成 `None`，不讀 `PRTHINKER_CONFIG`；`find_config_file(None)` 於是載入 `./.prthinker.yaml`，環境變數指向的檔案不會被用到。
- 依據：安全（外部設定決定金鑰與程式內容的送達端）；文件同步（`repo_config.py` 與 `architecture.md` §6：PyBreeze 以環境變數傳設定）。不建議改旗標或變數名稱。
- 狀態：未關閉
- 建議：載入 YAML 之後，已設定的環境變數再蓋過 YAML，命令列仍最後。預解析的 `--config` 預設改為與正式剖析器相同的 `PRTHINKER_CONFIG`。補一個「環境變數勝過 YAML、YAML 勝過套件預設、命令列勝過環境變數」的測試。

#### CR-02

- 嚴重度：缺陷
- 位置：`prthinker/issue_fix.py` 第 83–91、166–179、316–331 行；`prthinker/auto_fix.py` 第 172–181 行；`prthinker/sandbox.py` 第 122–127、196–219 行；`prthinker/diff.py` 第 93–106、147–152 行；對照 `prthinker/hypothesis_retriever.py` 第 104–116 行
- 說明：模型或 diff 給的路徑直接拿去 `workdir / path` 或 `sandbox_root / path`。`Path` 遇到絕對路徑會丟掉左運算元；含 `..` 的相對路徑在 `read_text` / `write_text` 時會走出根目錄。`issue-fix --apply`、`--test-cmd` 與 `issue-autofix --open-pr` 會呼叫 `apply_to_workdir`。`original` 為空字串時 `_apply_edit` 直接把 `replacement` 接在既有檔案後面，語法檢查對非 `.py` 恆真，因此不必猜中原文就能改寫工作樹外的既有檔。`issue_autofix.fix_open_issues` 最後的 `git checkout --force` 只還原倉庫內檔案，修補不了逃出的寫入。`--auto-fix-threshold` 與 `--verify-suggestions` 使用 diff 解析出的路徑，`parse_unified_diff` 不拒絕 `..` 或絕對路徑；沙盒註解寫「不碰原倉庫」，但寫入發生在 `rmtree` 範圍之外。`hypothesis_retriever._safe_relpath` 已有正確拒絕邏輯，寫入路徑沒有複用。預設的 `review-pr` 不寫檔；損害發生在有開啟套用、自動修復或建議驗證時。
- 依據：`CLAUDE.md` 安全節要求工作目錄相對路徑，並拒絕 PR 內容中的 `..` 與絕對路徑。
- 狀態：未關閉
- 建議：所有來自 diff、模型 JSON 或議題文字的路徑先正規化，拒絕絕對路徑、磁碟機代號與 `..`，再確認 `resolve()` 仍在預定根目錄內。空 `original` 不得對未通過檢查的路徑寫入。

#### CR-03

- 嚴重度：缺陷
- 位置：`codes/run/fastapi_server.py` 第 185–250、607–770 行；`docker/docker-compose.server-qwen3-coder.yml` 第 70–71 行；`docker/docker-compose.monitoring.yml` 第 8–16、51–52、75–89、103–121 行；`docker/monitoring/nginx.conf` 第 99–115 行；對照 `docker/nginx.conf` 第 46–53 行與 `prthinker/backends/remote.py` 第 69–76 行
- 說明：`/ask`、`/review`、`/rag` 與工作查詢／取消都不檢查 `Authorization`。客戶端會送 bearer，伺服器忽略。預設 compose 把 9000 發佈到主機。監控 overlay 把自己寫成 host:9000 的公開面，卻沒有套用 TLS overlay 那份 bearer 檢查：`/ask` 與 `/review` 可直接把外部文字送進模型，`/metrics` 一併露出；Grafana 未覆寫環境變數時使用映像預設管理者帳密；cAdvisor 為 privileged，並掛上根檔案系統與 `/var/run`，同樣無認證。工作識別碼是隨機值，擋不住未持有識別碼的提交，只擋猜測別人的結果。
- 依據：安全（外部輸入進入模型與監控工具的邊界）；文件同步（TLS 註解寫 bearer，預設與監控路徑沒有）。
- 狀態：未關閉
- 建議：在應用程式內核對與客戶端相同的環境變數 token，不要只靠選用的 nginx。監控用的 nginx 沿用同一檢查，並要求 Grafana 密碼必填、不要把 privileged 的 cAdvisor 放上未認證的公開埠。隔離用的本機埠應綁在迴圈位址。

#### CR-04

- 嚴重度：建議
- 位置：`prthinker/cli_review.py` 第 690–701 行；`prthinker/cli_parser_groups.py` 第 847–853 行；`prthinker/mcp_server.py` 第 202–236 行；`prthinker/injection_guard.py`；`README.md` 目錄樹對 `injection_guard.py` 的說明
- 說明：`redact()` 只在 `--redact-secrets` 為真時跑，預設由 `PRTHINKER_REDACT_SECRETS` 決定且預設關閉。第三方後端因此會收到 diff 裡的權杖，與「送進第三方前先遮罩」的專案文字不符。MCP 預設會遮罩，但呼叫端可把參數設為否。`scan_diff` / `redact_injection` 沒有被管線、CLI 或伺服器呼叫；README 把它寫成會擋下載荷中的注入。研究延伸文件把它寫成函式庫，與 README 不一致。模組自身也聲明只是啟發式。
- 依據：文件同步；安全（外部 diff 進入模型）。
- 狀態：未關閉
- 建議：對非本機後端預設開啟遮罩，或在文件寫明必須自選。README 改為「未接入預設審查路徑的啟發式函式庫」，若要生效再加明確旗標。不要把啟發式寫成安全保證。

#### CR-05

- 嚴重度：建議
- 位置：`codes/util/faiss_util.py` 第 75–83 行；`codes/util/embedding_config.py` 第 24–27 行；`codes/util/hf_model_util.py` 第 288–298、337–351 行
- 說明：`EMB_MODEL` 決定嵌入模型，非 EmbeddingGemma 的路徑使用 `trust_remote_code=True`，會執行該儲存庫的程式。`from_pretrained` 與 `PeftModel.from_pretrained` 都沒有 `revision`。Qwen 映像以離線環境變數避開啟動時連線，但權重若當初依未釘選的預設分支寫入快取，供應鏈仍未釘死。訓練腳本另有多處 `trust_remote_code=True`，不在預設服務路徑上。
- 依據：`CLAUDE.md`「Hugging Face 下載必須釘選 revision」。
- 狀態：未關閉
- 建議：服務路徑的 `from_pretrained` 帶上明確 revision；嵌入模型改為允許清單，或只對已知需要遠端程式的識別碼開啟 `trust_remote_code`。

### 總評

未發現 `eval(`、`exec(`、`pickle`、不安全的 `yaml.load`、`verify=False`、裸 `except:` 或 `shell=True`。金鑰沒有寫死，YAML 使用 `safe_load`，子程序使用參數陣列。問題集中在三處邊界：環境變數被倉庫 YAML 蓋過後，金鑰會跟著改道的 URL 送出；模型或 diff 路徑在寫入時沒有關在根目錄裡；推論服務與標成公開面的監控代理沒有認證。後兩項不是預設 `review-pr` 只讀評論路徑，但開啟寫入或採用文件中的公開部署時會直接造成損害。

### 已核對

- `repo_config.load_repo_config` 使用 `yaml.safe_load` 後再以 Pydantic 驗證。
- 模型輸出與 JSONL 使用 `json.loads`；`InlineFinding` 在 `findings._validate_finding` 把 `path` 釘回審查中的檔案，但沒有檢查該檔案路徑本身。
- `prthinker/backends/agent_cli.py` 以參數陣列呼叫本機 CLI，提示經 stdin，不用 shell。
- `execution_sandbox.DockerExecutor` 預設要求映像含 `@sha256:`，且 `network=none`、`--cap-drop ALL`。`verify` 子命令預設拒絕未沙盒執行。
- `sandbox._run_verify_cmd` 以 `verify_cmd.split()` 組成參數陣列（`shell` 維持關閉）。這不是 shell 注入，但引號會被拆壞；命令來自操作者的旗標或環境變數，不在 YAML 綱要內。
- `execution_evidence.run_tool` 沒有正式呼叫端，只有測試使用。
- `prthinker/` 與 `codes/` 都沒有 `urlopen`。文件仍描述 `redaction._https_urlopen`，目前沒有對應程式。
- 插件經由 `importlib.metadata` 進入點載入，失敗的進入點會略過。這是安裝套件的程式碼，不是 diff 文字。

### 未涵蓋

未執行 pytest、ruff、bandit 或圈複雜度工具，因此沒有把超長函式逐一列為缺陷。未讀 `datas/`、`scores/` 的資料檔、`paper/` 二進位、`build/`、`dist/`、`docs/_build/`，也未審 `tests/`。`progress.md` 的未完成項（發版、映像升級、研究評估）不在本次熱點內。

### 本專案加嚴

圈複雜度 8 與函式 NLOC 50 嚴於本次通用上限，但本次不把既有長度單獨開缺陷。runner 不得在模組頂層匯入 `codes`。修正 CR-01 時保留 §6 的子命令、旗標與 `PRTHINKER_*` 名稱，只改優先順序。

### 結論

需修正。未關閉缺陷 3 則（CR-01、CR-02、CR-03），建議 2 則（CR-04、CR-05）。沒有其他未關閉缺陷。
