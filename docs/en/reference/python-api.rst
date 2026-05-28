Python API
==========

The package exposes a stable, small public surface. Everything below is
re-exported from ``reviewmind`` so the common ``from reviewmind
import X`` works.

Top-level package
-----------------

.. automodule:: reviewmind
   :members:
   :no-index:

Config
------

.. automodule:: reviewmind.config
   :members:
   :show-inheritance:

Backends (Strategy)
-------------------

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

RAG (Repository)
----------------

.. automodule:: reviewmind.rag
   :members:
   :show-inheritance:

Steps (Registry + Template Method)
----------------------------------

.. automodule:: reviewmind.steps
   :members:
   :show-inheritance:

Pipeline
--------

.. automodule:: reviewmind.pipeline
   :members:
   :show-inheritance:

Diff parsing
------------

.. automodule:: reviewmind.diff
   :members:
   :show-inheritance:

Findings extraction
-------------------

.. automodule:: reviewmind.findings
   :members:
   :show-inheritance:

Rule packs
----------

.. automodule:: reviewmind.rules
   :members:

Learned corpora
---------------

.. automodule:: reviewmind.dismissed
   :members:
   :show-inheritance:

.. automodule:: reviewmind.accepted
   :members:
   :show-inheritance:

Harvesters
----------

.. automodule:: reviewmind.harvest
   :members:

CI signals
----------

.. automodule:: reviewmind.ci_signals
   :members:
   :show-inheritance:

Checks API gate
---------------

.. automodule:: reviewmind.checks
   :members:
   :show-inheritance:

GitHub integration
------------------

.. automodule:: reviewmind.github_api
   :members:

Formatters
----------

.. automodule:: reviewmind.formatters
   :members:

Schemas
-------

.. automodule:: reviewmind.schemas
   :members:
   :show-inheritance:
