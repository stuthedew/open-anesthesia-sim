"""Refuse a `README.md` at the repository root, which the project owner deleted.

The rule is exact and needs no judgment: **no file named `README.md` at the
repository root.** It is therefore a hard error rather than an advisory. Only
the root is covered - `subprojects/docket/README.md` (the queue tool's manual)
and `docs/references/README.md` are apparatus, were never in scope, and the
unanchored-name mistake that once let a rule about "README.md" reach all three
is `PL-ZQ35`.

**Why the file is gone.** The project owner deleted it on 2026-09-05
(`PL-WB5K`), on the finding that it was doing net harm in two directions at
once. Sessions read it as instruction: its "Development" section restated the
Makefile, `make check`'s composition and the CI job layout, so a second copy of
that material sat where a session would find it first, and no check held it to
the tree. For a human reader it had become 241 lines of separately-improved
paragraphs with no shape - the accumulation `PL-QTN6` had already recorded.

**Why a check rather than prose.** `PL-QTN6` tried the gentler remedy first: a
`.claude/rules/` freeze on editing the file. A path-scoped rule loads when a
session *reads* a matching file, and a first write is preceded by no read, so
the freeze was best-effort by construction - `PL-BTSW` records it being missed
one day after it was written, and `PL-3V4N` diagnosed why. This is the same
rule routed to the one disposition that cannot be missed. It is also cheap in
the way `CLAUDE.md` asks a check to be: silent on every run where nothing is
wrong, so it costs no attention until it has something to say.

**A stub is the failure, not an exception to it.** Half a README is still read
as instruction, still drifts, and still turns `PL-N092` (rewrite README as a
human-readable introduction) from a first draft into a revision of a document
nobody designed. `PL-N092` is sequenced behind `PL-XYRN` (decide when the
repository goes public, and run the human-facing pass immediately before it),
which is what "until" means here.

**It retires itself.** `PL-N092` deletes this file, and its two invocations in
`Makefile` and `.github/workflows/quality.yml`, in the commit that writes the
deliberate README - so the hold ends with nothing left behind to remember to
remove, which is what `CLAUDE.md` asks of a check that has stopped earning its
place. In CI it sits in the bare-interpreter section of the `checks` job, which
runs before `uv` is installed; `PL-D551` folded the former `floor` job in
there, so that section is where a standard-library tool belongs.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HELD = "README.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()

    if not (args.root / HELD).exists():
        print(f"readme-hold: no {HELD} at the repository root, as intended")
        return 0

    print(
        f"readme-hold: {HELD} exists at the repository root.\n"
        "  The project owner deleted it on 2026-09-05 (`PL-WB5K`) because sessions were "
        "reading it as instruction and a human reader could not use it. It stays deleted - "
        "a stub included - until `PL-N092` writes a deliberate one, which is sequenced "
        "behind `PL-XYRN` (decide when the repository goes public).\n"
        '  Record what you wanted it to say with `bin/docket new "..."` instead. If the '
        "owner has lifted the hold, delete `tools/readme_hold_check.py` and its two "
        "invocations in the same commit that writes the README.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
