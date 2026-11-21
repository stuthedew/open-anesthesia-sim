"""The regular expressions the tree held without a reason when `tools/regex_check.py` landed.

Each entry is a file, then the enclosing function or class and the function
called, then how many such calls that place holds. `tools/regex_check.py`
fails on a count above its entry and on an entry the tree no longer fills, so
this table only shrinks. Lower or delete an entry in the change that removes a
call or gives it a `regex:` reason. Never add one: a new call carries its
reason beside it instead.

Taken on 2026-11-03 (`PL-7JYV`): 346 calls in 73 files, under 126 keys.
`PL-3WFF` reviewed the six under `src/` and `PL-8FT2` reviewed the rest. Each
call was replaced by a parser or a string method, or kept with its reason
beside it, so the table is empty.
"""

GRANDFATHERED_REGEX: dict[str, dict[tuple[str, str], int]] = {}
