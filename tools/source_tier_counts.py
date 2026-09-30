"""Print how many stored values rest on a source of each tier, read from the data files.

For each data file under `src/anesthesia_sim/data/`, the stored values are
listed by the tier of the `sources` entry adopted as their authority - tier 1
(primary), 2 (secondary) or 3 (reference implementation), numbered as
`docs/MODEL.md` § "Source hierarchy" numbers them - with each entry's citation
beside the values it covers, or under "no adopted source". Then the totals over
all files, which are the counts that section states in prose, and how many
`sources` entries are adopted, by tier, and how many are cited without being
adopted.

It prints, and never checks or edits the prose. That is the project owner's
decision of 2026-09-13, recorded on `PL-9LXK`: a tool editing the paragraph
would be guessing at its rounding and its phrasing, and the counts rule in
`docs/MODEL.md` § "How this document is held to the tree" says a count no check
holds is read from the tool that prints it.

The link from a stored value to its source is each entry's `authority_for`
(`PL-9LXK`, 2026-09-30), which the loader in `core/parameters.py` and
`check_source_tiers` in `tools/doc_check.py` validate. This runs that check
first and prints no count while it reports anything: a value counted under two
tiers, or under none because its path was misspelt, is a plausible wrong
number. What a stored value is comes from `doc_check` too - `_leaf_numbers`,
the set `check_provenance` holds the provenance table to - so the rows counted
here cannot drift from the table's.

Exits 1 when it refuses to count, and 2 when there is no data directory.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import doc_check

#: The tiers in the order `docs/MODEL.md` § "Source hierarchy" numbers them.
TIERS = tuple(enumerate(doc_check.SOURCE_TIERS, start=1))
LABELS = {tier: f"tier {number} ({tier.replace('-', ' ')})" for number, tier in TIERS}


def _stored(count: int) -> str:
    return f"{count} stored value{'' if count == 1 else 's'}"


def _refuse(problems: Sequence[str]) -> int:
    print("source_tier_counts: no counts printed, until these are fixed:", file=sys.stderr)
    for problem in problems:
        print(f"  {problem}", file=sys.stderr)
    print("`python3 tools/doc_check.py check` gives the full report.", file=sys.stderr)
    return 1


def _format(documents: Mapping[str, Any]) -> str:
    """The per-file groups and the totals, for documents that pass `check_source_tiers`."""
    lines = [
        "Stored values by the tier of the source adopted for each, read from each sources "
        f"entry's authority_for under {doc_check.PACKAGE_ROOT}/data/.",
        "",
    ]
    values = dict.fromkeys(doc_check.SOURCE_TIERS, 0)
    unadopted_values = 0
    adopted = dict.fromkeys(doc_check.SOURCE_TIERS, 0)
    cited = 0
    for relative, document in documents.items():
        sources = document["sources"]
        leaves = [key_path for key_path, _value in doc_check._leaf_numbers(document)]
        authority = {
            path: index for index, entry in enumerate(sources) for path in entry["authority_for"]
        }
        lines.append(f"{relative}: {_stored(len(leaves))}")
        for tier in doc_check.SOURCE_TIERS:
            covered = [
                (
                    doc_check._short_citation(entry),
                    [leaf for leaf in leaves if authority.get(leaf) == index],
                )
                for index, entry in enumerate(sources)
                if entry["adopted"] and entry["tier"] == tier
            ]
            count = sum(len(named) for _citation, named in covered)
            values[tier] += count
            if count:
                lines.append(f"  {LABELS[tier]}: {count}")
                lines.extend(f"    {citation}: {', '.join(named)}" for citation, named in covered)
        unnamed = [leaf for leaf in leaves if leaf not in authority]
        unadopted_values += len(unnamed)
        if unnamed:
            lines.append(f"  no adopted source: {len(unnamed)}")
            lines.append(f"    {', '.join(unnamed)}")
        for entry in sources:
            if entry["adopted"]:
                adopted[entry["tier"]] += 1
            else:
                cited += 1

    by_tier = ", ".join(f"{values[tier]} {LABELS[tier]}" for tier in doc_check.SOURCE_TIERS)
    entries = ", ".join(f"{adopted[tier]} tier {number}" for number, tier in TIERS)
    lines.append("")
    lines.append(
        f"All files: {_stored(sum(values.values()) + unadopted_values)} - {by_tier}, "
        f"{unadopted_values} with no adopted source."
    )
    lines.append(
        f"sources entries: {sum(adopted.values()) + cited} - {sum(adopted.values())} adopted "
        f"({entries}), {cited} cited and not adopted."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()
    data_root = root / doc_check.PACKAGE_ROOT / "data"
    if not data_root.is_dir():
        print(f"source_tier_counts: no data directory at {data_root}", file=sys.stderr)
        return 2

    documents: dict[str, Any] = {}
    for data_path in doc_check._walk(data_root):
        if data_path.suffix != ".json":
            continue
        relative = data_path.relative_to(root / doc_check.PACKAGE_ROOT).as_posix()
        try:
            documents[relative] = json.loads(data_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return _refuse([f"{relative}: cannot be read as JSON ({error})"])

    report = doc_check.Report()
    doc_check.check_source_tiers(root, report)
    if report.errors:
        return _refuse(report.errors)

    print(_format(documents))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
