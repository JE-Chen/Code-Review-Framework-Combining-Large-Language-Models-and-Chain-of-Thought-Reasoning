"""Third-party review-step plugin loader via entry points.

Distributions can ship their own `ReviewStep` subclasses and advertise them
under the ``prthinker.steps`` entry-point group. Importing the loaded object
is expected to trigger ``@register_step`` (see :mod:`prthinker.steps`), so the
loader's only job is to import each entry point and report which ones loaded.

A single failing entry point (bad import, broken third-party package) must not
abort discovery of the others — it is logged and skipped. Pure stdlib, so this
module is runner-safe.
"""

from __future__ import annotations

import logging
from importlib import metadata

_LOG = logging.getLogger(__name__)

#: Entry-point group third-party packages advertise review steps under.
PLUGIN_STEPS_GROUP = "prthinker.steps"


def load_plugin_steps() -> list[str]:
    """Import every ``prthinker.steps`` entry point and return loaded names.

    Each loaded object is expected to self-register via ``@register_step`` on
    import. A single entry point that fails to load is logged and skipped so
    the remaining plugins still load.
    """
    loaded: list[str] = []
    for entry_point in metadata.entry_points(group=PLUGIN_STEPS_GROUP):
        try:
            entry_point.load()
        except (ImportError, AttributeError, ValueError) as err:
            _LOG.warning(
                "Skipping review-step plugin %r: %s", entry_point.name, err
            )
            continue
        loaded.append(entry_point.name)
    return loaded
