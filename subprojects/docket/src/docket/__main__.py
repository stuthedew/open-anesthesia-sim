"""Entry point, so `python -m docket` works from a bare checkout."""

from .cli import main

raise SystemExit(main())
