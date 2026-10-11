评估与集成
============================================================

实现支持 Python 3.10–3.14。按用户要求暂不进行模型实测；离线测试不能证明 benchmark 质量，也不能代替正式 1.0 的发布证据。

Benchmark 存档复制原始案例、固定哈希与顺序、逐案写入结果，保留失败和不支持状态，汇总前验证哈希。数据集 manifest 必须包含 dataset、HTTPS url、revision、license、source_sha256 与 cases_sha256。控制条件应固定权重 revision、adapter 状态、精度、审查步骤、解码模式与 max_new_tokens。解析后的配置不含凭证；完整审查保存实际检索文档数，未知 token 用量及费用保留 null。

对抗 v1 语料覆盖六类攻击及良性对照。文字标记分数只是攻击成功、检测、拒绝与问题覆盖的启发式代理指标，不是独立裁决或已执行的不安全动作。17 项单因素条件共用固定控制与案例顺序，各条件独立复制数据库和工作目录；缺少必要 fixture 时明确记为不支持。客观 precision／recall／F1 的配对差异附 bootstrap 区间、效应量、双侧 Wilcoxon 和全比较族群 Holm 校正，不能代替模型裁判分数。历史 44 案是“模型產生參考問題集”，不是人工黄金标准。

摘要输入是包含 diff 及可选 title、body、commits 的 JSON，独立于审查 findings。只有 --publish-summary 才更新带标记的摘要评论。知识图谱保留 Python／JS／TS 扫描，可选 Tree-sitter 支持 Java、Go、Rust、C／C++、C# 与 Kotlin；不确定或存在歧义的导入不建立链接。

自主修复要求测试，使用临时 worktree，限制重试、生成调用、时间、文件数及 patch 大小，并执行修复后审查。审计与脱敏 patch 在清理后仍保留。--open-pr 创建待人工批准合并的草稿。验证默认使用固定 digest 的 Docker 镜像；本地执行需要明确指定 --allow-unsandboxed。

质量事件只接受允许的指标和交互标识，使用至少 32 bytes 的 PRTHINKER_QUALITY_KEY 假名化。接受、忽略、应用、转 issue、回归、重开是操作信号；未知费用不能当作实测估算。操作者管理保留期限及事件导入。

IDE 标准输入／输出采用 JSONL protocol_version 1，使用唯一 request_id，支持 review／cancel／apply_patch／verify，返回进度、finding、patch 建议、验证及终止事件。应用 patch 要求明确批准、原文件 SHA-256 一致与仓库相对路径。JEditor／PyBreeze 使用隔离子进程，将结果放入 Problems 并提供 Quick Fix。需要一起安装编辑器变更，并在所选解释器安装本包。协议不会自动发布或合并。

正式发布要求完整且哈希验证通过的公开、对抗及消融结果，以及实现、安装和文档检查。通过前版本保持 0.1.0。参见 benchmarks/README.md 与 release/evidence.json。

.. code-block:: shell

   prthinker benchmark run cases.jsonl run --dataset-manifest dataset.json --control-manifest controls.json --review-pipeline
   prthinker benchmark validate run
   prthinker benchmark score run/cases.jsonl run/outcomes.jsonl --output score.json
   prthinker adversarial-benchmark run prthinker/adversarial_corpus/v1.jsonl attack-run
   prthinker adversarial-benchmark score attack-run --output attack-score.json
   prthinker ablation-study plan cases.jsonl controls.json study-plan.json
   prthinker ablation-study run cases.jsonl study-plan.json study --fixtures fixtures.json
   prthinker ablation-study compare study --output paired.json
   prthinker pr-summary --input-json summary-input.json --summary-format json --summary-output summary.json
   prthinker issue-autofix --repo owner/repo --workdir checkout --issue-number 1 --autonomous --test-cmd "python -m pytest" --sandbox-image IMAGE@sha256:DIGEST
   prthinker quality record event.json --store quality.sqlite
   prthinker quality report --store quality.sqlite --split-at 1791676800
   prthinker ide --sandbox-image IMAGE@sha256:DIGEST
   prthinker release-check release/evidence.json


发布流程先由 scripts/prepare_release.py 验证证据，再同步包、模块及引用版本到完全一致的 tag 后构建。离线验证可使用 scripts/verify_implementation.py OUTPUT --minimum-python PYTHON310 重现；可选语法包的探针是 scripts/probe_polyglot.py。

符号秩检验在非零配对差异不超过 50 对时使用条件精确推断，涵盖 44 案参考集；更大的样本使用考虑并列秩及连续性校正的正态近似，并逐项记录方法。

协议输入和输出固定使用 UTF-8，支持旧版 Windows 编码环境中的中文路径。
