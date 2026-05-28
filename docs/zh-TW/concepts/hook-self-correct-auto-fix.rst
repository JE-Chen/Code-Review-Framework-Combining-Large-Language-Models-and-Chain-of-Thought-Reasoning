Pre-commit hook、自我糾正、自動修補 PR
======================================

三項新增功能，把 prthinker 接到開發者日常流程的最後一哩。

Pre-commit hook（\ ``prthinker hook``\ ）
------------------------------------------

新增的 subcommand 會讀 ``git diff --cached``\ 、跑 per-file pipeline，
若在設定之嚴重度下限有 finding 倖存即以非零碼結束。配合
`pre-commit <https://pre-commit.com>`_ framework，prthinker 就成為
CI、IDE（MCP）、手動 CLI 之外的第四個觸發點：

.. code-block:: yaml

   # 消費端 repo 之 .pre-commit-config.yaml
   repos:
     - repo: https://github.com/<your-org>/prthinker
       rev: v0.1.0
       hooks:
         - id: prthinker
           env:
             PRTHINKER_BACKEND: openai
             PRTHINKER_OPENAI_MODEL: gpt-4o-mini

``.pre-commit-hooks.yaml`` 提供兩種 hook：

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - hook id
     - 結束碼語義
   * - ``prthinker``
     - 任一 error 嚴重度 finding 即 exit 1（commit 被擋）。可用
       ``--block-on warning`` 或 ``--block-on none`` 覆寫。
   * - ``prthinker-advisory``
     - 永遠 exit 0；finding 只印到 stderr。適合在開 branch protection
       前作為過渡。

Cache 與 telemetry 在此一樣可疊上；同一份 diff 重跑幾乎一定命中快取。

何時不要用
~~~~~~~~~~

* 若團隊提交頻率高、每次只 commit 很小的 WIP，hook 延遲會累積。改用
  ``prthinker-advisory``\ 、或把 hook 移到 ``pre-push`` 階段。
* 若隊友沒有 API 額度，僅在 CI 也審查之 branch 上啟用，避免「我能跑、
  你不能跑」的分裂。

自我糾正（\ ``--self-correct``\ ）
----------------------------------

``inline_findings`` step 產出 JSON 陣列、dismissed filter 抑制過已知重複
之後，再向模型問一次：「以資深 reviewer 視角再讀一次，哪些屬於
noise / 重複 / 過度挑剔？」runner 把模型標記之 index 從清單刪除後才
post inline review。

Prompt（\ :data:`codes.run.CoT_Prompts.finding_self_review.FINDING_SELF_REVIEW_TEMPLATE`\ ）
定義五類 noise（重複、過度挑剔、推測、同義反覆、超範圍）與四類保留
（明顯之 correctness / security、附具體修正之可維護性、隱性 bug、團隊
既有規則違規）。模型回：

.. code-block:: text

   {
     "drop": [<1-based index>, ...],
     "reasons": ["...", ...]
   }

失敗安全姿態
~~~~~~~~~~~~

:mod:`prthinker.self_review` 之 parser 故意寬容：模型輸出格式錯誤時
回\ **空 drop set**\ （不丟任何 finding），而非「全部丟」。此一不對稱
是刻意的——錯誤地 post 一筆 finding 可救（人可忽略），錯誤地刪掉一筆
真 bug 救不回。

成本
~~~~

每個檔多一次 backend call、與 finding 數量無關。開了 ``--cache`` 之後，
同一份 PR 反覆觸發只需付第一次的成本。

自動修補 draft PR（\ ``--auto-fix-threshold``\ ）
-------------------------------------------------

當倖存之 ``warning`` 嚴重度 + 帶 ``suggestion`` block 之 finding 數 ≥
threshold，runner 會：

1. 開新 branch ``auto-fix/prthinker-pr-<N>``\ 。
2. 對每個受影響檔案，由下而上套用 suggestion（保持後段行號穩定）。
   兩條相交之 edit 以先到先贏處理；被擋掉之 edit 寫入 skipped 報告。
3. 用單一固定訊息 commit。
4. 推上 branch（\ ``--force-with-lease`` 讓重跑安全）。
5. 開一個 **draft** PR 指向原 PR 之 base branch，body 摘要套用 / 跳過
   數量並列出變更檔案。

原 PR 上仍保留其原有 inline review；auto-fix PR 是一個獨立可合併之
artifact。作者檢查 diff 後決定要不要合回原 branch 或 close。

嚴重度過濾
~~~~~~~~~~

只有 ``warning`` 之 suggestion 會被自動套用。\ ``error`` finding 仍保留
為 inline comment——原則是 error 需要人類判斷「這個 patch 是否真的對」，
即便 patch 本身看起來沒問題。\ ``info`` 之 ``suggestion`` 早於 sanitizer
階段被剝掉。

衝突偵測
~~~~~~~~

純函式 :func:`prthinker.auto_fix.apply_suggestions_to_text` 回
:class:`prthinker.auto_fix.ConflictReport`\ ，內含 ``applied``\ （成功
寫入之 edit）與 ``skipped``\ （與既有 edit 相交而被擋之 edit + 擋住它
的 edit）兩份清單。偵測規則：edit 依 ``(start, end, finding_index)``
排序，按序走一遍；先到先贏。此函式不需 git 環境即可單元測試，見
``tests/test_auto_fix.py``\ 。

何時不要用
~~~~~~~~~~

* 若 CI 提供之 ``GITHUB_TOKEN`` 沒有 push branch 之權限（fork PR
  常如此），push 步驟會失敗。Auto-fix 最可靠的情境是同 repo PR。
* 若團隊要求 signed commits，auto-fix 之預設 commit 不會被簽。請在
  CI 端配置簽署，或於要求簽署之 branch 關閉此功能。

與其他功能之組合
----------------

三項新增可與既有 pipeline 自然疊合，不需要特殊處理：

* **hook ↔ cache**\ ：hook 重跑命中 CI 跑過之同一份 cache；相同 diff
  token 成本為零。
* **self-correct ↔ telemetry**\ ：多出之 backend call 與其他 ``generate``
  一樣記錄，於 ``prthinker stats`` 之 ``(backend, model)`` 欄位中可見。
* **auto-fix ↔ gate**\ ：gate 結算發生在 auto-fix 之前，所以原 PR 之
  Check Run 反映「未修補」狀態。作者合回 auto-fix PR 後，下一次推送會
  重新觸發 gate 對修正後 diff。
* **auto-fix ↔ judge**\ ：judge verdict 套在原 PR；auto-fix PR 不自己再
  跑 prthinker（會循環）。

CLI flag 速查
-------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 環境變數
     - 預設
   * - ``hook`` subcommand
     - 不適用
     - —
   * - ``--advisory``\ （僅 hook）
     - ``PRTHINKER_HOOK_ADVISORY``
     - ``false``
   * - ``--block-on {none,warning,error}``\ （僅 hook）
     - ``PRTHINKER_HOOK_BLOCK_ON``
     - ``error``
   * - ``--self-correct``
     - ``PRTHINKER_SELF_CORRECT``
     - ``false``
   * - ``--auto-fix-threshold N``\ （review-pr）
     - ``PRTHINKER_AUTO_FIX_THRESHOLD``
     - ``0``\ （關閉）
   * - ``--auto-fix-base-branch BRANCH``\ （review-pr）
     - ``PRTHINKER_AUTO_FIX_BASE_BRANCH``
     - *(自原 PR 抓)*
