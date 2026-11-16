"""State the one rule for what a currency code must look like (`PL-93B3`, `PL-1P15`).

`docs/INTERFACE.md` § "A cost at the reader's price" says that a price's currency
is stored and shown as its ISO 4217 alphabetic code. It is never shown as a
sign such as "$" that several currencies share. The store refuses a code that
is not three capital letters, and the formatters refuse to print one. Both
read the rule here, so they cannot disagree about it. The code is not checked
against the list of codes ISO 4217 assigns, for the reason `app/preferences.py`
gives.
"""

from __future__ import annotations

import re
from typing import Final

__all__ = ["is_currency_code"]

# Three capital letters, the form of an ISO 4217 alphabetic code. `[A-Z]` in
# Python's `re` matches only the 26 ASCII capitals.
_CURRENCY_CODE_PATTERN: Final = re.compile(r"[A-Z]{3}")


def is_currency_code(text: str) -> bool:
    """Return whether `text` is three capital letters, the form of an ISO 4217 code."""

    return _CURRENCY_CODE_PATTERN.fullmatch(text) is not None
