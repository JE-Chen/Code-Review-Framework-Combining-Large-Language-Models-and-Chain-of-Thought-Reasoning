Cache 與 telemetry
==================

兩份可選的 SQLite store 夾在 pipeline 與 backend 之間。彼此獨立──開一個
不需要開另一個──並在 factory 階段以 Decorator 形式包在實際 backend 之外。

Cache（\ ``--cache``\ ）
-------------------------

Read-through cache，key 是
``backend_kind | model | prompt | max_new_tokens`` 的 SHA-256。因為 prompt
文本本身就是 key 的一部分，\ **prompt template 改動、模型換掉、token cap
調整都會自動 invalidate cache**\ ──不需要手動 bust。

預設：

* 路徑：\ ``.prthinker/cache.sqlite``\ 。
* TTL：7 天（\ ``--cache-ttl-days`` 覆寫；\ ``0`` 關閉 TTL）。
* 啟用 WAL 模式，並發讀不會被擋。

Cache 是 process-local 的、純 ``sqlite3``\ （stdlib）──不需要外部服務。

什麼時候要開
~~~~~~~~~~~~

付費 provider 一律建議開；跑幾次 PR 之後 hit rate 通常會到 60–90%──大多數
檔案在兩次推送之間不會變。本機 backend 也有用（``synchronize`` 推送沒動
到某檔時可以省 GPU），只是因為生成「免費」所以收益較小。

Telemetry（\ ``--telemetry``\ ）
---------------------------------

Append-only ``calls`` 表，每次 ``generate()`` 一筆：

* ``timestamp``\ （unix）
* ``backend`` / ``model``
* ``prompt_tokens`` + ``completion_tokens``\ （有 provider 的 ``usage``
  block 時直接取；沒有時用 char count 估算──見 ``tokens_estimated`` 欄）
* ``latency_ms``
* ``cost_usd``\ （由 :mod:`prthinker.pricing` 計算；本機與自架 remote
  backend 為 ``NULL``\ ）
* ``cache_hit``\ （上游 ``CachingBackend`` 命中時為 1）
* ``error``\ （上游拋例外時填；成功為 ``NULL``\ ）

Pricing
~~~~~~~

:mod:`prthinker.pricing` 是 ``(backend, model) → (input_rate, output_rate)``
的靜態表，單位 USD 每百萬 token。表中沒有的型號回 ``None``──這一筆會
記下來但 ``cost_usd`` 留空，方便事後抓 provider 改價漂移。

``stats`` subcommand
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   prthinker stats                       # 全時段
   prthinker stats --since-days 7        # 過去一週
   prthinker stats --since-days 1        # 過去 24 小時

輸出範例見英文版 :doc:`../../en/concepts/cache-and-telemetry`。

為什麼這個重要
~~~~~~~~~~~~~~

接 paid API 之後，「Claude Opus 真的值得比 gpt-4o-mini 多 25 倍嗎？」會
變成一個實在的問題。Telemetry 表讓你不必手動 instrument 就答得出來，
cache 那一欄則告訴你把 workflow trigger 從 ``push`` 改成 ``synchronize``
能不能有意義地砍 bill。

Wrapping 順序
-------------

:func:`prthinker.backends.create_backend` 內 factory 的 wrapper stacking
順序是::

   InstrumentedBackend(CachingBackend(real_backend))

這樣 telemetry 層能正確看到 ``cache_hit=true``\ ，同時仍記到 cache lookup
本身（極短）的 latency。

關閉
----

兩個 wrapper 都是 flag + env var 開關，預設 **off**\ ：

* ``--cache`` / ``PRTHINKER_CACHE_ENABLED``
* ``--telemetry`` / ``PRTHINKER_TELEMETRY_ENABLED``

關閉時 factory 直接回 concrete backend──不寫 disk、沒有 schema migration
風險。
