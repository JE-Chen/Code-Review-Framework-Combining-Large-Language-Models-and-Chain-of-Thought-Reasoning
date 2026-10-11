評估與整合
============================================================

實作支援 Python 3.10–3.14。依使用者要求，暫不進行模型實測；離線測試不能證明 benchmark 品質，也不能取代正式 1.0 的發布證據。

Benchmark 封存複製原始案例、固定雜湊與順序、逐案寫入結果，保留失敗與不支援狀態，彙整前驗證雜湊。資料集 manifest 必須包含 dataset、HTTPS url、revision、license、source_sha256 與 cases_sha256。控制條件應固定權重 revision、adapter 狀態、精度、審查步驟、解碼模式與 max_new_tokens。解析後的組態不含憑證；完整審查保存實際檢索文件數，未知 token 用量及費用保留 null。

對抗 v1 語料涵蓋六類攻擊及良性對照。文字標記分數只是攻擊成功、偵測、拒絕與問題涵蓋的啟發式代理指標，並非獨立裁決或已執行的不安全動作。17 項單因子條件共用固定控制與案例順序，各條件獨立複製資料庫與工作目錄；缺少必要 fixture 時明確記為不支援。客觀 precision／recall／F1 的成對差異附 bootstrap 區間、效果量、雙尾 Wilcoxon 與全比較族群 Holm 校正，不能替代模型裁判分數。歷史 44 案是「模型產生參考問題集」，不是人工黃金標準。

摘要輸入為含 diff 及選填 title、body、commits 的 JSON，獨立於審查 findings。只有 --publish-summary 才更新具有標記的摘要留言。知識圖譜保留 Python／JS／TS 掃描，可選用 Tree-sitter 支援 Java、Go、Rust、C／C++、C# 與 Kotlin；無法確定或有歧義的匯入不建立連結。

自主修復要求測試，使用可拋棄 worktree，限制重試、生成呼叫、時間、檔案數與 patch 大小，並執行修復後審查。稽核與遮蔽敏感內容的 patch 在清理後仍保留。--open-pr 建立待人工核准合併的草稿。驗證預設使用固定 digest 的 Docker 映像；本機執行需明確指定 --allow-unsandboxed。

品質事件只接受允許的指標與互動識別碼，使用至少 32 bytes 的 PRTHINKER_QUALITY_KEY 假名化。接受、忽略、套用、轉 issue、回歸、重開是操作訊號；未知費用不能當作實測估算。操作者管理保存期限與事件匯入。

IDE 標準輸入／輸出採 JSONL protocol_version 1，使用唯一 request_id，支援 review／cancel／apply_patch／verify，回傳進度、finding、patch 建議、驗證及終止事件。套用 patch 要求明確核准、原檔 SHA-256 一致與儲存庫相對路徑。JEditor／PyBreeze 使用隔離子行程，將結果放入 Problems 並提供 Quick Fix。需一起安裝編輯器變更，並在所選直譯器安裝本套件。協定不會自動發布或合併。

正式發布要求完整且雜湊驗證通過的公開、對抗及消融結果，以及實作、安裝與文件檢查。通過前版本維持 0.1.0。詳見 benchmarks/README.md 與 release/evidence.json。

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


發布流程先由 scripts/prepare_release.py 驗證證據，再同步套件、模組與引用版本至完全一致的 tag 後建置。離線驗證可使用 scripts/verify_implementation.py OUTPUT --minimum-python PYTHON310 重現；可選語法套件的探針為 scripts/probe_polyglot.py。

符號等級檢定在非零成對差異不超過 50 對時使用條件式精確推論，涵蓋 44 案參考集；更大的樣本使用考慮同級與連續性校正的常態近似，並逐項記錄方法。

協定輸入與輸出固定使用 UTF-8，支援舊版 Windows 編碼環境中的中文路徑。
