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
   :members:
   :show-inheritance:

Backends（Strategy）
--------------------

.. automodule:: reviewmind.backends.base
   :members:
   :show-inheritance:

.. automodule:: reviewmind.backends.local
   :members:
   :show-inheritance:

.. automodule:: reviewmind.backends.remote
   :members:
   :show-inheritance:

.. autofunction:: reviewmind.backends.create_backend

RAG（Repository）
-----------------

.. automodule:: reviewmind.rag
   :members:
   :show-inheritance:

Steps（Registry + Template Method）
-----------------------------------

.. automodule:: reviewmind.steps
   :members:
   :show-inheritance:

Pipeline
--------

.. automodule:: reviewmind.pipeline
   :members:
   :show-inheritance:

Diff 解析
---------

.. automodule:: reviewmind.diff
   :members:
   :show-inheritance:

Findings 解析
-------------

.. automodule:: reviewmind.findings
   :members:
   :show-inheritance:

規則包
------

.. automodule:: reviewmind.rules
   :members:

學習語料
--------

.. automodule:: reviewmind.dismissed
   :members:
   :show-inheritance:

.. automodule:: reviewmind.accepted
   :members:
   :show-inheritance:

Harvester
---------

.. automodule:: reviewmind.harvest
   :members:

CI 訊號
-------

.. automodule:: reviewmind.ci_signals
   :members:
   :show-inheritance:

Checks API gate
---------------

.. automodule:: reviewmind.checks
   :members:
   :show-inheritance:

GitHub 整合
-----------

.. automodule:: reviewmind.github_api
   :members:

Formatter
---------

.. automodule:: reviewmind.formatters
   :members:

Schemas
-------

.. automodule:: reviewmind.schemas
   :members:
   :show-inheritance:
