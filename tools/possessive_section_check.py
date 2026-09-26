"""Report a possessive citation that names a section, which `§` should carry.

`CITATION_CONNECTIVE` admits the possessive since `PL-316G`, so both forms are
checked for staleness by the same containment test and neither can rot
silently. That settles correctness and leaves notation: `` `doc.md` § "X" ``
tells a reader the quotation is a *section title*, and `` `doc.md`'s "X" ``
tells them nothing, because this project writes the possessive to quote a
sentence as often as to cite a section.

**The decidable half is which of the two a given citation is, and only where
the answer is yes.** A quotation that matches a `#` heading in the cited file
is a section citation - that is a fact about the tree, not a reading of intent.
A quotation that matches no heading may still be a faithful quotation of a
sentence, which is correct as written, so this reports nothing about it. The
asymmetry is the point: `CLAUDE.md` refuses to script the judgment half, and
the half that would need judgment is exactly the one left alone here.

A `**Bold.**` marker is in that half. It is often a bullet's or a paragraph's
lead sentence as well as a title, so `` `CLAUDE.md`'s "Capture, always, and
capture cheaply" `` quotes a sentence correctly, and `§` would cite the same
marker correctly - `doc_check` resolves a section mark against markers too. It
was reported until `PL-FKH6`, a gate refusing a quotation that was right.

Run as a command it exits 1 with a line per site. It was `PL-316G`'s `verify:`
while the conversion was outstanding, and `make check` runs it now that the
tree is clean, so the convention holds for citations nobody has written yet.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import doc_check

#: The possessive citation, in the two spellings this project writes.
POSSESSIVE_RE = re.compile(
    r"`(?P<document>[\w./-]+\.md)`['’]s(?:\s+own)?[ \n]*\"(?P<quoted>\w[^\"]{2,200}?)\"", re.DOTALL
)


def sites(root: Path, declined: list[str]) -> list[str]:
    """Every possessive citation whose quotation names a section of its target.

    A source file this run cannot parse or read is appended to `declined`
    rather than skipped, for the reason `doc_check._quoting_sources` gives: CI's
    floor section runs this under 3.11, which cannot parse every file the
    source's own interpreter can, and a skip said nothing (`PL-MB3F`).
    """
    documents = doc_check.read_docs(root)
    headings = {
        str(path): [doc_check._comparable(title) for title in doc_check._hash_headings(text)]
        for path, text in documents.items()
    }
    found: list[str] = []
    for path, offset, text in doc_check._quoting_sources(root, documents, declined):
        for match in POSSESSIVE_RE.finditer(doc_check.without_fences(text)):
            quoted = doc_check._comparable(match.group("quoted"))
            titles = headings.get(match.group("document"), ())
            if not any(title == quoted or title.startswith(quoted + " ") for title in titles):
                continue
            line = offset + doc_check._line_of(text, match.start()) - 1
            written = doc_check._normalized(match.group("quoted"))
            found.append(
                f'{path}:{line}: `{match.group("document")}`\'s "{written}" names a section; '
                f'write it as `{match.group("document")}` § "{written}"'
            )
    return found


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent
    declined: list[str] = []
    found = sites(root, declined)
    print("\n".join(found) if found else "possessive citations: none names a section")
    if declined:
        # A decline is not a finding, so it does not fail the run - the same
        # split `doc_check.Report.declined` keeps: nothing was read, so
        # nothing is claimed either way.
        print(f"Not checked ({len(declined)}; this run cannot answer, and nothing is claimed):")
        print("\n".join(f"  {line}" for line in declined))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
