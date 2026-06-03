CI 訊號與合併前 gate
====================

兩個功能讓 reviewer 從「丟一句留言」變成「依資料行動」：\ **CI 失敗訊號**
（輸入端）與 **Check Run gate**\ （輸出端）。

CI 失敗訊號
-----------

開 ``--include-ci-signals`` 時，runner 會抓 PR head SHA 已經完成的
Actions runs，挑出失敗的，把每個失敗 job 的 log 末端取出，包成 fenced
區塊**前置到 diff** 再跑 pipeline：

.. code-block:: text

   <!-- CI Failure Signals -->
   # CI Failure Signals

   These are failed jobs from the latest CI run on this PR head.
   Correlate findings with the failures below when applicable; do NOT
   invent failures not present here.

   ## CI / test-python (failure)

   ```
   E   AssertionError: expected 1, got 2
   E       at tests/test_auth.py:42
   ...
   ```

   <!-- End CI Failure Signals -->

   diff --git a/auth.py b/auth.py
   ...

模型現在有 runtime context。Finding 可以把 flagged 行與具體測試失敗對上
（「\ ``auth.py:42`` 這個改動對應到上面的 ``test_auth`` 退步」）。

可調整參數
~~~~~~~~~~

* ``--ci-signal-max-jobs N``\ ──最多納入幾個失敗 job。預設 ``5``\ ，每個 job
  獨立處理。
* ``--ci-signal-tail-chars N``\ ──每個 job 保留多少字（從末端切）。預設
  ``4000``\ 。模型通常只會用到最後幾百字。

兩個旋鈕都在 prompt token 預算與訊號覆蓋率之間做取捨。

權限
~~~~

Actions API 需要 ``actions: read`` 權限。內附 workflow 已宣告；fork 時請
保留。

時機
~~~~

預設的 ``pull_request`` trigger 一推就跑，比任何 CI 都早。Runner 拿到的是
「跑這一刻 head SHA 上已存在的 CI 訊號」──通常是首次推送什麼都拿不到，
之後每次推送拿到的是上一次 run 的 log。

如果你要 reviewer 等 CI 跑完：

.. code-block:: yaml

   on:
     workflow_run:
       workflows: ["CI"]
       types: [completed]

``workflow_run`` 模式下要從 run payload 取得 PR 編號──請見 ``prthinker.yml``
的內附註解。

合併前 Check Run gate
---------------------

``--gate-on`` flag 控制 PR head commit 上一個名為 ``prthinker`` 的專屬
Check Run。CLI 會：

1. 審查開始時 ``POST /check-runs``\ ，狀態 ``status: in_progress``\ 。
2. Pipeline 跑完（含 dismissed filter）後，依嚴重度分類計算 surviving
   findings 數量。
3. ``PATCH /check-runs/:id`` 把 ``status`` 設為 ``completed``\ ，\ ``conclusion``
   根據設定的 gate floor 決定。

結算邏輯
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - ``--gate-on``
     - 何時結算為 ``failure``
     - 否則
   * - ``none``
     - 永遠不
     - 永遠 ``success``
   * - ``error``
     - ``error`` 數 ≥ 1
     - ``success``
   * - ``warning``
     - ``error`` 或 ``warning`` 數 ≥ 1
     - ``success``\ （只有 ``info`` 時）

``info`` 嚴重度的 finding **永遠不會**\ 觸發 gate。它們是團隊可能在意也可能
不在意的小問題──如果連這也擋合併，merge friction 會爆炸。

設成 branch protection
----------------------

把 reviewer 真的接到擋合併：

1. 跑至少一次 ``PRTHINKER_GATE_ON=error`` 的 PR，讓 ``prthinker`` 這個 Check
   Run 出現在 Checks 分頁。
2. **Settings → Branches → branch protection rule**\ ，選你的預設 branch。
3. 啟用 **Require status checks to pass before merging**\ ，把 ``prthinker``
   加進必要檢查。

之後，只要 PR 還有 error 嚴重度的 finding 就無法合併。作者會直接看到 gate
結果（Check Run summary 會列出 error / warning / info 的數量分佈）。

例外情境
~~~~~~~~

* **Pipeline crash**\ ──CLI 的 exception handler 會 PATCH Check Run 成
  ``conclusion: failure``\ ，\ ``title: "Reviewer crashed"``\ 。PR 不會永遠卡在
  「跑中」的狀態。
* **空 diff**\ ──reviewer 直接跳過：不開 Check Run、不貼留言。
* **Findings 被過濾到零**\ ──gate 結算為 ``success``\ 。總結留言仍會貼上來
  讓作者知道 reviewer 有跑過。

貼出審查：留言與 inline 建議
----------------------------

完整的逐檔審查可能達數百 KB，遠超過 GitHub 單則留言 65 536 字元的上限。
與其截斷，總結會\ **切分成多則留言**\ ：只在整個檔案區塊之間切（絕不切在
區塊中間），第一則之後的每一則都帶有 ``Part k/N`` 標記。跨多次 push 時，
這些分頁會以 marker 對齊\ ──既有留言原地更新、不足的分頁新增、上一輪較長
留言殘留的多餘分頁刪除，殘缺的舊分頁不會留下。GitHub 以外的平台則退回
單則留言（溢出的內容留在 job log 裡）。

加上 ``--findings-only``\ （環境變數 ``PRTHINKER_FINDINGS_ONLY``）時，總結
\ **只**\ 列出有 finding 的檔案；乾淨的檔案會收合成一行
``N file(s) reviewed with no findings — hidden``\ ，而整個 PR 零 finding 時
則收合成一行 ``✅ No findings`` 確認訊息，而非完整的空結果。在大型但大多
乾淨的 PR 上，這通常能把多則分頁的總結縮回單則留言。

inline 建議\ ──diff 上一鍵 *Apply suggestion* 的區塊\ ──會以另一個 PR
review 貼出。新的 review 會\ **先**\ 送出，之後才移除上一輪的 inline 留言，
而且移除時會排除剛剛送出的 review。先貼再移除代表：當送出被拒（只要有任何
一則留言指到 diff hunk 範圍外的行，GitHub 會 422 拒絕\ *整個*\ review）時，
上一輪的建議仍會保留，而不是在失敗的重貼之前就被清掉。

CI 訊號 + gate 一起用
---------------------

兩個功能組合得很好：CI 訊號讓 findings 更可能包含真正的 bug（模型可以
grounding 在實際的失敗），gate 再把這些更高品質的 finding 變成硬性合併
阻擋。

更嚴的設定可以再開 ``--rules-dir``\ （團隊規則），讓模型知道你的團隊把
什麼當 error、什麼當 warning。
