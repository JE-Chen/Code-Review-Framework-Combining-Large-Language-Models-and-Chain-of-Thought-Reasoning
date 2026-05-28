# reviewmind

[English](../README.md) · [繁體中文](README.zh-TW.md) · **简体中文**

> 为 GitHub Pull Request 设计的思维链（Chain-of-Thought）代码审查框架，
> 底层由微调后的 Qwen3-Coder 模型加上检索增强（RAG）提示驱动。

`reviewmind` 会读取 PR diff、执行五步思维链审查、把结构化的总结与一键应用的
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

四个多数 LLM code review 系统未实作的机制。均需搭配 `--inline-review`；
依本项目不臆造原则，我们只交付框架，量化 benchmark 数字属于未来工作。

- **对抗鲁棒性**（`reviewmind adversarial-eval`）──针对四种攻击类型
  （direct injection / encoded payload / split injection / role hijack）
  跑 prompt-injection 语料，把每一笔调用结果写入 SQLite。随附之
  `seed.jsonl` 是种子语料，**不是** benchmark。
- **闭环多轮对话**（`--reply-to-author`）──读取 PR 作者对上次 reviewmind
  摘要评论之回复，注入为 *Prior dialogue* 区块。下一次审查可在作者
  反论下舍弃 / 精炼 / 反驳该评论。
- **反事实审查**（`--counterfactual`）──针对属于 *设计选择* 之 finding，
  列出竞争性实现方案与小型 trade-off 矩阵，而非单一「请改成 X」。
- **评论来源 / 引用审计**（`--provenance`）──每条 finding 附上 `provenance`
  payload，标注引用了哪一条 RAG 规则 / accepted-example / diff 行号，
  并可选自评信心值 ∈ [0, 1]。坏引用绝不拖垮真评论。

设计细节见 [`docs/zh-CN/concepts/research-extensions.rst`](../docs/zh-CN/concepts/research-extensions.rst)。

## 快速开始

```bash
# 只装 runner 所需依赖，不需要 torch / transformers
pip install -e ".[runner]"

# 对本地 diff 跑审查（指向远程推理服务器）
reviewmind review-file my-change.diff \
    --backend remote \
    --remote-url https://my-host:8000 \
    --per-file --inline-review

# 完整审查 PR（GitHub Action 内部用的就是这个）
reviewmind review-pr \
    --repo owner/name --pr-number 42 \
    --backend remote --remote-url https://my-host:8000 \
    --gate-on error --include-ci-signals

# …或通过 OpenAI-compat backend 使用 OpenAI / Azure / vLLM / Ollama
reviewmind review-pr --repo o/r --pr-number 42 \
    --backend openai \
    --openai-base-url http://localhost:11434/v1 \
    --openai-model llama3.1:8b \
    --openai-api-key ollama

# …或使用 Anthropic Claude
reviewmind review-pr --repo o/r --pr-number 42 \
    --backend anthropic \
    --anthropic-model claude-sonnet-4-6 \
    --anthropic-api-key "$ANTHROPIC_API_KEY"

# …或一次开启所有研究级扩展
reviewmind review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review \
    --reply-to-author --counterfactual --provenance \
    --judge --self-correct

# 对 backend 做 prompt-injection 鲁棒性压测
reviewmind adversarial-eval \
    --corpus reviewmind/adversarial_corpus/seed.jsonl \
    --outcomes-path .reviewmind/adversarial.sqlite \
    --backend openai --openai-model gpt-4o-mini
```

部署推理服务器（需要 GPU 与较重的依赖）：

```bash
pip install -e ".[server]"
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000
```

## GitHub Actions

复制 `.github/workflows/reviewmind.yml`，然后在 repo 设置两个 secrets：

| Secret               | 用途                                |
| -------------------- | ----------------------------------- |
| `REVIEWMIND_BACKEND_URL`    | FastAPI 推理服务器的基础 URL        |
| `REVIEWMIND_BACKEND_API_KEY`| Bearer token（可选）                |

workflow 会在 `pull_request` opened / synchronize / reopened 时触发，
并维护一条可折叠的 PR 评论（重复触发时就地 upsert，不刷屏）。

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
py -m sphinx -b html docs            docs/_build/html-en
py -m sphinx -b html docs/zh-TW      docs/_build/html-zh-TW
py -m sphinx -b html docs/zh-CN      docs/_build/html-zh-CN
```

## 仓库结构

```
reviewmind/        独立 Python 包（Strategy / Factory / Registry）
codes/run/           原本的脚本；cot.py 与 fastapi_server.py 现在会调用包
codes/run/CoT_Prompts/  Prompt templates（单一真实来源）
codes/train/         LoRA 微调脚本（Qwen3.1-7B、Qwen2.5-Coder-7B、Qwen3-30B、Qwen3-Coder-30B）
codes/util/          模型加载 + FAISS 检索工具
datas/               测试数据、RAG 规则文档
paper/               论文 + slide build
.github/workflows/   reviewmind.yml──GHA 集成
docs/                Sphinx 文档
```

## 引用

若在学术工作中使用本框架，请引用 `paper/` 下对应的论文。Read the Docs 站点
附有原始稿件链接。

## 许可证

请见 [LICENSE](../LICENSE)。
