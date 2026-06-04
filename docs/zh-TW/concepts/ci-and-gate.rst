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

加上 ``--pr-overview``\ （環境變數 ``PRTHINKER_PR_OVERVIEW``）時，總結最上方
會多一段不需模型的 **What this PR does (preliminary)** 區塊，完全由 PR 的
commit messages 與變更檔案\ *決定式*\ 產生：檔案／目錄／副檔名分佈、
conventional-commit 類型統計（``feat (3) · fix (1)``），以及 commit 主旨清單。
它是\ *脈絡*\ 而非結論──回答「改了什麼」，下方的摘要才回答「好不好」──
同樣固定在會被原地更新的 part-1 留言，每次審查都會刷新。

``--impact-map``\ （環境變數 ``PRTHINKER_IMPACT_MAP``）會加一段 **Impacted
areas** 註記，列出變更檔案的\ *下游 importer*\ ──import 了被改動模組、但
本身沒被改到的檔案──資料來自 repo 知識圖譜（``repo-kg.sqlite``）。它標示
diff 本身看不到的波及面。比對是啟發式（模組名 vs import target），所以是
提示性質；KG 不存在時靜默略過。

每份逐檔總結最上方都有一個 **Review at a glance** 摘要──白話的狀態
（🔴 changes requested／🟡 review suggested／🔵 minor notes／✅ looks good）、
依嚴重度分類的 finding 數量、已審查／有 finding／乾淨的檔案分佈，以及
finding 最多的\ *熱點*\ 檔案。當任何 finding 附帶一鍵 ``suggestion`` 時，摘要
會在一行 **Suggestions** 統計它們的數量（跑過 ``--verify-suggestions`` 時還會
標出沙箱驗證過的數量）；另有一行 **Review effort** 給出粗略的 ``~N min`` 估計
（依檔案數與 finding 嚴重度加權）以及有幾個檔案需要注意，讓人不必展開任何
區塊就能掌握工作量。有開 gate 時還會顯示一行 **Gate**\ （✅ pass / ❌ failure
與 error／warning／info 數）；結算為 failure 時，這行會連結第一個觸發 floor 的
finding 作為\ *第一個阻擋點*\ ，讓原因一鍵可達。此摘要固定在會被原地更新的
part-1 留言最上方，所以每次重新審查都會原地改寫，永遠反映最新一次的結果。

摘要下方有一個可展開的 **By severity** 索引，依最嚴重度把檔案分組。當 finding
帶有 ``category``\ （security／correctness／performance／design／test／docs／
style／other）時，旁邊還會有一個可展開的 **By category** 索引，依主題把 finding
分組，讓審查者一次只處理一類關注點；沒有任何 finding 被分類時則整段省略。每則
留言結尾則有中繼資料 footer（commit、後端/模型、檔案覆蓋、prthinker 版本、
時間戳）以及一個可展開的 **Legend** 解釋所有圖示。

當存在 error 嚴重度的 finding 時，最上方會釘一個 **🚨 Must fix** 清單──把
error finding 以單行加深層連結列出，並引用出問題的那行原始碼（從 diff 解析），
讓阻擋性問題不必展開任何區塊、也不必開 Files-changed 分頁就讀得到。含 error
的檔案會展開呈現（``<details open>``），乾淨／warning／info 維持收合；每個檔案
區塊還會有一行 ``Signal:``\ ，統計 sandbox 驗證過的 suggestion（``✓``）與低
再現性 finding（``⚠️``），讓高可信的 finding 更突出。

若想要一條橫跨整個 PR 的優先佇列，可展開的 **🔝 Top findings** 清單會把每一條
finding 依嚴重度再依模型信心排序──比只含 error 的 Must-fix 更廣、比檔案層級的
熱點更扁平──讓審查者有一個\ 「\ 先看這些\ 」\ 的順序。逐檔區塊已能看出優先序的
小型審查則略過。

加上 ``--walkthrough`` 時，每個檔案區塊最上方會有一段 **📝 Walkthrough**\ ──
模型寫的、關於該檔變更\ 「\ 做了什麼、為何\ 」\ 的簡短敘事，釘在審查 summary
之上，因為它是\ *定位*\ （變更\ *是什麼*\ ）、要在\ *評斷*\ （\ *哪裡有問題*\ ）
之前讀。它是無推論之 commit-message PR 概覽之推論側對應物，只描述、不評斷。

每個檔案都是自己的可展開 ``<details>`` 項，summary 在檔名前以最嚴重度的狀態
圖示（``🔴`` / ``🟡`` / ``🔵``）開頭，讓整份審查成為一份可掃描的檔案選單。
逐檔區塊會\ **依嚴重度排序**\ （有 error 的檔案在前，再來 warning、info，
同級再比 finding 數），每個檔案的徽章改用嚴重度圖示（``🔴2 🟡1``）而非單純
數字，並附上變更規模徽章（``+12 −3 · 2 hunks``\ ，直接從 diff 解析），讓選單
在展開前就顯示每個變更\ *有多大*\ 。加上 ``--findings-only``\ （CI 預設開啟）時，
沒有 finding 的檔案會被跳過而不列出。``--summary-table``\ （環境變數
``PRTHINKER_SUMMARY_TABLE``）會把收合區塊換成一個緊湊的
``severity | location | finding`` 表格──finding 很多時更快掃。在 GitHub 上，
每個檔名──熱點列與區塊標頭──都是\ **深層連結**\ ，直接跳到該檔在
Files-changed 分頁的第一個 finding（GitHub Enterprise 主機請設定
``PRTHINKER_PR_FILES_URL``）。

在索引區塊與逐檔細節之間，會放一組可選的\ *定位*\ 區塊，每個都是 best-effort、
會自我省略（只有有話可說時才呈現）：

* 一個 **Suggested review order** 註記（``--review-order``）用 repo knowledge
  graph 的 import 邊把變更檔案按\ 「\ 被最多其他變更檔案依賴\ 」\ 排前面，最地基
  的檔案標上\ 「\ start here\ 」\ ──讓審查者先讀基礎變更再讀其呼叫端。
* 一個 **high-risk files** 註記（``--risk-weighted``）把預算分配器本來就算出的
  每檔風險分（churn＋複雜度＋bug 歷史）秀出來，讓審查者知道歷史上哪些檔案最
  脆弱──不論本次 PR 是否在它們上面提出 finding。
* 一個 **🧪 changed without a matching test change** 區塊，列出同名測試未一併
  變更的 production ``.py`` 檔──一個便宜、確定性的提示（不需推論），永遠開啟
  且永不作為 gate，因為 docs-only 或純重構的變更本來就不需要動測試。
* 一個 **🗺️ Change map**\ （``--change-map``\ ）在留言內嵌一張小的 Mermaid 圖，
  畫出變更檔案之間的 import 邊，讓改動的結構一眼可見。
* 一個 **✅ Reviewer checklist** 收集一鍵 suggestion 無法自行了結的項目──未驗證
  的 error 修正、低再現性 finding、跨語言 API drift──以 ``- [ ]`` 方框呈現，給
  審查者一份明確的把關清單，而不必自己重新推導。

加上 ``--review-delta``\ （環境變數 ``PRTHINKER_REVIEW_DELTA``）時，摘要會多一行
``Since last review: +2 new · 3 resolved · 5 carried``\ 。finding 以
``(path, severity, comment)`` 取指紋──而非會隨 push 位移的行號──並把這組
指紋持久化在 CI 本來就會跨 push 還原的 per-PR 狀態（``--delta-state``\ ，預設
``.prthinker/pr-state/findings-fp.json``）裡，因此重推時一眼就能看到進展。
同一行在作者於上次審查後有回覆時會接上 ``💬 N author reply(ies)``\ 。接著由
兩個收合清單把差異具體呈現：本次 run 才首度出現的 finding 會收進一個
**🆕 New since last review** 區塊，消失的 finding 則以刪除線列在 **✅ Resolved
since last review** 區塊──讓重新審查只需讀新增的條目、作者有成就感、審查者
清楚看到哪些已處理。

完整的逐檔審查可能達數百 KB，遠超過 GitHub 單則留言 65 536 字元的上限。
與其截斷，總結會\ **切分成多則留言**\ ：在整個檔案區塊之間切，第一則之後的
每一則都帶有 ``Part k/N`` 標記。單一檔案區塊若本身就超過一頁，會在它的巢狀
子區塊邊界切分──每一片都是自我閉合、可獨立成立的 ``<details>``\ ，所以標記
不會跨留言斷裂，續接的片段會標上 ``(continued)``\ ──而不是被單則留言上限
截斷。跨多次 push 時，
這些分頁會以 marker 對齊\ ──既有留言原地更新、不足的分頁新增、上一輪較長
留言殘留的多餘分頁刪除，殘缺的舊分頁不會留下。GitHub 以外的平台則退回
單則留言（溢出的內容留在 job log 裡）。

加上 ``--findings-only``\ （環境變數 ``PRTHINKER_FINDINGS_ONLY``）時，總結
\ **只**\ 列出有 finding 的檔案；乾淨的檔案會收合成一行
``N file(s) reviewed with no findings — hidden``\ ，而整個 PR 零 finding 時
則收合成一行 ``✅ No findings`` 確認訊息，而非完整的空結果。在大型但大多
乾淨的 PR 上，這通常能把多則分頁的總結縮回單則留言。

``--hide-info``\ （環境變數 ``PRTHINKER_HIDE_INFO``）會把 ``info`` 嚴重度的
finding 從總結中略去──數量徽章、at-a-glance 統計、熱點排名都不計入它們，
而只有 info finding 的檔案會被視為乾淨。這只影響顯示：diff 上的 inline
review 與合併 gate 仍會看到所有 finding。

``--summary-min-confidence``\ （環境變數 ``PRTHINKER_SUMMARY_MIN_CONFIDENCE``\ ，
0–1 浮點數）會進一步把模型信心低於門檻的 finding 從總結中丟掉；沒有信心
分數的 finding 一律保留（未知不丟）。同樣只影響顯示。

由於這兩者會悄悄縮小摘要計數（否則讀者會看到 ``🔵 0 info`` 而誤以為本來就
沒有），摘要會多一行 **Filtered from view**\ ──``2 info · 1 low-confidence
hidden``\ ──以\ *未過濾*\ 的結果計算，使摘要永不隱藏它隱藏了多少
（no-silent-caps 原則）。

加上 ``--pr-labels``\ （環境變數 ``PRTHINKER_PR_LABELS``）時，reviewer 還會
在 PR 上貼兩個受管理的標籤──規模（``prthinker/size-xs`` … ``size-xl``\ ，
依審查檔案數）與狀態（``prthinker/changes-requested`` / ``review-suggested``
/ ``clean``）──讓 PR 列表不必逐一點開就能掃描。只有 ``prthinker/`` 前綴的
標籤會跨 run 對齊，人工貼的標籤完全不動。

每則 inline 留言體都以一個 `Conventional Comments
<https://conventionalcomments.org>`_ 標籤開頭，由 finding 的嚴重度與 category
推得──``🔴 issue (security):``\ 、``🟡 suggestion:``\ 、``🔵 nitpick:``\ ──
讓讀者（與工具）一眼分流阻擋性與可選項。同一個共用 formatter 在每個平台
（GitHub、Gitea）渲染留言體，所以標籤與一鍵 suggestion 區塊在各 host 上完全
一致。

inline 建議\ ──diff 上一鍵 *Apply suggestion* 的區塊\ ──會以另一個 PR
review 貼出。新的 review 會\ **先**\ 送出，之後才移除上一輪的 inline 留言，
而且移除時會排除剛剛送出的 review。先貼再移除代表：當送出被拒（只要有任何
一則留言指到 diff hunk 範圍外的行，GitHub 會 422 拒絕\ *整個*\ review）時，
上一輪的建議仍會保留，而不是在失敗的重貼之前就被清掉。

行落在 diff hunk 範圍外的 finding 無法 inline 貼出，否則就會憑空消失。為了讓
總結誠實，這些 finding 會收進一個收合的 **⚠️ Outside the diff** 區塊，逐一列出
（位置＋留言）：inline finding 的數量已經說明\ *丟了幾個*\ ，而這個區塊說明\
*是哪些*\ ，讓審查者仍能手動處理。當每個 finding 都落在 diff 上時，這個區塊
會省略。

加上 ``--check-annotations``\ （環境變數 ``PRTHINKER_CHECK_ANNOTATIONS``）時，
gate 的 Check Run 還會帶逐行標註（每個 finding 一筆，依嚴重度為
``failure`` / ``warning`` / ``notice``）。它們顯示在 Files-changed 與 Checks
分頁，是 inline review 之外的\ *並行*\ 管道：單一壞行只會被個別丟棄，而不會
422 拖垮整批；且 GitHub 會跨請求累加，因此超過 50 個 finding 的審查會分成
數次更新送出。

其他輸出管道
~~~~~~~~~~~~

審查不只在 PR 對話框。aggregate job 會把合併後的 findings 寫成 **SARIF**\ （
``--sarif-out`` / ``PRTHINKER_SARIF_OUT``），workflow 再用
``github/codeql-action/upload-sarif`` 上傳,於是 findings 也會出現在
**Security 分頁**\ 與 diff 原生標註──可關閉、GitHub 還會跨 PR 去重。另外,
當 ``$GITHUB_STEP_SUMMARY`` 有設定（每次 Actions run 都有）時,at-a-glance
摘要會附加到 **run summary 頁**\ ,從 Checks 分頁就能直接看到,不必開 PR。
SARIF 與 HTML 報告（``PRTHINKER_HTML_REPORT``）都會作為 run artifact 上傳,
而總結留言結尾會帶一段 **Reports** footer,連回該 workflow run（可下載報告）
與 code scanning——讓產出的報告檔案永遠離審查只有一鍵之遙。

加上 ``--pr-body-summary``\ （環境變數 ``PRTHINKER_PR_BODY_SUMMARY``）時,
at-a-glance 摘要還會被 upsert 進 **PR 描述（body）本身**\ ,以 marker 圈起,
讓結論出現在 PR 最頂端,而非只在留言串裡。只會改寫被圈起的區塊,作者原本的
描述完整保留。

不貼部分結果
~~~~~~~~~~~~

加上 ``--require-full-scan``\ （環境變數 ``PRTHINKER_REQUIRE_FULL_SCAN``）時,
aggregate **只在 PR 的每個檔案都有結果時**\ 才貼報告。它會把 PR 的變更檔案
（扣掉 ``--exclude-globs``）與合併後 partials 已覆蓋的檔案比對;只要有缺
（例如某 shard 失敗）,就貼 ``⏳ Review in progress — N/M files scanned`` 提示,
並把選單、gate、inline review 全部押後,直到之後某次 run 覆蓋到全部檔案。
若無法取得檔案清單,則 fail-open(照常貼)。

審查進行中
~~~~~~~~~~

大型 PR 的 GPU 審查要跑數分鐘，這段期間 PR 上什麼都看不到。``post-status``
指令會在總結 marker 底下 upsert 一則 ``⏳ Review in progress…`` 佔位留言；
CI 的 ``enumerate`` job 會先跑它（best-effort），之後 aggregate 再透過同一個
marker 把它\ *對齊*\ 成真正的總結──於是審查者看到的是「已經開始審查」而非
一個空 PR。

CI 訊號 + gate 一起用
---------------------

兩個功能組合得很好：CI 訊號讓 findings 更可能包含真正的 bug（模型可以
grounding 在實際的失敗），gate 再把這些更高品質的 finding 變成硬性合併
阻擋。

更嚴的設定可以再開 ``--rules-dir``\ （團隊規則），讓模型知道你的團隊把
什麼當 error、什麼當 warning。
