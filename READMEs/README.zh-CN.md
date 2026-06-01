# prthinker

[English](../README.md) · [繁體中文](README.zh-TW.md) · **简体中文**

> 为 GitHub Pull Request 设计的思维链（Chain-of-Thought）代码审查框架，
> 底层由微调后的 Qwen3-Coder 模型加上检索增强（RAG）提示驱动。

`prthinker` 会读取 PR diff、执行五步思维链审查、把结构化的总结与一键应用的
`suggestion` 区块回帖到 PR。它会从每个 repo 的历史中学习──被 PR 作者拒绝的评论
下次会被过滤掉，被采纳的建议会以示例（exemplar）的形式注入下一轮 prompt──
并且可以作为合并前的必需状态检查。

## 你会得到什么

- **五步 CoT pipeline**──`first_summary` → `first_code_review` → `linter` →
  `code_smell` → `total_summary`，外加可选的逐文件 inline-findings 步骤，
  输出结构化 JSON。
- **逐文件 inline review**，配合 GitHub `suggestion` 区块，PR 作者点一下
  即可应用。
- **全局规则 + 各 repo 规则包**：通过 `--rules-dir` 把团队自定的 markdown
  规则加进 prompt。
- **两份学习语料**：`dismissed.jsonl`（用相似度过滤掉重复命中）、
  `accepted.jsonl`（把 top-K 采纳过的示例注入 prompt）。
- **CI 失败信号**：把失败 job 的末端日志前置到 diff，让 reviewer 能对齐
  flagged 行与实际的测试失败。
- **合并前 Check Run gate**：当出现 error 严重度的 finding 时让 Check Run
  变成 failure，可在 branch protection 设为必需检查。
- **可替换的 backend**：四种任你挑──本地 in-process Hugging Face
  causal-LM（Qwen、Llama、Mistral、CodeLlama …，支持 LoRA + 量化）、
  自部署 FastAPI 推理服务器、任何 OpenAI-Chat-Completions 兼容端点
  （OpenAI、Azure、vLLM、Ollama `/v1`、LM Studio、Together、Groq、
  DeepInfra、OpenRouter …）、或 Anthropic Claude Messages API。

### 研究级扩展（opt-in）

十三个多数 LLM code review 系统未实作的机制。大多需搭配 `--inline-review`；
依本项目不臆造原则，我们只交付框架，量化 benchmark 数字属于未来工作。

- **对抗鲁棒性**（`prthinker adversarial-eval`）──针对四种攻击类型跑
  prompt-injection 语料，把每一笔调用结果写入 SQLite。随附之
  `seed.jsonl` 是种子语料，**不是** benchmark。
- **闭环多轮对话**（`--reply-to-author`）──读取 PR 作者对上次 prthinker
  摘要评论之回复，注入为 *Prior dialogue* 区块。
- **反事实审查**（`--counterfactual`）──针对属于 *设计选择* 之 finding，
  列出竞争性实现方案与小型 trade-off 矩阵。
- **评论来源 / 引用审计**（`--provenance`）──每条 finding 附上 `provenance`
  payload，标注引用了哪一条 RAG 规则 / accepted-example / diff 行号。
- **Force-push 差分**（`--diff-since-last`）──把每文件新侧内容 hash，
  同一 PR 之下次 push 时未动的文件直接 reuse 上次 findings。
- **建议 sandbox 验证**（`--verify-suggestions`）──把 working tree 复制到
  disposable sandbox 套用 suggestion 后跑 `--verify-cmd`，每条建议标
  `[verified]` / `[FAILED]` / `[skipped]` / `[error]`。原 repo 绝不动。
- **跨语言 API 一致性**（`--api-consistency`）──当 PR 同时碰到后端 `.py`
  与前端 `.ts` / `.tsx`，新增一个 step 检测两侧 request/response 形状漂移。
- **PR 类型自适应**（`--pr-classify`）──从 diff + 标题 + body 把 PR 分为
  bugfix / feature / refactor / docs / chore / unknown，后续 review 深度
  随之调整。
- **评论一致性信号**（`--reproducibility-check`）──同 prompt 跑两次 inline-findings，
  把 finding 标 `[stable]` / `[low-reproducibility]`。
- **依赖升级影响**（`--dep-upgrade-check`）──检测 lock-file 触碰，
  抽出版本 delta，问模型 breaking change 是否影响本 repo 之实际用法。
- **多角色 + 冲突显化**（`--personas`）──跑 N 个正交 lens（security /
  performance / readability / api_stability / maintainability），
  conflict-finder step 把它们的分歧显化出来。
- **风险加权注意力**（`--risk-weighted`）──以 churn + complexity + bug
  history（从 `git log` 抓）算每文件风险分，按比例缩放 finding budget。
- **Diff 熵 /「Diff bomb」检测**（`--diff-entropy`）──算 PR size +
  目录分布 Shannon entropy；熵高时于评论顶端贴「Consider splitting this PR」警示。

设计细节见 [`docs/zh-CN/concepts/research-extensions.rst`](../docs/zh-CN/concepts/research-extensions.rst)。

## 快速开始

```bash
# 只装 runner 所需依赖，不需要 torch / transformers
pip install -e ".[runner]"

# 对本地 diff 跑审查（指向远程推理服务器）
prthinker review-file my-change.diff \
    --backend remote \
    --remote-url http://my-host:9000 \
    --per-file --inline-review

# 完整审查 PR（GitHub Action 内部用的就是这个）
prthinker review-pr \
    --repo owner/name --pr-number 42 \
    --backend remote --remote-url http://my-host:9000 \
    --gate-on error --include-ci-signals

# …或通过 OpenAI-compat backend 使用 OpenAI / Azure / vLLM / Ollama
prthinker review-pr --repo o/r --pr-number 42 \
    --backend openai \
    --openai-base-url http://localhost:11434/v1 \
    --openai-model llama3.1:8b \
    --openai-api-key ollama

# …或使用 Anthropic Claude
prthinker review-pr --repo o/r --pr-number 42 \
    --backend anthropic \
    --anthropic-model claude-sonnet-4-6 \
    --anthropic-api-key "$ANTHROPIC_API_KEY"

# …或一次开启所有研究级扩展
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review \
    --reply-to-author --counterfactual --provenance \
    --diff-since-last --verify-suggestions --api-consistency \
    --pr-classify --reproducibility-check --dep-upgrade-check \
    --personas all --risk-weighted --diff-entropy \
    --judge --self-correct

# 对 backend 做 prompt-injection 鲁棒性压测
prthinker adversarial-eval \
    --corpus prthinker/adversarial_corpus/seed.jsonl \
    --outcomes-path .prthinker/adversarial.sqlite \
    --backend openai --openai-model gpt-4o-mini
```

部署推理服务器（需要 GPU 与较重的依赖）：

```bash
pip install -e ".[server]"
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 9000
```

或使用 `docker/` compose bundle。base 部署把 FastAPI 服务器 expose 在
`:9000`；其上可再叠两个可选 overlay：

```bash
cd docker && cp .env.example .env
docker compose up -d                                                  # :9000
docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d        # +TLS+token :443
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d # +仪表板 :9000
```

monitoring overlay 把所有东西依路径收在 host `:9000` 之下——`/grafana/`
（Grafana，默认 `admin`/`admin`）、`/prometheus/`、`/cadvisor/`、`/kg/`
（repo knowledge-graph 页），其余路径一律由 prthinker 提供。完整参考
（文件、volume、路由 URL）：
[`docs/zh-CN/concepts/docker-platforms-report.rst`](../docs/zh-CN/concepts/docker-platforms-report.rst)。

## GitHub Actions

复制 `.github/workflows/prthinker.yml`，然后在 repo 设置两个 secrets：

| Secret               | 用途                                |
| -------------------- | ----------------------------------- |
| `PRTHINKER_BACKEND_URL`    | FastAPI 推理服务器的基础 URL        |
| `PRTHINKER_BACKEND_API_KEY`| Bearer token（可选）                |

workflow 在 `pull_request` opened / synchronize / reopened 时触发，
跑三个 job：`enumerate` 列出 files（依 `PRTHINKER_EXCLUDE_GLOBS` 过滤
noise），`review` 是个 matrix──每个 file 各自一个 runner + 60 分钟
timeout，`aggregate` 合所有 partial JSON 为单一 summary comment +
一个 inline review + 开关 gate 各一次。Runner ↔ server 走
`POST /review/submit` + `GET /review/result/{id}` 轮询，所以即使
反向 proxy 有短 idle timeout（如 Cloudflare 100 秒）也不会撞墙。

Workflow 被取消时不会继续烧 GPU──runner 离开前会 post
`POST /review/cancel/{id}`\ ；backend 的 idle sweeper 也会把 180 秒
没被 poll 的 job 自动设成 cancel。Aggregate 之 PR-wide
`### Overall Summary` 通过 `POST /ask/submit` 跨 file 合成。
对同一 SHA 重复 run 不会累积：summary comment 就地 upsert、旧
inline review 的 child comments 全部删掉、旧 `prthinker` check
PATCH 成 *superseded* 灰色状态。完整架构见
[`docs/zh-CN/guide/github-actions.rst`](../docs/zh-CN/guide/github-actions.rst)。

## 文档

- **[`setup.zh-CN.md`](setup.zh-CN.md)** — 完整设置指南（六种场景、
  所有 env var、疑难排查）。
- **[`features.zh-CN.md`](features.zh-CN.md)** — 完整功能总览。
- **[`docs/zh-CN/`](../docs/zh-CN/)** — Read-the-Docs 风格深度章节。

完整文档在 [`docs/`](../docs/) 并通过 Read the Docs 发布，三种语言并行维护：

- `docs/`（英文，主版本）
- `docs/zh-TW/`（繁体中文）
- `docs/zh-CN/`（简体中文）

每个版本包含：

- **Guide**──安装、快速开始、配置、GitHub Actions
- **Concepts**──架构、pipeline、RAG、语料库、CI 信号与 gate
- **Reference**──CLI、HTTP API、Python API

本地构建文档：

```bash
pip install -r docs/requirements.txt
py -m sphinx -b html docs docs/_build/html
```

## 仓库结构

```
prthinker/        独立 Python 包（Strategy / Factory / Registry）
codes/run/           原本的脚本；cot.py 与 fastapi_server.py 现在会调用包
codes/run/CoT_Prompts/  Prompt templates（单一真实来源）
codes/train/         LoRA 微调脚本（Qwen3.1-7B、Qwen2.5-Coder-7B、Qwen3-30B、Qwen3-Coder-30B）
codes/util/          模型加载 + FAISS 检索工具
datas/               测试数据、RAG 规则文档
paper/               论文 + slide build
.github/workflows/   prthinker.yml──GHA 集成
docs/                Sphinx 文档
```

## 引用

若在学术工作中使用本框架，请引用 `paper/` 下对应的论文。Read the Docs 站点
附有原始稿件链接。

## 许可证

请见 [LICENSE](../LICENSE)。