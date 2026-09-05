#!/usr/bin/env python3
"""Evaluate `warn_unused_ignores` over the trees the type-check gate excludes.

`[tool.mypy] files` covers `src`, `tools` and `subprojects/docket/src`, and
every `type: ignore` in this repository sits outside that set - under `tests/`
or `subprojects/docket/tests/`. `strict = true` enables `warn_unused_ignores`,
but a directive in a file mypy never reads is not checked and found live: it is
unread. `PL-CMCB` audited the ten that existed on 2026-09-01 by hand and found
all ten live. This is what stops the eleventh going unread, and it is the
guarantee `RUF100` already gives for `noqa`, arriving through the other tool.

Widening the gate is the other way here, and `pyproject.toml`'s comment above
`files` is the standing decision against it: 54 errors across the two trees,
most of them hand-built Flet doubles and the deliberately wrong arguments the
safety-critical standard asks for. So mypy runs over those trees separately and
exactly two things are read out of its output. The other 54 pass unread.

**Two ways a naive version of this is worse than nothing.** Both report live
directives as inert, and the natural response to an inert directive is to
delete it, so a wrong answer here removes real suppressions.

- *An import that does not resolve.* Without `subprojects/docket/src` and
  `tools` on `MYPYPATH`, `docket` and `doc_check` are unresolvable, every name
  they provide degrades to `Any`, the lines using them raise nothing, and all
  six `[arg-type]` directives report as unused. Measured, not reasoned. So an
  unresolved import fails this check rather than passing quietly.
- *A disabled error code.* `--disable-error-code=arg-type` produces those same
  six false verdicts. That is why the surgical form of widening the gate - add
  `tests` to `files`, silence the noisy codes per module - cannot work at all,
  rather than merely being blunt. Nothing here disables a code: the filtering
  is applied to mypy's output, after it has run.

The incremental cache is a third hazard, met while auditing: one file edited
twice in quick succession produced a stale "no error at this line", which reads
exactly like an inert directive. Running every check with `--no-incremental`
costs 12 seconds against 0.5 warm, on every `make check`, to defend against a
case nobody has characterised. So the cache is used, and an accusation is
confirmed without it: a finding re-runs cold before it is reported. Fast when
clean, certain when it accuses, and the slow path costs nothing while the
answer stays zero.

`PL-J5NN` carries the decision and the measurements.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tokenize
from collections.abc import Sequence
from pathlib import Path

#: The trees `[tool.mypy] files` excludes, and the only place this repository
#: has ever carried a `type: ignore`.
TREES = ("tests", "subprojects/docket/tests")

#: Not optional, and not a convenience: without these, six live directives
#: report as unused. See the module docstring.
MYPY_PATH = ("subprojects/docket/src", "tools", ".claude/hooks")

#: The one finding this check exists to raise.
INERT = "[unused-ignore]"

#: Findings that invalidate the answer rather than adding to it. An unresolved
#: import degrades the names it provides to `Any`, which silences the errors
#: the directives suppress and reports them as unused.
UNSOUND = ("[import-not-found]", "[import-untyped]")

DIRECTIVE = re.compile(r"type:\s*ignore")


def directives(root: Path) -> list[str]:
    """Every real `type: ignore` comment in the checked trees, as `path:line`.

    Tokenized rather than grepped, because the string that names the directive
    is not the directive. `subprojects/docket/src/docket/verify.py` holds one in
    a tuple of suppression markers, `test_release.py` names one in prose, and
    `test_verify.py` writes one into a fixture file as a string literal. A grep
    counts all three; only a comment token is a directive.
    """
    found: list[str] = []
    for tree in TREES:
        for path in sorted((root / tree).rglob("*.py")):
            try:
                with tokenize.open(path) as handle:
                    tokens = list(tokenize.generate_tokens(handle.readline))
            except (OSError, SyntaxError, UnicodeDecodeError, tokenize.TokenError):
                # Unparseable or unreadable is not this check's finding to
                # make: mypy reports it below, against the same file.
                continue
            for token in tokens:
                if token.type == tokenize.COMMENT and DIRECTIVE.search(token.string):
                    found.append(f"{path.relative_to(root).as_posix()}:{token.start[0]}")
    return found


def run_mypy(root: Path, *, cold: bool = False) -> subprocess.CompletedProcess[str]:
    """mypy over the excluded trees, with the paths that make its answer sound.

    The trees are passed as arguments, which overrides `[tool.mypy] files`
    rather than adding to it, so the gate itself is untouched. Everything else
    in that config still applies, `strict = true` among it - which is what
    turns `warn_unused_ignores` on.

    `cold` discards the incremental cache, and is used only to confirm a
    finding: see the module docstring on why that is the shape rather than
    always or never.
    """
    extra = ("--no-incremental",) if cold else ()
    env = dict(os.environ)
    env["MYPYPATH"] = os.pathsep.join(str(root / path) for path in MYPY_PATH)
    return subprocess.run(
        (sys.executable, "-m", "mypy", *extra, *TREES),
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def report(sites: Sequence[str], returncode: int, stdout: str, stderr: str) -> tuple[int, str]:
    """The exit code and the line to print, given what mypy said.

    Pure, so the interesting cases can be tested without running mypy: an
    unresolved import, a crash, and mypy missing entirely all have to report as
    "not checked" rather than as a clean result, because a check that cannot
    tell "nothing is inert" from "nothing was read" is the failure this whole
    tool exists to avoid.
    """
    lines = stdout.splitlines()
    if returncode not in (0, 1) or (returncode == 1 and not stdout.strip()):
        detail = (stderr.strip() or stdout.strip() or "no output").splitlines()
        body = "\n".join(f"  {line}" for line in detail[:10])
        return 1, (
            f"type: ignore directives: not checked - mypy exited {returncode} without "
            f"reporting findings, so nothing was evaluated\n{body}"
        )

    unsound = [line for line in lines if any(code in line for code in UNSOUND)]
    if unsound:
        body = "\n".join(f"  {line}" for line in unsound[:10])
        return 1, (
            f"type: ignore directives: not checked - {len(unsound)} unresolved import(s). "
            "Every name an unresolved module provides degrades to `Any`, which silences "
            "the errors these directives suppress and reports live ones as unused. Fix "
            f"the import, or MYPY_PATH in this tool, before trusting any verdict\n{body}"
        )

    inert = [line for line in lines if INERT in line]
    if inert:
        body = "\n".join(f"  {line}" for line in inert)
        return 1, (
            f"type: ignore directives: {len(sites)} evaluated, {len(inert)} inert. An "
            "inert directive reads as a deliberate exemption and is not one, so a reader "
            "concludes the type checker has an opinion here when it has never objected. "
            f"Delete it, or fix what it was meant to suppress\n{body}"
        )

    return 0, f"type: ignore directives: {len(sites)} evaluated, 0 inert"


def accuses(printed: str) -> bool:
    """Does this report name an inert directive, as opposed to passing or failing?"""
    return " inert. " in printed


def evaluate(root: Path) -> tuple[int, str]:
    """The check, including the cold re-run that confirms a finding.

    A clean tree is answered from the incremental cache and never pays for the
    second run. Only an accusation does, and an accusation that the cold run
    does not reproduce was the cache talking rather than the code.
    """
    result = run_mypy(root)
    sites = directives(root)
    code, printed = report(sites, result.returncode, result.stdout, result.stderr)
    if not accuses(printed):
        return code, printed
    confirmed = run_mypy(root, cold=True)
    return report(sites, confirmed.returncode, confirmed.stdout, confirmed.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    args = parser.parse_args(argv)

    code, printed = evaluate((args.root or Path(__file__).resolve().parent.parent).resolve())
    print(printed)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
