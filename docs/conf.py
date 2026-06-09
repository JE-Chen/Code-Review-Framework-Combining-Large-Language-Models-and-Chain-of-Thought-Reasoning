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
copyright = "2026, JeffreyChen"  # pylint: disable=redefined-builtin  # Sphinx-required config name

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
    "sphinxcontrib.mermaid",
]

# Mermaid renders client-side via mermaid.js for the HTML builder. The PDF
# (LaTeX) builder would otherwise need the mermaid-cli (mmdc) binary, which
# is not available on Read the Docs — so every ``.. mermaid::`` block is
# wrapped in ``.. only:: html`` with a plain-text fallback under
# ``.. only:: latex``. This keeps both the HTML and the PDF formats building
# without an extra system dependency.

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

# -- LaTeX / PDF output ------------------------------------------------------
# This documentation set mixes English, Traditional Chinese, and Simplified
# Chinese. pdflatex cannot render CJK without third-party packages; XeLaTeX
# with xeCJK + Noto CJK fonts handles all three without per-language
# preprocessing. The apt_packages installed by .readthedocs.yaml
# (texlive-xetex + fonts-noto-cjk + texlive-lang-chinese) and the
# latexmkrc at the repo root ($pdf_mode = 5) make this configuration
# build end-to-end on Read the Docs.

latex_engine = "xelatex"

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "figure_align": "H",
    "fontpkg": "",
    "fncychap": "",
    "preamble": r"""
\usepackage{fontspec}
\usepackage{xeCJK}

\setmainfont{Noto Serif}[Scale=1.0]
\setsansfont{Noto Sans}[Scale=1.0]
\setmonofont{Noto Sans Mono}[Scale=0.9]

% Noto CJK TC covers Simplified Chinese codepoints too, so a single
% face renders both zh-TW and zh-CN sections.
\setCJKmainfont{Noto Serif CJK TC}[Scale=1.0]
\setCJKsansfont{Noto Sans CJK TC}[Scale=1.0]
\setCJKmonofont{Noto Sans Mono CJK TC}[Scale=0.9]

% Allow line breaks between Latin and CJK runs without hyphenation.
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 1pt
""",
}

latex_documents = [
    ("index", "code-review-framework.tex",
     "Code Review Framework documentation",
     "JeffreyChen", "manual"),
]
latex_show_urls = "footnote"
