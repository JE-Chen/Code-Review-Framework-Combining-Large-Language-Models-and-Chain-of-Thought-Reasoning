Python API
==========

The package exposes a stable, small public surface. Everything below is
re-exported from ``prthinker`` so the common ``from prthinker
import X`` works.

Top-level package
-----------------

.. automodule:: prthinker
   :members:
   :no-index:

Config
------

.. automodule:: prthinker.config
   :members:
   :show-inheritance:

Backends (Strategy)
-------------------

.. automodule:: prthinker.backends.base
   :members:
   :show-inheritance:

.. automodule:: prthinker.backends.local
   :members:
   :show-inheritance:

.. automodule:: prthinker.backends.remote
   :members:
   :show-inheritance:

.. autofunction:: prthinker.backends.create_backend

RAG (Repository)
----------------

.. automodule:: prthinker.rag
   :members:
   :show-inheritance:

Steps (Registry + Template Method)
----------------------------------

.. automodule:: prthinker.steps
   :members:
   :show-inheritance:

Pipeline
--------

.. automodule:: prthinker.pipeline
   :members:
   :show-inheritance:

Diff parsing
------------

.. automodule:: prthinker.diff
   :members:
   :show-inheritance:

Findings extraction
-------------------

.. automodule:: prthinker.findings
   :members:
   :show-inheritance:

Rule packs
----------

.. automodule:: prthinker.rules
   :members:

Learned corpora
---------------

.. automodule:: prthinker.dismissed
   :members:
   :show-inheritance:

.. automodule:: prthinker.accepted
   :members:
   :show-inheritance:

Harvesters
----------

.. automodule:: prthinker.harvest
   :members:

CI signals
----------

.. automodule:: prthinker.ci_signals
   :members:
   :show-inheritance:

Checks API gate
---------------

.. automodule:: prthinker.checks
   :members:
   :show-inheritance:

GitHub integration
------------------

.. automodule:: prthinker.github_api
   :members:

Formatters
----------

.. automodule:: prthinker.formatters
   :members:

Schemas
-------

.. automodule:: prthinker.schemas
   :members:
   :show-inheritance:
