"""Shared result reporting for the review-verification scripts.

Each check reports one of four states so that a later reader - human or
agent - can tell at a glance whether a reviewed claim still holds against
the current working tree, rather than having to interpret raw numbers.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

CONFIRMED = "CONFIRMED"
REGRESSED = "REGRESSED"
REPRODUCED = "REPRODUCED"
FIXED = "FIXED"

_LABEL_WIDTH = 62


@dataclass(slots=True)
class Report:
    """Collect check results and summarise them for an exit code."""

    title: str
    results: list[tuple[str, str, str]] = field(default_factory=list)

    def start(self) -> None:
        print(f"\n{self.title}")
        print("=" * _LABEL_WIDTH + " " + "=" * 10)

    def record(self, finding_id: str, claim: str, state: str, detail: str = "") -> None:
        """Record one check outcome and print it immediately."""

        label = f"[{finding_id}] {claim}"

        if len(label) > _LABEL_WIDTH:
            label = label[: _LABEL_WIDTH - 1] + "…"

        print(f"{label:<{_LABEL_WIDTH}} {state}")

        if detail:
            for line in detail.splitlines():
                print(f"{'':<{_LABEL_WIDTH}} {line}")

        self.results.append((finding_id, state, detail))

    def note(self, text: str) -> None:
        """Print supporting evidence that is not itself a pass/fail check."""

        for line in text.splitlines():
            print(f"    {line}")

    def finish(self) -> int:
        """Print a summary and return a process exit code.

        Exit code 0 means every check behaved as the review recorded it:
        physics claims still CONFIRMED, defect claims still REPRODUCED.
        Exit code 1 means something changed and the review text is now
        stale for that finding - which is the useful signal, not a failure.
        """

        states = [state for _, state, _ in self.results]
        changed = [
            finding_id for finding_id, state, _ in self.results if state in {REGRESSED, FIXED}
        ]

        print("-" * (_LABEL_WIDTH + 11))
        print(
            f"{len(states)} checks: "
            f"{states.count(CONFIRMED)} confirmed, "
            f"{states.count(REPRODUCED)} reproduced, "
            f"{states.count(FIXED)} fixed, "
            f"{states.count(REGRESSED)} regressed"
        )

        if changed:
            print(f"\nChanged since the review: {', '.join(changed)}")
            print("The review write-up is stale for those findings.")
            return 1

        print("\nEvery finding still holds exactly as reviewed.")
        return 0


def main_guard(exit_code: int) -> None:
    """Exit with the collected status."""

    sys.exit(exit_code)
