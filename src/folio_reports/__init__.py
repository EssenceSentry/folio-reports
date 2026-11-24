"""Typeset decision briefs and research reports from Markdown."""

from importlib.metadata import PackageNotFoundError, version

from folio_reports.core import build, new

try:
    __version__ = version("folio-reports")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["__version__", "build", "new"]
