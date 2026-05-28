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

规则包
------

.. automodule:: reviewmind.rules
   :members:

学习语料
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

CI 信号
-------

.. automodule:: reviewmind.ci_signals
   :members:
   :show-inheritance:

Checks API gate
---------------

.. automodule:: reviewmind.checks
   :members:
   :show-inheritance:

GitHub 集成
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
