"""Vercel serverless entrypoint for the GoalCoach API.

Vercel maps ``api/[...path].py`` to ``/api/*``, so the FastAPI app registered
here receives the original request path unchanged. The frontend build is served
as static output from ``apps/web/dist`` and never reaches this function.

The repository root and ``src/`` are put on ``sys.path`` first because Vercel
only pip-installs the ``goalcoach`` package, while ``apps`` is a source tree
that is not part of the wheel.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

for _entry in (_ROOT, _ROOT / "src"):
    if str(_entry) not in sys.path:
        sys.path.insert(0, str(_entry))

from apps.api.main import app

__all__ = ["app"]
