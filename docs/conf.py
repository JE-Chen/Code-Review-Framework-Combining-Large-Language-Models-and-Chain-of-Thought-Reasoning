"""Sphinx configuration for the prthinker documentation."""

from __future__ import annotations

import sys
from pathlib import Path

# Make the package importable so autodoc can introspect signatures.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

# -- Project information -----------------------------------------------------

project = "prthinker"
author = "JeffreyChen"
copyright = "2026, JeffreyChen"

try:
    from prthinker import __version__ as release  # noqa: WPS433
except Exception:
    release = "0.1.0"

version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# Use the first heading on a page as the document title.
master_doc = "index"

# -- HTML output -------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "prthinker"
html_show_sphinx = False
html_theme_options = {
    "navigation_depth": 3,
    "collapse_navigation": False,
    "sticky_navigation": True,
}

# -- Autodoc -----------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_member_order = "bysource"

# -- Napoleon (Google-style docstrings) --------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False

# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
}

# -- Copybutton --------------------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ |# "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False
