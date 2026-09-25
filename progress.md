# progress.md：prthinker（Code-Review-Framework）

只放還沒做的事。做完就在同一個 commit 裡刪掉這條，並在 `docs/updates/` 新增一筆 `#done` 紀錄（格式與查詢方式見 `docs/updates/README.md`）。不放已完成的項目、不寫流水帳、不寫規則（規則在 `CLAUDE.md` / `AGENTS.md`）。實驗狀態與證據在 `paper/AGENT_HANDOFF.md`。
編號 `#n` 不重用。標記：〔決定〕需擁有者拍板、〔選作〕可做可不做、〔阻塞〕在等別的事。實驗相關項目皆需使用者決定，勿擅自開始。
跨專案與工作區層級的待辦在 `D:\Codes\progress.md`（與本專案相關：X-16、X-21）。

## 待辦

- **#2** 〔選作〕`multi_rag_on` 條件下的 LoRA vs 基礎模型：尚未安排。本輪只跑了 rag_off 一臂，故 LoRA×RAG 交互作用未測。伺服器目前仍在 LoRA 組態、語料 sha 一致，補這 44 案不需重部署，直接跑 driver 即可。
- **#3** 〔選作〕同一部署內的 LoRA 隨機化對照：尚未安排且無法直接做——LoRA 開與關無法在同一容器並存。現有結果是「相鄰部署、僅切換旗標」，論文須據實表述，不可寫成同一部署內對照。
- **#4** 〔決定〕`CHANGELOG.md` 的 Unreleased（3 項新增、1 項變更）沒發版：repo 沒有任何 tag，`prthinker` 也從沒上過 PyPI（`pyproject.toml:7` 仍是 0.1.0）。`release.yml` 只在推 `v*` tag 時觸發，發佈走 `pypi` environment 的 Trusted Publishing，所以第一次發版前要先在 PyPI 設好 trusted publisher，再決定版號、打 tag。`dev` 已經全部合進 `main`。
- **#7** 〔決定〕17 項研究級機制都還沒做端到端評估，論文以 §6.4.5 未來工作對應（`paper/REWRITE_BRIEF.md` ≈:144）；跨後端比較也屬未來工作（≈:147）。
- **#8** 〔決定〕ContextBench 的本機快取在 2026-09-22 被誤刪（工作區 `D:\Codes\docs\updates` U-20260922-20）：`D:\tmp\contextbench-repos\`（19 個公開 repo 的 clone）整個不見；`D:\tmp\contextbench_worktrees\` 還在，但每個 worktree 的 `.git` 都指向已刪除的 repo，django 那一組也只剩部分。`scores/outcomes_full.jsonl`（266/266）等結果檔都在 repo 裡，沒有受影響。要重跑 `scores/run_full.py` 之前，先整個移除 `D:\tmp\contextbench_worktrees\`：`_ensure_worktree`（`scores/run_full.py:114-118`）只要資料夾存在就直接沿用、不檢查內容，會安靜地讀到殘缺的檔案樹；`_ensure_repo` 則會自動重新 clone。
- **#14** 〔阻塞：要在 L40S 上實測〕dependabot #62 想把 `/docker` 的 `nvidia/pytorch` 從 25.09-py3 升到 26.08-py3。GPU 映像是伺服器的重現性邊界（`CLAUDE.md`「GPU Server: bf16」），升版前要在機器上跑一次 boot probe（不要設 `PRTHINKER_SKIP_BOOT_PROBE`）確認注意力實作與記憶體用量沒有退步。
