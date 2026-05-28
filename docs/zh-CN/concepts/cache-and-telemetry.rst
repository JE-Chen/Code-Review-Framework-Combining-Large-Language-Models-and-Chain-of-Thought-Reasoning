Cache 与 telemetry
==================

两份可选的 SQLite store 夹在 pipeline 与 backend 之间。彼此独立──开一个
不需要开另一个──并在 factory 阶段以 Decorator 形式包在实际 backend 之外。

Cache（\ ``--cache``\ ）
-------------------------

Read-through cache，key 是
``backend_kind | model | prompt | max_new_tokens`` 的 SHA-256。因为 prompt
文本本身就是 key 的一部分，\ **prompt template 改动、模型换掉、token cap
调整都会自动 invalidate cache**\ ──不需要手动 bust。

默认：

* 路径：\ ``.reviewmind/cache.sqlite``\ 。
* TTL：7 天（\ ``--cache-ttl-days`` 覆盖；\ ``0`` 关闭 TTL）。
* 启用 WAL 模式，并发读不会被挡。

Cache 是 process-local 的、纯 ``sqlite3``\ （stdlib）──不需要外部服务。

什么时候要开
~~~~~~~~~~~~

付费 provider 一律建议开；跑几次 PR 之后 hit rate 通常会到 60–90%──大多数
文件在两次推送之间不会变。本地 backend 也有用（\ ``synchronize`` 推送没动
到某文件时可以省 GPU），只是因为生成「免费」所以收益较小。

Telemetry（\ ``--telemetry``\ ）
---------------------------------

Append-only ``calls`` 表，每次 ``generate()`` 一条记录：

* ``timestamp``\ （unix）
* ``backend`` / ``model``
* ``prompt_tokens`` + ``completion_tokens``\ （有 provider 的 ``usage``
  block 时直接取；没有时用 char count 估算──见 ``tokens_estimated`` 列）
* ``latency_ms``
* ``cost_usd``\ （由 :mod:`reviewmind.pricing` 计算；本地与自建 remote
  backend 为 ``NULL``\ ）
* ``cache_hit``\ （上游 ``CachingBackend`` 命中时为 1）
* ``error``\ （上游抛异常时填；成功为 ``NULL``\ ）

Pricing
~~~~~~~

:mod:`reviewmind.pricing` 是 ``(backend, model) → (input_rate, output_rate)``
的静态表，单位 USD 每百万 token。表中没有的型号返回 ``None``──这一条会
记录但 ``cost_usd`` 留空，方便事后抓 provider 改价漂移。

``stats`` subcommand
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   reviewmind stats                       # 全时段
   reviewmind stats --since-days 7        # 过去一周
   reviewmind stats --since-days 1        # 过去 24 小时

输出示例见英文版 :doc:`../../en/concepts/cache-and-telemetry`。

为什么这个重要
~~~~~~~~~~~~~~

接 paid API 之后，「Claude Opus 真的值得比 gpt-4o-mini 多 25 倍吗？」会
变成一个实在的问题。Telemetry 表让你不必手动 instrument 就答得出来，
cache 那一列则告诉你把 workflow trigger 从 ``push`` 改成 ``synchronize``
能不能有意义地砍 bill。

Wrapping 顺序
-------------

:func:`reviewmind.backends.create_backend` 内 factory 的 wrapper stacking
顺序是::

   InstrumentedBackend(CachingBackend(real_backend))

这样 telemetry 层能正确看到 ``cache_hit=true``\ ，同时仍记到 cache lookup
本身（极短）的 latency。

关闭
----

两个 wrapper 都是 flag + env var 开关，默认 **off**\ ：

* ``--cache`` / ``REVIEWMIND_CACHE_ENABLED``
* ``--telemetry`` / ``REVIEWMIND_TELEMETRY_ENABLED``

关闭时 factory 直接返回 concrete backend──不写 disk、没有 schema migration
风险。
