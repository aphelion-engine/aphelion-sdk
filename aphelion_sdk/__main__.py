"""Allow ``python -m aphelion_sdk`` to invoke the packaging CLI."""

from __future__ import annotations

import sys

from aphelion_sdk.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
