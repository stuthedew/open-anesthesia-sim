"""Report a possessive citation that names a section, which `§` should carry.

`CITATION_CONNECTIVE` admits the possessive since `PL-316G`, so both forms are
checked for staleness by the same containment test and neither can rot
silently. That settles correctness and leaves notation: `` `doc.md` § "X" ``
tells a reader the quotation is a *section title*, and `` `doc.md`'s "X" ``
tells them nothing, because this project writes the possessive to quote a
sentence as often as to cite a section.

**The decidable half is which of the two a given citation is, and only where
the answer is yes.** A quotation that matches a heading or a `**Bold.**` marker
in the cited file is a section citation - that is a fact about the tree, not a
reading of intent. A quotation that matches no heading may still be a faithful
quotation of a sentence, which is correct as written, so this reports nothing
about it. The asymmetry is the point: `CLAUDE.md` refuses to script the
judgment half, and the half that would need judgment is exactly the one left
alone here.

Run as a command it exits 1 with a line per site. It is `PL-316G`'s `verify:`
while the conversion is outstanding, and is wired into `make check` once the
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


def sites(root: Path) -> list[str]:
    """Every possessive citation whose quotation names a section of its target."""
    documents = doc_check.read_docs(root)
    headings = {
        str(path): [doc_check._comparable(title) for title in doc_check._headings(text)]
        for path, text in documents.items()
    }
    found: list[str] = []
    for path, offset, text in doc_check._quoting_sources(root, documents):
        for match in POSSESSIVE_RE.finditer(doc_check._without_fences(text)):
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
    found = sites(root)
    print("\n".join(found) if found else "possessive citations: none names a section")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
