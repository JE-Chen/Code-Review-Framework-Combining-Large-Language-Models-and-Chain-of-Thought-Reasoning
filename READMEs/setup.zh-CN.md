# 设置

[English](setup.md) · [繁體中文](setup.zh-TW.md) · **简体中文**

这是完整的设置指南。简短介绍请见 [`README.zh-CN.md`](README.zh-CN.md)。
功能总览请见 [`features.zh-CN.md`](features.zh-CN.md)。

---

## 目录

- [前置需求](#前置需求)
- [安装 profile](#安装-profile)
- [场景 1 — 只用 GitHub Actions（无 GPU）](#场景-1--只用-github-actions无-gpu)
- [场景 2 — 个人开发 + 付费 API key](#场景-2--个人开发--付费-api-key)
- [场景 3 — 个人开发 + 本地 Ollama](#场景-3--个人开发--本地-ollama)
- [场景 4 — Claude Desktop / Cursor / Cline（MCP）](#场景-4--claude-desktop--cursor--clinemcp)
- [场景 5 — 团队自部署（GPU server + GHA runner）](#场景-5--团队自部署gpu-server--gha-runner)
- [场景 6 — 研究环境（LoRA 训练 + 本地推理）](#场景-6--研究环境lora-训练--本地推理)
- [`.prthinker.yaml` repo 配置](#prthinkeryaml-repo-配置)
- [GitHub repo secrets](#github-repo-secrets)
- [GitHub Actions workflow](#github-actions-workflow)
- [Branch protection](#branch-protection)
- [Bootstrap 学习语料](#bootstrap-学习语料)
- [Cache 与 telemetry 首次运行](#cache-与-telemetry-首次运行)
- [可选的研究级 flag](#可选的研究级-flag)
- [验证安装](#验证安装)
- [疑难排查](#疑难排查)

---

## 前置需求

- **Python 3.12 或更新。** 包内用了 PEP 604 union 语法（\ `str | None`\ ）
  与其他 3.12 才有的模式。
- **`git`** 在 `$PATH` 内（CLI 的 local-diff 流程会用到）。
- **GPU**\ 只有想跑本地 Hugging Face backend 或 inference server 时才需要。
  `runner` / `openai` / `anthropic` profile 纯 CPU 即可。
- **GitHub repo + admin 权限**\ 才能启用 workflow + Check Run gate。

---

## 安装 profile

```bash
git clone <repo-url>
cd Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning

# 挑一个（或叠着用）：
pip install -e ".[runner]"   # 薄客户端 — 只装 httpx + pydantic（~5 MB）
pip install -e ".[local]"    # 多加 torch、transformers、faiss、peft、bitsandbytes
pip install -e ".[server]"   # 在 `local` 之上多加 fastapi + uvicorn
pip install -e ".[mcp]"      # 多加 `mcp` SDK 给 IDE 集成用
pip install -e ".[dev]"      # 多加 pytest 给跑测试用
```

CLI 入口是 `prthinker`。装完验证：

```bash
prthinker --help
```

---

## 场景 1 — 只用 GitHub Actions（无 GPU）

最便宜的路径：GHA-hosted runner + 付费 API 做推理，全部靠 repo secrets +
`.prthinker.yaml`。

1. **在 repo 根目录加 `.prthinker.yaml`\ ：**

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

2. **设 repo secret**\ （Settings → Secrets and variables → Actions）：

   | Secret | 值 |
   |---|---|
   | `ANTHROPIC_API_KEY` | `sk-ant-...` |

3. **复制 workflow 文件** `.github/workflows/prthinker.yml`\ ──本 repo 内
   附的版本已经声明必要 permissions（\ `contents: read`\ 、
   `pull-requests: write`\ 、\ `checks: write`\ 、\ `actions: read`\ ）。

4. **推 PR**\ ──workflow 自动跑──summary 评论 + 带 suggestion block 的
   inline review 就上来了。

完成。不需要部署服务器。成本 = 每个 PR 的 Anthropic API token。

---

## 场景 2 — 个人开发 + 付费 API key

想在本地 review 自己改的东西，不走 GHA。

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

或对 staged 变更：

```bash
git diff --cached | prthinker review-file - \
    --backend openai --openai-model gpt-4o-mini \
    --per-file --inline-review --redact-secrets
```

Markdown 结果输出到 stdout，不会贴到任何地方。

---

## 场景 3 — 个人开发 + 本地 Ollama

不想按 token 付费的话，把 prthinker 指到本地的 Ollama（通过它的
OpenAI-compatible endpoint）。

```bash
# 1. 安装并启动 Ollama（https://ollama.com）
ollama pull qwen2.5-coder:7b
ollama serve   # 监听 :11434

# 2. 用 prthinker review
pip install -e ".[runner]"

prthinker review-file my-change.diff \
    --backend openai \
    --openai-base-url http://localhost:11434/v1 \
    --openai-model qwen2.5-coder:7b \
    --openai-api-key ollama \
    --per-file --inline-review
```

（\ `--openai-api-key` 随便填个非空字符串都行──Ollama 不检查。）

同样的方式可用在 vLLM、LM Studio、llama.cpp server、Together、Groq、
DeepInfra、OpenRouter──它们都说同一种协议。

---

## 场景 4 — Claude Desktop / Cursor / Cline（MCP）

在 IDE 内直接跑 review，完全不走 GHA。

```bash
pip install -e ".[mcp]"
```

在 client 的 config 加 MCP server 条目。Claude Desktop on macOS 是
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

重启 Claude Desktop。在 chat：

> Run prthinker on `$(git diff --cached)`

LLM 调用 `review_diff` MCP tool、secret 在送 API 前被 redact 掉、
markdown review 流式回 chat。

Cursor / Continue / Cline / Zed 都用同样 schema──请查各家 MCP 文档确认
config 文件路径。

---

## 场景 5 — 团队自部署（GPU server + GHA runner）

适用于：

- 想用自家 fine-tune 的 LoRA（或不想永远按 token 付费）。
- 有 GitHub Actions 可连的 GPU 机器。
- 想要每个 PR 都有 CI 信号注入、gate、inline review。

**GPU 机器上：**

```bash
pip install -e ".[server]"

export PRTHINKER_DISMISSED_PATH=./store/dismissed.jsonl
export PRTHINKER_ACCEPTED_PATH=./store/accepted.jsonl
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000
```

前面套 nginx / Cloudflare Access + TLS。确认：

```bash
curl https://my-host:8000/healthz   # → {"status": "ok", "model": "..."}
```

**Repo 内：**

`.prthinker.yaml`\ ：

```yaml
backend: remote
remote:
  url: https://my-host:8000
  use_pipeline_endpoint: true
per_file: true
inline_review: true
gate:
  severity: error
ci_signals:
  enabled: true
rag:
  enabled: true
  remote: true            # runner 调用 /rag，不在本地加载 FAISS
```

Repo secret：

| Secret | 值 |
|---|---|
| `PRTHINKER_BACKEND_URL` | `https://my-host:8000` |
| `PRTHINKER_BACKEND_API_KEY` | （可选）reverse proxy 的 bearer token |

推 PR。Runner 保持薄（只有 httpx + pydantic）；GPU、FAISS index、
dismissed/accepted store 都在 server。

---

## 场景 6 — 研究环境（LoRA 训练 + 本地推理）

正在迭代 paper。\ `codes/train/` 的脚本负责 fine-tune LoRA；framework
对 held-out diff set 跑每个迭代结果，方便对比。

```bash
pip install -e ".[local,dev]"

# 1. 训 LoRA（超参数见 codes/train/*.py）
python -m codes.train.qwen3-coder-30b

# 2. 对标准测试语料批量跑 review
python -m codes.run.cot     # 在 cwd 为每个文件产一个目录

# 3. 查 telemetry 对比各次跑的成本/延迟
prthinker stats --since-days 7
```

`codes/run/CoT_Prompts/` 是 prompt templates；prthinker 重用它们作为
single source of truth。改 prompt → content hash 变 → cache 自动失效。

---

## `.prthinker.yaml` repo 配置

完整 schema 放在 repo 根目录。每个 key 都可省略，默认值都合理。

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
                               # 注意：不要写 `on:`──YAML 1.1 会把
                               # 未加引号的 on 解析成 boolean True。

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
  url: https://my-host:8000
  timeout_seconds: 600
  use_pipeline_endpoint: true
```

**密钥绝对不放 YAML。** API key / GitHub token 一律只从环境变量读。

### 优先级

`CLI flag` ≻ `env var` ≻ `.prthinker.yaml` ≻ `包默认`

所以 workflow 内的 flag 盖过 YAML、YAML 又盖过包默认。

---

## GitHub repo secrets

依 backend：

| Backend | 必需 secret |
|---|---|
| `remote` | `PRTHINKER_BACKEND_URL`\ 、可选 `PRTHINKER_BACKEND_API_KEY` |
| `openai` | `OPENAI_API_KEY`\ （或 `PRTHINKER_OPENAI_API_KEY`\ ） |
| `anthropic` | `ANTHROPIC_API_KEY`\ （或 `PRTHINKER_ANTHROPIC_API_KEY`\ ） |
| `local` | 无──但需要 self-hosted GPU runner |

`GITHUB_TOKEN` 是 GitHub Actions 自动提供的，不用设。

---

## GitHub Actions workflow

内附的 `.github/workflows/prthinker.yml` 已涵盖一般情况。定制请改
`env:` block──每个 CLI flag 都有对应的 `PRTHINKER_*` env var。完整列表
见 [`features.zh-CN.md`](features.zh-CN.md)。

**必要 permissions：**

```yaml
permissions:
  contents: read         # checkout
  pull-requests: write   # 贴 summary + inline review
  checks: write          # 打开与结算 gate
  actions: read          # 抓 CI 失败 log
```

**Trigger：** 默认 `pull_request` opened / synchronize / reopened。想等 CI
跑完才 review 的话：

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
```

---

## Branch protection

让 prthinker 真的能挡 error 严重度的 finding：

1. 跑至少一次 `PRTHINKER_GATE_ON=error` 的 PR，让 `prthinker` 这个
   Check Run 出现在 PR 的 Checks 标签页。
2. **Settings → Branches → branch protection rule**\ ，选默认 branch。
3. 启用 **Require status checks to pass before merging**\ ，把
   `prthinker` 加进列表。

之后，PR 只要有 error 严重度的 finding 就无法合并，直到作者处理（或
maintainer 强制覆盖）。

---

## Bootstrap 学习语料

两份 append-only JSONL 记录 PR 作者对过去 review 的反应：

```bash
# 作者按 👎 或回「false positive」的评论
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

服务器端指过去：

```bash
export PRTHINKER_DISMISSED_PATH=.prthinker/dismissed.jsonl
export PRTHINKER_ACCEPTED_PATH=.prthinker/accepted.jsonl
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000
```

两份 store 为空时都是 no-op──server log 会打印 `filter disabled` /
`exemplars disabled`\ ，行为与没装一样。

---

## Cache 与 telemetry 首次运行

```bash
prthinker review-file my-change.diff \
    --backend anthropic --anthropic-api-key "$ANTHROPIC_API_KEY" \
    --cache --telemetry
```

两份 SQLite 会生在 `.prthinker/` 下。请加进 `.gitignore`\ ──它们是
runtime state、不是 config：

```gitignore
.prthinker/cache.sqlite
.prthinker/cache.sqlite-*
.prthinker/telemetry.sqlite
.prthinker/telemetry.sqlite-*
```

（\ `dismissed.jsonl` / `accepted.jsonl` 反过来：是学到的判断，**应该**
commit。）

跑几次后查看：

```bash
prthinker stats --since-days 7
```

---

## 可选的研究级 flag

四个超越多数 LLM code-review 系统「一次性审查」之扩展。所有 flag 均为
**opt-in**\ ，需搭配 `--inline-review`；本框架交付代码，依不臆造原则
**不**\ 随附测得之 benchmark 数字。设计细节见
[`docs/zh-CN/concepts/research-extensions.rst`](../docs/zh-CN/concepts/research-extensions.rst)\ 。

| Flag                       | 环境变量                              | 默认 | 额外成本                       |
| -------------------------- | ------------------------------------ | ---- | ------------------------------ |
| `--reply-to-author`        | `PRTHINKER_REPLY_TO_AUTHOR`         | 关闭 | 一次平台 API 调用              |
| `--counterfactual`         | `PRTHINKER_COUNTERFACTUAL`          | 关闭 | 每文件多一次 backend           |
| `--provenance`             | `PRTHINKER_PROVENANCE`              | 关闭 | prompt + 输出变大              |
| `--judge`                  | `PRTHINKER_JUDGE`                   | 关闭 | 每文件多一次 backend           |
| `--self-correct`           | `PRTHINKER_SELF_CORRECT`            | 关闭 | 每文件多一次 backend           |
| `--diff-since-last`        | `PRTHINKER_DIFF_SINCE_LAST`         | 关闭 | 迭代 PR 之上省 token           |
| `--verify-suggestions`     | `PRTHINKER_VERIFY_SUGGESTIONS`      | 关闭 | 每建议多 1× sandbox + verify_cmd |
| `--api-consistency`        | `PRTHINKER_API_CONSISTENCY`         | 关闭 | 跨语言 PR 上多 1× backend      |
| `--pr-classify`            | `PRTHINKER_PR_CLASSIFY`             | 关闭 | 每 PR 多 1× backend            |
| `--reproducibility-check`  | `PRTHINKER_REPRODUCIBILITY_CHECK`   | 关闭 | 每文件多 1× backend            |
| `--dep-upgrade-check`      | `PRTHINKER_DEP_UPGRADE_CHECK`       | 关闭 | 每升级包多 1× backend          |
| `--personas`               | `PRTHINKER_PERSONAS`                | 空   | 每 PR 多 N× backend + 1 conflict step |
| `--risk-weighted`          | `PRTHINKER_RISK_WEIGHTED`           | 关闭 | 少量 `git log` 调用            |
| `--diff-entropy`           | `PRTHINKER_DIFF_ENTROPY`            | 关闭 | 纯 CPU，无 backend 调用        |

### 闭环多轮对话──`--reply-to-author`

**做什么。** 在产生下一轮审查之前\ ，通过
`PlatformAdapter.fetch_author_replies()` 取回 PR 作者对上次 prthinker
摘要评论之回复\ ，渲染成\ *Prior dialogue*\ 区块\ ，注入 inline-findings
prompt\ 。模型被要求对作者已回复过的评论\ 「\ 舍弃\ 」、「\ 精炼\ 」或
「\ 反驳\ 」\ ，但绝不静默重贴\ 。

**何时开启。** 长寿命 PR、多轮审查；团队抱怨\ 「\ bot 在我回了 wontfix
之后还是一直重贴相同评论\ 」\ 。

**怎么开启。**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --reply-to-author
```

或于 `.prthinker.yaml`：

```yaml
reply_to_author: true
```

**会看到什么。** 在以前已被作者回复过之行上的 finding\ ，下一轮应该
消失、精炼、或附上新理由\ 。

### 反事实审查──`--counterfactual`

**做什么。** 在 `--inline-review` 产生 findings 之后\ ，对其中
属于\ *设计选择*（非 bug、非 nit）之 finding\ ，列出最多三个竞争性
实现方案与小型 trade-off 矩阵（轴如 `performance`、`readability`、
`testability`）\ 。

**何时开启。** 设计面比重高之 PR（新模块、API 变更、refactor）\ 。
热修补丁不适合 —— 该步骤没得发挥\ ，只会白烧一次 backend 调用\ 。

**怎么开启。**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --counterfactual
```

或于 `.prthinker.yaml`：

```yaml
counterfactual: true
```

**会看到什么。** 每文件折叠区块多出一段\ *Alternative implementations*\ ，
列出选项与其 trade-off\ 。Parser 会丢弃选项少于 2、或 `finding_index`
越界之区块 ——\ 坏步骤绝不污染评论\ 。

### 评论来源 / 引用审计──`--provenance`

**做什么。** 要求模型为每条 finding 附上 `provenance` payload\ ，引用
RAG 规则 / accepted-example / diff 行号\ ，并可选自评信心值
∈ `[0, 1]`\ 。PR 评论每文件多一段\ *Audit trail*\ 引用清单\ 。

**何时开启。** 团队需要追问\ 「\ 为什么会提出这条评论\ 」\ ；或
训练 verifier 需要可追溯之标签\ 。会放大 prompt + 输出大小\ ，记得把
`--max-new-tokens` 调宽松\ 。

**怎么开启。**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --provenance
```

或于 `.prthinker.yaml`：

```yaml
provenance: true
```

**安全属性**（已内建于 parser）：

- 坏掉的 `provenance` 区块绝不拖垮原评论\ ；解析失败则剥除\ 并保留
  finding\ 。
- 越界之 `rag_rule` / `accepted_example` 索引会被静默丢弃 ——
  模型无法虚构引用\ 。
- `confidence` 只供人类参考\ ，**绝不**\ 被用来静默过滤 finding\ 。

### 对抗鲁棒性──`prthinker adversarial-eval`

**做什么。** 将 prompt-injection 语料送入当前 backend\ ，把每笔调用
之结果（bypass / detected / 命中 markers / 原始输出）写入 SQLite\ 。
**不输出**\ 任何聚合检测率 —— 聚合计算交给下游 SQL\ ，原始输出保留
以利审计\ 。

**何时使用。** 采用新 backend、修改 system prompt、或 paper-grade
多 provider 鲁棒性比较之前\ 。**请勿**\ 把随附之 `seed.jsonl` 视为
benchmark —— 它是涵盖四种攻击类型（`direct_injection`、
`encoded_payload`、`split_injection`、`role_hijack`）之手工种子\ 。
要发表数字之前\ ，请先扩充它\ 。

**怎么跑。**

```bash
prthinker adversarial-eval \
    --corpus prthinker/adversarial_corpus/seed.jsonl \
    --outcomes-path .prthinker/adversarial.sqlite \
    --backend openai --openai-model gpt-4o-mini
```

**检视结果。** 用 SQL 即可：

```bash
sqlite3 .prthinker/adversarial.sqlite \
  "SELECT category, COUNT(*), SUM(bypassed), SUM(detected)
     FROM outcomes
    GROUP BY category;"
```

### Force-push 差分审查──`--diff-since-last`

**做什么。** 把每文件新侧内容 hash（`FileDiff.content_sha256`），
findings 存进小型 SQLite cache，key 为
`(pr_number, repo, file_path, hunk_sha256)`。下次 push 时未动的文件
直接 reuse 上次 findings；只有真正改动的文件才重新进模型。

```bash
prthinker review-pr --pr 42 --per-file --inline-review \
    --diff-since-last --diff-cache-path .prthinker/diff-cache.sqlite
```

跨 PR 以 primary key 隔离。关 PR 时用 `ReviewCache.evict_pr()` 清掉。

### 建议 sandbox 验证──`--verify-suggestions`

**做什么。** 对每条带 `suggestion` 之 finding，把 working tree 复制到
`tempfile.mkdtemp` 套用 suggestion（用 `original` 守备检查），跑
`--verify-cmd`（默认 `pytest -x`）于 `--verify-timeout`（默认 60s）下，
把每条 finding 标 `[verified]` / `[FAILED]` / `[skipped]` / `[error]`。

```bash
prthinker review-pr --pr 42 --inline-review --verify-suggestions \
    --verify-cmd "pytest -x tests/" --verify-timeout 60
```

原 repo 绝不动；verify 命令以 argv list 跑（无 `shell=True`）。

### 跨语言 API 一致性──`--api-consistency`

**做什么。** 当 PR 同时碰到后端 `.py` 与前端 `.ts` / `.tsx` / `.js` /
`.jsx`，新增一个 step 问模型\ 「\ 跨文件 drift\ 」── 重命名字段、移除路由、
类型变更。单语言 PR 上静默 pass，不浪费 backend 调用。

```bash
prthinker review-pr --pr 42 --inline-review --api-consistency
```

### PR 类型自适应──`--pr-classify`

**做什么。** 从 diff + PR 标题 + body 把 PR 分为 bugfix / feature /
refactor / docs / chore / unknown，后续 review 深度随之调整：docs PR 跳
inline findings；bugfix PR 用 focused prompt 与较小 budget；refactor PR
放大 budget 并注入行为等价 hint。

```bash
prthinker review-pr --pr 42 --inline-review --pr-classify
```

### 评论一致性信号──`--reproducibility-check`

**做什么。** 同 prompt 跑两次 inline-findings（非 0 temperature 自然产生
第二个样本），按 (path, line, 正规化 comment) 比对，标
`[stable]` / `[low-reproducibility]`。第二次新出现之 finding 也保留。
每文件多 1× backend 调用。

```bash
prthinker review-pr --pr 42 --inline-review --reproducibility-check
```

### 依赖升级影响──`--dep-upgrade-check`

**做什么。** 检测 lock-file 触碰（`requirements.txt` / `pyproject.toml` /
`package.json`），抽出 `(package, old, new)` delta，把该包在 diff 其他
文件中的实际调用点放进 prompt，问模型 breaking change 是否影响本 repo。

```bash
prthinker review-pr --pr 42 --dep-upgrade-check
```

PR 评论顶端多出\ 「\ Dependency upgrade impact\ 」\ 表格。框架\ 不\ 在
review-time 抓 remote changelog。

### 多角色 + 冲突显化──`--personas`

**做什么。** 跑 N 个正交 lens（`security` / `performance` /
`readability` / `api_stability` / `maintainability`），每个 lens 之
prompt 明确要求只在该 lens 范围内评论。最后一个 conflict-finder step
找出角色间之分歧。PR 评论顶端多出\ 「\ Persona conflicts\ 」\ 表格（刻意
不替你选边）。

```bash
# 子集：
prthinker review-pr --pr 42 --personas security,performance,readability
# 全 5 个：
prthinker review-pr --pr 42 --personas all
```

成本：每个角色一次 backend 调用 + conflict step 一次。

### 风险加权注意力──`--risk-weighted`

**做什么。** 以 churn（`git log` 于 lookback window，默认 90 天）+
complexity proxy（HEAD 行数）+ bug history（commit message 命中
`fix:` / `bug` / `revert`）算每文件风险分。每文件
`max_findings_per_file` 随之线性缩放于 `floor`（默认 2）到
`ceiling`（默认 `2 × base_budget`）。

```bash
prthinker review-pr --pr 42 --inline-review --risk-weighted \
    --risk-workdir /path/to/repo
```

GHA 注意：`actions/checkout` 默认 shallow clone（`fetch-depth: 1`）；
请在 workflow 设 `fetch-depth: 0`，lookback window 才有 commit 可数。
默认权重（0.4 / 0.3 / 0.3）是\ 框架惯例\ ，非校准公式。

### Diff 熵──`--diff-entropy`

**做什么。** 纯 data 算 PR size + 目录分布 Shannon entropy，分为
`focused` / `wide` / `bomb`。verdict 为 `bomb` 时于评论顶端贴
\ 「\ Consider splitting this PR\ 」\ 警示。框架\ 不\ 因高分阻挡，目的是
把 PR 形状显化。

```bash
prthinker review-pr --pr 42 --diff-entropy
```

无 backend 调用，纯本机 CPU。

### 全部叠起来跑

研究级单 PR 跑法：

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

预期约为素 review 的 4–6× token 预算\ 。搭配
`--cache --cache-path .prthinker/cache.sqlite` 可在同 PR 多次迭代
时摊平成本\ 。

---

## 验证安装

跑测试套件：

```bash
pip install -e ".[dev]"
py -m pytest tests/ -q
```

本地构建文档（三种语言）：

```bash
pip install -r docs/requirements.txt
py -m sphinx -b html docs docs/_build/html
```

只会跑一次 build；输出单一 HTML 树\ ，三语在侧边栏各自为一个大章节
（English / 繁體中文 / 简体中文）\ 。应 zero error / zero warning\ 。

---

## 疑难排查

### Windows 上 `bitsandbytes` import 失败

bitsandbytes 官方只出 Linux wheel；Windows 请用上游
`bitsandbytes-windows-webui` wheel，或直接在 WSL2 内跑 prthinker。或者
完全跳过量化（local config 内 `quantization: false`\ ）──VRAM 用量会
飙，但不需要 bitsandbytes。

### 加载 Qwen3-Coder-30B 时 GPU OOM

30B 模型在 4-bit NF4 量化下大约要 18 GB VRAM。较小的 LoRA 目标可在 12 GB
卡上：

```yaml
local:
  model: Qwen/Qwen2.5-Coder-7B-Instruct
  lora_path: ../train/outputs-lora-qwen2.5-coder-7b
```

### 「PRTHINKER_BACKEND_URL secret is not configured」

Workflow 启动检查失败，因为 secret 没设。Settings → Secrets and variables
→ Actions 补上。

### RAG 跑太慢 / runner OOM 加载 embedding 模型

Qwen3-Embedding-4B 约 8 GB VRAM。默认 GitHub-hosted runner 加载不动。
依优先级：

1. `.prthinker.yaml` 内设 `rag.remote: true`\ ──runner 改打 server 的
   `/rag` endpoint，不在本地加载 FAISS。
2. `rag.enabled: false`\ ──整个关掉 RAG。会失去全局规则，但能在最小硬件
   上跑。

### Cache 文件越长越大

默认 TTL 7 天。可调 `cache.ttl_days: 1`\ （更积极）或 `cache.ttl_days: null`
（永不过期）。手动 prune：

```bash
sqlite3 .prthinker/cache.sqlite "DELETE FROM prompt_cache WHERE created_at < strftime('%s','now','-7 days');"
```

### `prthinker mcp` 报「The `mcp` package is not installed」

装了 runner profile 但没装 MCP extras：

```bash
pip install -e ".[runner,mcp]"
```

### Inline review 返回 HTTP 422

GitHub 拒绝在不在 diff 内的行贴 inline comment。Findings sanitizer 应该
在 client 侧就丢掉，但定制 prompt 可能产出超范围的条目。检查 runner
log 里的 `Dropping finding on …` 消息──每条丢弃都有 log。

### Sphinx build 抱怨 CJK punctuation

如果在改中文 docs 看到 `Inline literal start-string without end-string`\ ，
通常是 CJK 括号或 em-dash 直接贴在 \`\`code\`\` 或 \*\*bold\*\* 旁边。
中间补一个 `\ `\ （backslash + space）的 zero-width separator：

```rst
``foo``\ ──不要这样
```