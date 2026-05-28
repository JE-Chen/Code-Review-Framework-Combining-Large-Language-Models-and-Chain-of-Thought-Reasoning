Python API
==========

套件公開的 API 面積小而穩定。下列項目都會從 ``prthinker`` re-export，
所以 ``from prthinker import X`` 是常見用法。

頂層套件
--------

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

規則包
------

.. automodule:: prthinker.rules
   :no-index:
   :members:

學習語料
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

CI 訊號
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

GitHub 整合
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
