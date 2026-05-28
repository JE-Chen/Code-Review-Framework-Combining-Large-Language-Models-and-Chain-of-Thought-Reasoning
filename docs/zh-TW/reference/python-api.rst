Python API
==========

套件公開的 API 面積小而穩定。下列項目都會從 ``reviewmind`` re-export，
所以 ``from reviewmind import X`` 是常見用法。

頂層套件
--------

.. automodule:: reviewmind
   :members:
   :no-index:

Config
------

.. automodule:: reviewmind.config
   :no-index:
   :members:
   :show-inheritance:

Backends（Strategy）
--------------------

.. automodule:: reviewmind.backends.base
   :no-index:
   :members:
   :show-inheritance:

.. automodule:: reviewmind.backends.local
   :no-index:
   :members:
   :show-inheritance:

.. automodule:: reviewmind.backends.remote
   :no-index:
   :members:
   :show-inheritance:

.. autofunction:: reviewmind.backends.create_backend
   :no-index:

RAG（Repository）
-----------------

.. automodule:: reviewmind.rag
   :no-index:
   :members:
   :show-inheritance:

Steps（Registry + Template Method）
-----------------------------------

.. automodule:: reviewmind.steps
   :no-index:
   :members:
   :show-inheritance:

Pipeline
--------

.. automodule:: reviewmind.pipeline
   :no-index:
   :members:
   :show-inheritance:

Diff 解析
---------

.. automodule:: reviewmind.diff
   :no-index:
   :members:
   :show-inheritance:

Findings 解析
-------------

.. automodule:: reviewmind.findings
   :no-index:
   :members:
   :show-inheritance:

規則包
------

.. automodule:: reviewmind.rules
   :no-index:
   :members:

學習語料
--------

.. automodule:: reviewmind.dismissed
   :no-index:
   :members:
   :show-inheritance:

.. automodule:: reviewmind.accepted
   :no-index:
   :members:
   :show-inheritance:

Harvester
---------

.. automodule:: reviewmind.harvest
   :no-index:
   :members:

CI 訊號
-------

.. automodule:: reviewmind.ci_signals
   :no-index:
   :members:
   :show-inheritance:

Checks API gate
---------------

.. automodule:: reviewmind.checks
   :no-index:
   :members:
   :show-inheritance:

GitHub 整合
-----------

.. automodule:: reviewmind.github_api
   :no-index:
   :members:

Formatter
---------

.. automodule:: reviewmind.formatters
   :no-index:
   :members:

Schemas
-------

.. automodule:: reviewmind.schemas
   :no-index:
   :members:
   :show-inheritance:
