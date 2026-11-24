"""Sphinx configuration. Builds run with -W -n, so every warning fails them."""

from folio_reports import __version__

project = "Folio Reports"
author = "Agustín Sellanes"
release = __version__
version = __version__

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]
exclude_patterns = ["_build"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

autodoc_member_order = "bysource"
autodoc_typehints = "description"
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_ivar = True

nitpicky = True
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

html_theme = "pydata_sphinx_theme"
html_title = project
html_theme_options = {
    "github_url": "https://github.com/EssenceSentry/folio-reports",
    "navigation_with_keys": False,
}
