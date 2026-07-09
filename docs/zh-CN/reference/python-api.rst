Python API
==========

包公开的 API 面积小而稳定。下列项目都会从 ``prthinker`` re-export，
所以 ``from prthinker import X`` 是常见用法。

顶层包
------

.. automodule:: prthinker
   :members:
   :no-index:

Config
------

.. automodule:: prthinker.config
   :no-index:
   :members:
   :show-inheritance:

Backends（Strategy）
--------------------

.. automodule:: prthinker.backends.base
   :no-index:
   :members:
   :show-inheritance:

.. automodule:: prthinker.backends.local
   :no-index:
   :members:
   :show-inheritance:

.. automodule:: prthinker.backends.remote
   :no-index:
   :members:
   :show-inheritance:

.. autofunction:: prthinker.backends.create_backend
   :no-index:

RAG（Repository）
-----------------

.. automodule:: prthinker.rag
   :no-index:
   :members:
   :show-inheritance:

Steps（Registry + Template Method）
-----------------------------------

.. automodule:: prthinker.steps
   :no-index:
   :members:
   :show-inheritance:

Pipeline
--------

.. automodule:: prthinker.pipeline
   :no-index:
   :members:
   :show-inheritance:

Diff 解析
---------

.. automodule:: prthinker.diff
   :no-index:
   :members:
   :show-inheritance:

Findings 解析
-------------

.. automodule:: prthinker.findings
   :no-index:
   :members:
   :show-inheritance:

规则包
------

.. automodule:: prthinker.rules
   :no-index:
   :members:

学习语料
--------

.. automodule:: prthinker.dismissed
   :no-index:
   :members:
   :show-inheritance:

.. automodule:: prthinker.accepted
   :no-index:
   :members:
   :show-inheritance:

Harvester
---------

.. automodule:: prthinker.harvest
   :no-index:
   :members:

.. automodule:: prthinker.gitlab_harvest
   :no-index:
   :members:

CI 信号
-------

.. automodule:: prthinker.ci_signals
   :no-index:
   :members:
   :show-inheritance:

Checks API gate
---------------

.. automodule:: prthinker.checks
   :no-index:
   :members:
   :show-inheritance:

GitHub 集成
-----------

.. automodule:: prthinker.github_api
   :no-index:
   :members:

Formatter
---------

.. automodule:: prthinker.formatters
   :no-index:
   :members:

Schemas
-------

.. automodule:: prthinker.schemas
   :no-index:
   :members:
   :show-inheritance:
