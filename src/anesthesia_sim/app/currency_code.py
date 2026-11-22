"""State the rules for a currency code, and for how many decimals its amounts show.

`PL-93B3` and `PL-1P15` set the first rule, and `PL-7R8S` the second.

`docs/INTERFACE.md` § "A cost at the reader's price" says that a price's currency
is stored and shown as its ISO 4217 alphabetic code. It is never shown as a
sign such as "$" that several currencies share. The store refuses a code that
is not three capital letters, and the formatters refuse to print one. Both
read the rule here, so they cannot disagree about it. The code is not checked
against the list of codes ISO 4217 assigns, for the reason `app/preferences.py`
gives.

A cost is shown to its currency's minor unit, such as the cent
(`docs/INTERFACE.md` § "Agent amounts in millilitres, and the cost"). The count
of decimals comes from the Unicode CLDR's currency data, read through Babel,
and this is the only module that imports Babel.
"""

from __future__ import annotations

import re
from typing import Final

from babel.numbers import get_currency_precision

__all__ = ["is_currency_code", "minor_unit_decimals"]

# regex: three capital letters, the form of an ISO 4217 alphabetic code. `[A-Z]`
# in Python's `re` matches only the 26 ASCII capitals. The pattern checks only
# the shape, so a code that ISO 4217 does not assign, such as QQQ, passes. The
# module docstring says why that is enough.
_CURRENCY_CODE_PATTERN: Final = re.compile(r"[A-Z]{3}")


def is_currency_code(text: str) -> bool:
    """Return whether `text` is three capital letters, the form of an ISO 4217 code."""

    return _CURRENCY_CODE_PATTERN.fullmatch(text) is not None


def minor_unit_decimals(currency: str) -> int:
    """Return how many decimals an amount in `currency` is shown to: 2 for USD, 0 for JPY.

    The count is the `digits` that CLDR's currency data gives the currency.
    CLDR bases it on the minor unit that ISO 4217 lists, and departs from
    ISO 4217 only where customary use differs. A code that CLDR does not list,
    such as a mistyped `UDS`, gets CLDR's default of 2 (Unicode Technical
    Standard #35, Part 3, Numbers, section "Currency Fraction Digits and Rounding",
    https://www.unicode.org/reports/tr35/tr35-numbers.html). Babel's
    `get_currency_precision` applies that default for an unlisted code. CLDR's
    separate figures for cash, such as rounding Swiss francs to 0.05, are not
    used, because a cost is not paid in cash.

    The caller checks the code's form with `is_currency_code` first. This
    function does not refuse a code of another form.
    """

    return get_currency_precision(currency)
