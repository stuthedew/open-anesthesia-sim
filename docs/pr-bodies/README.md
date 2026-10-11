# Recovered pull request bodies

Every file here is a historical record, not documentation. Each holds one
merged pull request's body, named by its number. Most are here because the
squash commit that should have carried the body onto `main` landed without it;
the files headed `recorded:` were written for every pull request in the two
days `PL-979D`'s record stood. For every other pull request the squash commit's
body is the record, and nothing is kept here. `tools/pr_body_check.py` wrote
them and recovers new ones at each release, and its docstring says what each
header field holds.

**Nothing in a record is maintained.** The body is verbatim, as GitHub served
it on the day it was fetched. Its paths, line numbers, symbols, item states and
commit hashes describe the tree at the pull request's merge, and the tree has
moved since: a path that no longer exists, or a hash that no longer resolves,
is the history rather than a defect, so it is not repaired and not filed. That
is the reading `.claude/rules/citation-drift.md` gives a closed item's brief,
for the same reason. The one field kept current is the header's `commit:`, the
squash commit the body belongs to, which `tools/pr_body_check.py --anchors`
checks in `make check`.

GitHub's view of a record shows two things that reading the raw file does not:

- A placeholder written between angle brackets, such as an item id or a branch
  name, is taken for an HTML tag and not shown. It is in the file.
- The header follows the item files' front-matter convention, which is
  deliberately not YAML (`subprojects/docket/README.md` § "What the front
  matter is, exactly"), so a header holding a colon inside a value is shown
  below an "Error in user YAML" box. Every field is still there, as raw text.

`tools/doc_check.py` does not read this directory, by design. Its document
sweep covers `docs/*.md` one level deep, and its host-claim rule lists the
directory among the dated records it leaves alone: holding these files to the
present tree would refuse records nobody rewrites. Nothing reads a record as
the authority for a present-day fact, and one that did would make this
directory documentation and reopen the question `PL-TDBT` answered (project
owner, 2026-10-03, ratified, over treating the records as current
documentation and repairing their citations).
