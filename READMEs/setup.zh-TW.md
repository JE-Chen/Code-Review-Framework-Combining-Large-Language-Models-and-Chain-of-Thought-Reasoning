# 設置

[English](setup.md) · **繁體中文** · [简体中文](setup.zh-CN.md)

這是完整的設置指引。簡短介紹請見 [`README.zh-TW.md`](README.zh-TW.md)。
功能總覽請見 [`features.zh-TW.md`](features.zh-TW.md)。

---

## 目錄

- [前置需求](#前置需求)
- [安裝 profile](#安裝-profile)
- [情境 1 — 只用 GitHub Actions（無 GPU）](#情境-1--只用-github-actions無-gpu)
- [情境 2 — 個人開發 + 付費 API key](#情境-2--個人開發--付費-api-key)
- [情境 3 — 個人開發 + 本機 Ollama](#情境-3--個人開發--本機-ollama)
- [情境 4 — Claude Desktop / Cursor / Cline（MCP）](#情境-4--claude-desktop--cursor--clinemcp)
- [情境 5 — 團隊自架（GPU server + GHA runner）](#情境-5--團隊自架gpu-server--gha-runner)
- [情境 6 — 研究環境（LoRA 訓練 + 本機推論）](#情境-6--研究環境lora-訓練--本機推論)
- [`.prthinker.yaml` repo 組態](#prthinkeryaml-repo-組態)
- [GitHub repo secrets](#github-repo-secrets)
- [GitHub Actions workflow](#github-actions-workflow)
- [Branch protection](#branch-protection)
- [Bootstrap 學習語料](#bootstrap-學習語料)
- [Cache 與 telemetry 首次執行](#cache-與-telemetry-首次執行)
- [選用之研究級 flag](#選用之研究級-flag)
- [驗證安裝](#驗證安裝)
- [疑難排解](#疑難排解)

---

## 前置需求

- **Python 3.12 以上。** 套件用了 PEP 604 union 語法（\ `str | None`\ ）
  與其他 3.12 才有的模式。
- **`git`** 在 `$PATH` 內（CLI 的 local-diff 流程會用到）。
- **GPU**\ 只有想跑本機 Hugging Face backend 或 inference server 時才需要。
  `runner` / `openai` / `anthropic` profile 純 CPU 即可。
- **GitHub repo + admin 權限**\ 才能啟用 workflow + Check Run gate。

---

## 安裝 profile

```bash
git clone <repo-url>
cd Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning

# 挑一個（或疊著用）：
pip install -e ".[runner]"   # 薄客戶端 — 只裝 httpx + pydantic（~5 MB）
pip install -e ".[local]"    # 多加 torch、transformers、faiss、peft、bitsandbytes
pip install -e ".[server]"   # 在 `local` 之上多加 fastapi + uvicorn
pip install -e ".[mcp]"      # 多加 `mcp` SDK 給 IDE 整合用
pip install -e ".[dev]"      # 多加 pytest 給跑測試用
```

CLI 入口是 `prthinker`。裝完驗證：

```bash
prthinker --help
```

---

## 情境 1 — 只用 GitHub Actions（無 GPU）

最便宜的路徑：GHA-hosted runner + 付費 API 做推論，全部靠 repo secrets +
`.prthinker.yaml`。

1. **在 repo 根目錄加 `.prthinker.yaml`\ ：**

   ```yaml
   backend: anthropic
   per_file: true
   inline_review: true
   gate:
     severity: error
   ci_signals:
     enabled: true
   anthropic:
     model: claude-sonnet-4-6
   ```

2. **設 repo secret**\ （Settings → Secrets and variables → Actions）：

   | Secret | 值 |
   |---|---|
   | `ANTHROPIC_API_KEY` | `sk-ant-...` |

3. **複製 workflow 檔** `.github/workflows/prthinker.yml`\ ──本 repo 內附
   的版本已經宣告必要 permissions（\ `contents: read`\ 、
   `pull-requests: write`\ 、\ `checks: write`\ 、\ `actions: read`\ ）。

4. **推 PR**\ ──workflow 自動跑──summary 留言 + 帶 suggestion block 的
   inline review 就上來了。

完成。不需要架伺服器。成本 = 每個 PR 的 Anthropic API token。

---

## 情境 2 — 個人開發 + 付費 API key

想在本機 review 自己改的東西，不走 GHA。

```bash
pip install -e ".[runner]"

export OPENAI_API_KEY="sk-..."

git diff main..HEAD > my-change.diff

prthinker review-file my-change.diff \
    --backend openai \
    --openai-model gpt-4o-mini \
    --per-file --inline-review \
    --redact-secrets
```

或對 staged 變更：

```bash
git diff --cached | prthinker review-file - \
    --backend openai --openai-model gpt-4o-mini \
    --per-file --inline-review --redact-secrets
```

Markdown 結果寫到 stdout，不會貼到任何地方。

---

## 情境 3 — 個人開發 + 本機 Ollama

不想按 token 付費的話，把 prthinker 指到本機的 Ollama（透過它的
OpenAI-compatible endpoint）。

```bash
# 1. 安裝並啟動 Ollama（https://ollama.com）
ollama pull qwen2.5-coder:7b
ollama serve   # 監聽 :11434

# 2. 用 prthinker review
pip install -e ".[runner]"

prthinker review-file my-change.diff \
    --backend openai \
    --openai-base-url http://localhost:11434/v1 \
    --openai-model qwen2.5-coder:7b \
    --openai-api-key ollama \
    --per-file --inline-review
```

（\ `--openai-api-key` 隨便填個非空字串都行──Ollama 不檢查。）

同樣的方式可用在 vLLM、LM Studio、llama.cpp server、Together、Groq、
DeepInfra、OpenRouter──它們都講同一種協定。

---

## 情境 4 — Claude Desktop / Cursor / Cline（MCP）

在 IDE 內直接跑 review，完全不走 GHA。

```bash
pip install -e ".[mcp]"
```

在 client 的 config 加 MCP server 項目。Claude Desktop on macOS 是
`~/Library/Application Support/Claude/claude_desktop_config.json`\ ：

```json
{
  "mcpServers": {
    "prthinker": {
      "command": "prthinker",
      "args": ["mcp"],
      "env": {
        "PRTHINKER_BACKEND": "anthropic",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "PRTHINKER_ANTHROPIC_MODEL": "claude-sonnet-4-6",
        "PRTHINKER_CACHE_ENABLED": "true",
        "PRTHINKER_TELEMETRY_ENABLED": "true"
      }
    }
  }
}
```

重啟 Claude Desktop。在 chat：

> Run prthinker on `$(git diff --cached)`

LLM 呼叫 `review_diff` MCP tool、secret 在送 API 前被 redact 掉、
markdown review 串流回 chat。

Cursor / Continue / Cline / Zed 都用同樣 schema──請查各家 MCP 文件確認
config 檔位置。

---

## 情境 5 — 團隊自架（GPU server + GHA runner）

適用於：

- 想用自家 fine-tune 的 LoRA（或不想永遠按 token 付費）。
- 有 GitHub Actions 可連的 GPU 機器。
- 想要每個 PR 都有 CI 訊號注入、gate、inline review。

**GPU 機器上：**

```bash
pip install -e ".[server]"

export PRTHINKER_DISMISSED_PATH=./store/dismissed.jsonl
export PRTHINKER_ACCEPTED_PATH=./store/accepted.jsonl
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 9000
```

確認：

```bash
curl http://my-host:9000/healthz   # → {"status": "ok", "model": "..."}
```

**或用 Docker compose**（`docker/` bundle，免手動建 venv）。提供兩個伺服器
映像:可攜的 Qwen3-Coder-30B 部署(`docker-compose.server-qwen3-coder.yml`,
如下)與本機 DGX Spark 上目前的 Gemma-4-31B-it 部署
(`docker-compose.server-gemma4.yml`)：

```bash
cd docker
cp .env.example .env            # PRTHINKER_HOST_PORT 預設 9000
docker compose -f docker-compose.server-qwen3-coder.yml up -d   # base：prthinker FastAPI on :9000
curl http://my-host:9000/healthz

# 可選 TLS overlay — nginx TLS + bearer-token 驗證 on :443：
#   .env 內 PRTHINKER_BACKEND_TOKEN=$(openssl rand -hex 32)
docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.tls.yml up -d
curl https://my-host/healthz -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"

# 可選 monitoring overlay — Prometheus + Grafana + DCGM + cAdvisor，
# 全部依路徑收在 host :9000 之下：
docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.monitoring.yml up -d
#   http://my-host:9000/grafana/     Grafana   （預設 admin / admin）
#   http://my-host:9000/prometheus/  Prometheus UI
#   http://my-host:9000/cadvisor/    cAdvisor
#   http://my-host:9000/kg/          repo knowledge-graph 頁
```

完整部署參考（檔案、volume、路由 URL 表）：
`docs/zh-TW/concepts/docker-platforms-report.rst`。

**Repo 內：**

`.prthinker.yaml`\ ：

```yaml
backend: remote
remote:
  url: http://my-host:9000
  use_pipeline_endpoint: true
per_file: true
inline_review: true
gate:
  severity: error
ci_signals:
  enabled: true
rag:
  enabled: true
  remote: true            # runner 打 /rag，不在本機載 FAISS
```

Repo secret：

| Secret | 值 |
|---|---|
| `PRTHINKER_BACKEND_URL` | `http://my-host:9000` |
| `PRTHINKER_BACKEND_API_KEY` | （可選）reverse proxy 的 bearer token |

推 PR。Runner 保持薄（只有 httpx + pydantic）；GPU、FAISS index、
dismissed/accepted store 都在 server。

---

## 情境 6 — 研究環境（LoRA 訓練 + 本機推論）

正在迭代 paper。\ `codes/train/` 的腳本負責 fine-tune LoRA；framework
對 held-out diff set 跑每個迭代結果，方便對比。

```bash
pip install -e ".[local,dev]"

# 1. 訓 LoRA（超參數見 codes/train/*.py）
python -m codes.train.qwen3-coder-30b

# 2. 對標準測試語料批次跑 review
python -m codes.run.cot     # 在 cwd 為每個檔產一個資料夾

# 3. 查 telemetry 對比各次跑的成本/延遲
prthinker stats --since-days 7
```

`codes/run/CoT_Prompts/` 是 prompt templates；prthinker 重用它們作為
single source of truth。改 prompt → content hash 變 → cache 自動失效。

---

## `.prthinker.yaml` repo 組態

完整 schema 放在 repo 根目錄。每個 key 都可省略，預設值都合理。

```yaml
backend: openai                # local | remote | openai | anthropic
max_new_tokens: 32768

per_file: true
inline_review: true
max_findings_per_file: 10

rag:
  enabled: true
  threshold: 0.7
  rules_dir: ./team-rules
  remote: false

gate:
  severity: error              # none | warning | error
                               # 注意：不要寫 `on:`──YAML 1.1 會把
                               # 未加引號的 on 解析成 boolean True。

ci_signals:
  enabled: true
  max_jobs: 5
  tail_chars: 4000

cache:
  enabled: true
  path: .prthinker/cache.sqlite
  ttl_days: 7

telemetry:
  enabled: true
  path: .prthinker/telemetry.sqlite

stores:
  dismissed: .prthinker/dismissed.jsonl
  accepted:  .prthinker/accepted.jsonl

local:
  model: Qwen/Qwen3-Coder-30B-A3B-Instruct
  lora_path: ../train/outputs-lora-qwen3-coder-30b

openai:
  model: gpt-4o-mini
  base_url: https://api.openai.com/v1

anthropic:
  model: claude-opus-4-7
  base_url: https://api.anthropic.com
  version: "2023-06-01"

remote:
  url: http://my-host:9000
  timeout_seconds: 600
  use_pipeline_endpoint: true
```

**密鑰絕對不放 YAML。** API key / GitHub token 一律只從環境變數讀。

### 優先序

`CLI flag` ≻ `env var` ≻ `.prthinker.yaml` ≻ `套件預設`

所以 workflow 內的 flag 蓋過 YAML、YAML 又蓋過套件預設。

---

## GitHub repo secrets

依 backend：

| Backend | 必需 secret |
|---|---|
| `remote` | `PRTHINKER_BACKEND_URL`\ 、可選 `PRTHINKER_BACKEND_API_KEY` |
| `openai` | `OPENAI_API_KEY`\ （或 `PRTHINKER_OPENAI_API_KEY`\ ） |
| `anthropic` | `ANTHROPIC_API_KEY`\ （或 `PRTHINKER_ANTHROPIC_API_KEY`\ ） |
| `local` | 無──但需要 self-hosted GPU runner |

`GITHUB_TOKEN` 是 GitHub Actions 自動提供的，不用設。

---

## GitHub Actions workflow

內附的 `.github/workflows/prthinker.yml` 已涵蓋一般情況。客製化請改
`env:` block──每個 CLI flag 都有對應的 `PRTHINKER_*` env var。完整清單
見 [`features.zh-TW.md`](features.zh-TW.md)。

**三 job 架構：** `enumerate` → `review` matrix（\ `max-parallel: 1`\ ，
每 shard 60 分鐘）→ `aggregate`。每個 PR file 各自有一個 runner 與
獨立 timeout budget，所以一個慢檔案不會把整段 review 拖垮。Matrix
runner 把 partial `ReviewResult` JSON 寫成 artifact；aggregate 把
所有 partial 合一後 post **一個** summary comment + **一個** inline
review + 開 + 關 gate 各一次。Skip / fallback 行為、env vars、fan-in
合約細節見
[GitHub Actions guide](../docs/zh-TW/guide/github-actions.rst)。

**必要 permissions：**

```yaml
permissions:
  contents: read         # checkout
  pull-requests: write   # 貼 summary + inline review
  checks: write          # 開啟與結算 gate
  actions: read          # 抓 CI 失敗 log
```

**Trigger：** 預設 `pull_request` opened / synchronize / reopened。想等 CI
跑完才 review 的話：

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
```

**過濾 noise paths。** workflow 頂層 `env:` block 定義
`PRTHINKER_EXCLUDE_GLOBS`\ （comma-separated fnmatch patterns）。
`enumerate` job 與 CLI 的 per-file loop 都讀同一份，避免 generated
data、IDE state、大段 markdown 變更白白吃 GPU 時間。可依專案調整。

**Backend timeout 防護。** Matrix runner 用
`POST /review/submit` + `GET /review/result/{id}`\ （5 秒 poll）
跟 backend 通訊──每個 HTTP call 都遠低於 1 秒，反正
Cloudflare 免費 / Pro / Business 方案 100 秒 idle timeout 不會
觸發。Aggregate 之 PR-wide overall summary 合成也走同樣的 job
pattern（\ `POST /ask/submit`\ ），即使單一 prompt 跑很久也安全。

**取消與閒置 GPU 防護。** Workflow 被取消時（新 push 觸發
`concurrency: cancel-in-progress`\ 、手動 *Cancel workflow*\ 、
runner crash），matrix runner 的 try/finally 會 post
`POST /review/cancel/{job_id}` 通知 server 於下一個 token
邊界中斷。Backend 自己的 idle sweeper 是 fallback：任何 running
job 若 result endpoint 超過 180 秒沒被 poll，就自動 set
cancel event，涵蓋 SIGKILL / 網路中斷等 try/finally 來不及執行
之情境，確保 GPU 不被白燒。

**Comment / review / check dedup。** 對同 SHA 重複 run workflow
原本會在 PR 上累積多份 prthinker 產物。現在每次 post 前都會清
理舊產物：

| 產物 | 機制 |
|---|---|
| Summary comment | 以 HTML marker（\ `<!-- prthinker:summary -->`\ ）upsert；同一條 comment 永遠被 PATCH 在原位。 |
| Inline review | body 嵌入隱藏 `<!-- prthinker:inline -->` marker；post 前 runner 把所有 marker-tagged review 之 child comment 全部 DELETE。空 wrapper 留為 timeline stub（GitHub 不允許 dismiss COMMENT-state review）。 |
| Check run | open gate 前對同 SHA 上所有 `prthinker` check 都 PATCH 成 `status=completed` / `conclusion=neutral` 加 *superseded* 標題；UI 會把它們折疊在 live check 下方。 |

---

## Branch protection

讓 prthinker 真的能擋 error 嚴重度的 finding：

1. 跑至少一次 `PRTHINKER_GATE_ON=error` 的 PR，讓 `prthinker` 這個
   Check Run 出現在 PR 的 Checks 標籤頁。
2. **Settings → Branches → branch protection rule**\ ，選預設 branch。
3. 啟用 **Require status checks to pass before merging**\ ，把
   `prthinker` 加進清單。

之後，PR 只要有 error 嚴重度的 finding 就無法合併，直到作者處理（或
maintainer 強制覆寫）。

---

## Bootstrap 學習語料

兩份 append-only JSONL 紀錄 PR 作者對過去 review 的反應：

```bash
# 作者按 👎 或回「false positive」的留言
prthinker harvest-dismissed \
    --repo owner/name \
    --max-prs 100 \
    --out .prthinker/dismissed.jsonl

# 含「Apply suggestion」commit 的 PR
prthinker harvest-accepted \
    --repo owner/name \
    --max-prs 100 \
    --out .prthinker/accepted.jsonl
```

伺服器端指過去：

```bash
export PRTHINKER_DISMISSED_PATH=.prthinker/dismissed.jsonl
export PRTHINKER_ACCEPTED_PATH=.prthinker/accepted.jsonl
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 9000
```

兩份 store 為空時都是 no-op──server log 會印 `filter disabled` /
`exemplars disabled`\ ，行為與沒裝一樣。

---

## Cache 與 telemetry 首次執行

```bash
prthinker review-file my-change.diff \
    --backend anthropic --anthropic-api-key "$ANTHROPIC_API_KEY" \
    --cache --telemetry
```

兩份 SQLite 會生在 `.prthinker/` 下。請加進 `.gitignore`\ ──它們是
runtime state、不是 config：

```gitignore
.prthinker/cache.sqlite
.prthinker/cache.sqlite-*
.prthinker/telemetry.sqlite
.prthinker/telemetry.sqlite-*
```

（\ `dismissed.jsonl` / `accepted.jsonl` 反過來：是學到的判斷，**應該**
commit。）

跑幾次後檢視：

```bash
prthinker stats --since-days 7
```

---

## 選用之研究級 flag

四個超越多數 LLM code-review 系統「一次性審查」之擴充。所有 flag 皆為
**opt-in**\ ，需搭配 `--inline-review`；本框架交付程式碼，依不謊造原則
**不**\ 隨附量測過之 benchmark 數字。設計細節見
[`docs/zh-TW/concepts/research-extensions.rst`](../docs/zh-TW/concepts/research-extensions.rst)\ 。

| Flag                       | 環境變數                              | 預設 | 額外成本                       |
| -------------------------- | ------------------------------------ | ---- | ------------------------------ |
| `--reply-to-author`        | `PRTHINKER_REPLY_TO_AUTHOR`         | 關閉 | 一次平台 API 呼叫              |
| `--counterfactual`         | `PRTHINKER_COUNTERFACTUAL`          | 關閉 | 每檔多一次 backend             |
| `--provenance`             | `PRTHINKER_PROVENANCE`              | 關閉 | prompt + 輸出變大              |
| `--judge`                  | `PRTHINKER_JUDGE`                   | 關閉 | 每檔多一次 backend             |
| `--self-correct`           | `PRTHINKER_SELF_CORRECT`            | 關閉 | 每檔多一次 backend             |
| `--diff-since-last`        | `PRTHINKER_DIFF_SINCE_LAST`         | 關閉 | 迭代 PR 之上省 token           |
| `--verify-suggestions`     | `PRTHINKER_VERIFY_SUGGESTIONS`      | 關閉 | 每建議多 1× sandbox + verify_cmd |
| `--api-consistency`        | `PRTHINKER_API_CONSISTENCY`         | 關閉 | 跨語言 PR 上多 1× backend      |
| `--pr-classify`            | `PRTHINKER_PR_CLASSIFY`             | 關閉 | 每 PR 多 1× backend            |
| `--reproducibility-check`  | `PRTHINKER_REPRODUCIBILITY_CHECK`   | 關閉 | 每檔多 1× backend              |
| `--dep-upgrade-check`      | `PRTHINKER_DEP_UPGRADE_CHECK`       | 關閉 | 每升級套件多 1× backend        |
| `--personas`               | `PRTHINKER_PERSONAS`                | 空   | 每 PR 多 N× backend + 1 conflict step |
| `--risk-weighted`          | `PRTHINKER_RISK_WEIGHTED`           | 關閉 | 少量 `git log` 呼叫            |
| `--diff-entropy`           | `PRTHINKER_DIFF_ENTROPY`            | 關閉 | 純 CPU，無 backend 呼叫        |

### 閉環多輪對話──`--reply-to-author`

**做什麼。** 在產生下一輪審查之前\ ，透過
`PlatformAdapter.fetch_author_replies()` 取回 PR 作者對上次 prthinker
摘要評論之回覆\ ，渲染成\ *Prior dialogue*\ 區塊\ ，注入 inline-findings
prompt\ 。模型被要求對作者已回覆過的評論\ 「\ 捨棄\ 」、「\ 精煉\ 」或
「\ 反駁\ 」\ ，但絕不靜默重貼\ 。

**何時開啟。** 長壽 PR、多輪審查；團隊抱怨\ 「\ bot 在我回了 wontfix
之後還是一直重貼相同評論\ 」\ 。

**怎麼開啟。**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --reply-to-author
```

或於 `.prthinker.yaml`：

```yaml
reply_to_author: true
```

**會看到什麼。** 在以前已被作者回覆過之行上的 finding\ ，下一輪應該
消失、精煉、或附上新理由\ 。

### 反事實審查──`--counterfactual`

**做什麼。** 在 `--inline-review` 產生 findings 之後\ ，對其中
屬於\ *設計選擇*（非 bug、非 nit）之 finding\ ，列出最多三個競爭性
實作方案與小型 trade-off 矩陣（軸如 `performance`、`readability`、
`testability`）\ 。

**何時開啟。** 設計面比重高之 PR（新模組、API 變更、refactor）\ 。
熱修補丁不適合 —— 該步驟沒得發揮\ ，只會白燒一次 backend 呼叫\ 。

**怎麼開啟。**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --counterfactual
```

或於 `.prthinker.yaml`：

```yaml
counterfactual: true
```

**會看到什麼。** 每檔摺疊區塊多出一段\ *Alternative implementations*\ ，
列出選項與其 trade-off\ 。Parser 會丟棄選項少於 2、或 `finding_index`
越界之區塊 ——\ 壞步驟絕不汙染留言\ 。

### 評論來源 / 引用稽核──`--provenance`

**做什麼。** 要求模型為每條 finding 附上 `provenance` payload\ ，引用
RAG 規則 / accepted-example / diff 行號\ ，並可選自評信心值
∈ `[0, 1]`\ 。PR 留言每檔多一段\ *Audit trail*\ 引用清單\ 。

**何時開啟。** 團隊需要追問\ 「\ 為什麼會提出這條評論\ 」\ ；或
訓練 verifier 需要可追溯之標籤\ 。會放大 prompt + 輸出大小\ ，記得把
`--max-new-tokens` 調寬鬆\ 。

**怎麼開啟。**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --provenance
```

或於 `.prthinker.yaml`：

```yaml
provenance: true
```

**安全屬性**（已內建於 parser）：

- 壞掉的 `provenance` 區塊絕不拖垮原評論\ ；解析失敗則剝除\ 並保留
  finding\ 。
- 越界之 `rag_rule` / `accepted_example` 索引會被靜默丟棄 ——
  模型無法虛構引用\ 。
- `confidence` 只供人類參考\ ，**絕不**\ 被用來靜默過濾 finding\ 。

### 對抗強健性──`prthinker adversarial-eval`

**做什麼。** 將 prompt-injection 語料送入目前 backend\ ，把每筆呼叫
之結果（bypass / detected / 命中 markers / 原始輸出）寫入 SQLite\ 。
**不輸出**\ 任何聚合偵測率 —— 聚合計算交給下游 SQL\ ，原始輸出保留
以利稽核\ 。

**何時使用。** 採用新 backend、修改 system prompt、或 paper-grade
多 provider 強健性比較之前\ 。**請勿**\ 把隨附之 `seed.jsonl` 視為
benchmark —— 它是涵蓋四種攻擊類型（`direct_injection`、
`encoded_payload`、`split_injection`、`role_hijack`）之手工種子\ 。
要發表數字之前\ ，請先擴充它\ 。

**怎麼跑。**

```bash
prthinker adversarial-eval \
    --corpus prthinker/adversarial_corpus/seed.jsonl \
    --outcomes-path .prthinker/adversarial.sqlite \
    --backend openai --openai-model gpt-4o-mini
```

**檢視結果。** 用 SQL 就好：

```bash
sqlite3 .prthinker/adversarial.sqlite \
  "SELECT category, COUNT(*), SUM(bypassed), SUM(detected)
     FROM outcomes
    GROUP BY category;"
```

### Force-push 差分審查──`--diff-since-last`

**做什麼。** 把每檔新側內容 hash（`FileDiff.content_sha256`），
findings 存進小型 SQLite cache，key 為
`(pr_number, repo, file_path, hunk_sha256)`。下次 push 時未動的檔
直接 reuse 上次 findings；只有真正改動的檔才重新進模型。

```bash
prthinker review-pr --pr 42 --per-file --inline-review \
    --diff-since-last --diff-cache-path .prthinker/diff-cache.sqlite
```

跨 PR 以 primary key 隔離。關 PR 時用 `ReviewCache.evict_pr()` 清掉。

### 建議 sandbox 驗證──`--verify-suggestions`

**做什麼。** 對每條帶 `suggestion` 之 finding，把 working tree 複製到
`tempfile.mkdtemp` 套用 suggestion（用 `original` 守備檢查），跑
`--verify-cmd`（預設 `pytest -x`）於 `--verify-timeout`（預設 60s）下，
把每條 finding 標 `[verified]` / `[FAILED]` / `[skipped]` / `[error]`。

```bash
prthinker review-pr --pr 42 --inline-review --verify-suggestions \
    --verify-cmd "pytest -x tests/" --verify-timeout 60
```

原 repo 絕不動；verify 指令以 argv list 跑（無 `shell=True`）。

### 跨語言 API 一致性──`--api-consistency`

**做什麼。** 當 PR 同時碰到後端 `.py` 與前端 `.ts` / `.tsx` / `.js` /
`.jsx`，新增一個 step 問模型\ 「\ 跨檔 drift\ 」── 重命名欄位、移除路由、
類型變更。單語言 PR 上靜默 pass，不浪費 backend 呼叫。

```bash
prthinker review-pr --pr 42 --inline-review --api-consistency
```

### PR 類型自適應──`--pr-classify`

**做什麼。** 從 diff + PR 標題 + body 把 PR 分為 bugfix / feature /
refactor / docs / chore / unknown，後續 review 深度隨之調整：docs PR 跳
inline findings；bugfix PR 用 focused prompt 與較小 budget；refactor PR
放大 budget 並注入行為等價 hint。

```bash
prthinker review-pr --pr 42 --inline-review --pr-classify
```

### 評論一致性訊號──`--reproducibility-check`

**做什麼。** 同 prompt 跑兩次 inline-findings（非 0 temperature 自然產生
第二個樣本），按 (path, line, 正規化 comment) 比對，標
`[stable]` / `[low-reproducibility]`。第二次新出現之 finding 也保留。
每檔多 1× backend 呼叫。

```bash
prthinker review-pr --pr 42 --inline-review --reproducibility-check
```

### 依賴升級影響──`--dep-upgrade-check`

**做什麼。** 偵測 lock-file 觸碰（`requirements.txt` / `pyproject.toml` /
`package.json`），抽出 `(package, old, new)` delta，把該套件在 diff 其他
檔案中的實際呼叫點放進 prompt，問模型 breaking change 是否影響本 repo。

```bash
prthinker review-pr --pr 42 --dep-upgrade-check
```

PR 留言頂端多出\ 「\ Dependency upgrade impact\ 」\ 表格。框架\ 不\ 在
review-time 抓 remote changelog。

### 多角色 + 衝突顯化──`--personas`

**做什麼。** 跑 N 個正交 lens（`security` / `performance` /
`readability` / `api_stability` / `maintainability`），每個 lens 之
prompt 明確要求只在該 lens 範圍內評論。最後一個 conflict-finder step
找出角色間之分歧。PR 留言頂端多出\ 「\ Persona conflicts\ 」\ 表格（刻意
不替你選邊）。

```bash
# 子集：
prthinker review-pr --pr 42 --personas security,performance,readability
# 全 5 個：
prthinker review-pr --pr 42 --personas all
```

成本：每個角色一次 backend 呼叫 + conflict step 一次。

### 風險加權注意力──`--risk-weighted`

**做什麼。** 以 churn（`git log` 於 lookback window，預設 90 天）+
complexity proxy（HEAD 行數）+ bug history（commit message 命中
`fix:` / `bug` / `revert`）算每檔風險分。每檔
`max_findings_per_file` 隨之線性縮放於 `floor`（預設 2）到
`ceiling`（預設 `2 × base_budget`）。

```bash
prthinker review-pr --pr 42 --inline-review --risk-weighted \
    --risk-workdir /path/to/repo
```

GHA 注意：`actions/checkout` 預設 shallow clone（`fetch-depth: 1`）；
請在 workflow 設 `fetch-depth: 0`，lookback window 才有 commit 可數。
預設權重（0.4 / 0.3 / 0.3）是\ 框架慣例\ ，非校準公式。

### Diff 熵──`--diff-entropy`

**做什麼。** 純 data 算 PR size + 目錄分布 Shannon entropy，分為
`focused` / `wide` / `bomb`。verdict 為 `bomb` 時於留言頂端貼
\ 「\ Consider splitting this PR\ 」\ 警示。框架\ 不\ 因高分阻擋，目的是
把 PR 形狀顯化。

```bash
prthinker review-pr --pr 42 --diff-entropy
```

無 backend 呼叫，純本機 CPU。

### 全部疊起來跑

研究級單 PR 跑法：

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review \
    --reply-to-author --counterfactual --provenance \
    --diff-since-last --verify-suggestions --api-consistency \
    --pr-classify --reproducibility-check --dep-upgrade-check \
    --personas all --risk-weighted --diff-entropy \
    --judge --self-correct \
    --rules-dir ./team-rules \
    --max-new-tokens 65536
```

預期約為素 review 的 4–6× token 預算\ 。搭配
`--cache --cache-path .prthinker/cache.sqlite` 可在同 PR 多次迭代
時攤平成本\ 。

---

## 驗證安裝

跑測試套件：

```bash
pip install -e ".[dev]"
py -m pytest tests/ -q
```

本機建文件（三種語言）：

```bash
pip install -r docs/requirements.txt
py -m sphinx -b html docs docs/_build/html
```

只會跑一次 build；輸出單一 HTML 樹\ ，三語在側邊欄各自為一個大章節
（English / 繁體中文 / 简体中文）\ 。應 zero error / zero warning\ 。

---

## 疑難排解

### Windows 上 `bitsandbytes` import 失敗

bitsandbytes 官方只出 Linux wheel；Windows 請用上游
`bitsandbytes-windows-webui` wheel，或直接在 WSL2 內跑 prthinker。或者
完全跳過量化（local config 內 `quantization: false`\ ）──VRAM 用量會
飆，但不需要 bitsandbytes。

### 載 Qwen3-Coder-30B 時 GPU OOM

30B 模型在 4-bit NF4 量化下大約要 18 GB VRAM。較小的 LoRA 目標可在 12 GB
卡上：

```yaml
local:
  model: Qwen/Qwen2.5-Coder-7B-Instruct
  lora_path: ../train/outputs-lora-qwen2.5-coder-7b
```

### 「PRTHINKER_BACKEND_URL secret is not configured」

Workflow 啟動檢查失敗，因為 secret 沒設。Settings → Secrets and variables
→ Actions 補上。

### RAG 跑太慢 / runner OOM 載 embedding 模型

Qwen3-Embedding-4B 約 8 GB VRAM。預設 GitHub-hosted runner 載不動。
依優先序：

1. `.prthinker.yaml` 內設 `rag.remote: true`\ ──runner 改打 server 的
   `/rag` endpoint，不在本機載 FAISS。
2. `rag.enabled: false`\ ──整個關掉 RAG。會失去全域規則，但能在最小硬體
   上跑。

### Cache 檔越長越大

預設 TTL 7 天。可調 `cache.ttl_days: 1`\ （更積極）或 `cache.ttl_days: null`
（永不過期）。手動 prune：

```bash
sqlite3 .prthinker/cache.sqlite "DELETE FROM prompt_cache WHERE created_at < strftime('%s','now','-7 days');"
```

### `prthinker mcp` 喊「The `mcp` package is not installed」

裝了 runner profile 但沒裝 MCP extras：

```bash
pip install -e ".[runner,mcp]"
```

### Inline review 回 HTTP 422

GitHub 拒絕在不在 diff 內的行貼 inline comment。Findings sanitizer 應該
在 client 側就丟掉，但客製化 prompt 可能產出超範圍的條目。檢查 runner
log 裡的 `Dropping finding on …` 訊息──每筆丟棄都有 log。

### Sphinx build 抱怨 CJK punctuation

如果在改中文 docs 看到 `Inline literal start-string without end-string`\ ，
通常是 CJK 括號或 em-dash 直接黏在 \`\`code\`\` 或 \*\*bold\*\* 旁邊。
中間補一個 `\ `\ （backslash + space）的 zero-width separator：

```rst
``foo``\ ──不要這樣
```