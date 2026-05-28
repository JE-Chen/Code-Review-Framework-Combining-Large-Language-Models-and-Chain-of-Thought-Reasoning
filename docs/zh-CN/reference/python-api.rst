Python API
==========

包公开的 API 面积小而稳定。下列项目都会从 ``reviewmind`` re-export，
所以 ``from reviewmind import X`` 是常见用法。

顶层包
------

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

规则包
------

.. automodule:: reviewmind.rules
   :no-index:
   :members:

学习语料
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

CI 信号
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

GitHub 集成
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
