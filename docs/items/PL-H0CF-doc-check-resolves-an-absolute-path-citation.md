---
id: PL-H0CF
title: doc_check resolves an absolute-path citation against the container filesystem, so one tree gives root and CI different verdicts on the same line
priority: P2
effort: S
status: ready
classes: defect, infra
feature: doc-consistency-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-21
payoff: A path citation's verdict depends on the repository alone, so root and the CI runner agree on the same commit - which is what PL-1RTM needs before it hands the queue's 22 absolute tokens to check_citations.
verify: grep -q 'def test_an_absolute_citation_is_repository_anchored' tests/unit/test_doc_check.py
---

**Problem.** doc_check resolves an absolute-path citation against the container filesystem, so one tree gives root and CI different verdicts on the same line

**Where.** `tools/doc_check.py`, `_resolves`. `PATH_ROOTS` is `("",
str(PACKAGE_ROOT))`, and `base / candidate` for an absolute `candidate` is the
absolute path itself - `Path("/repo") / "/root/.ccr/README.md"` is
`/root/.ccr/README.md`. So for any token beginning `/`, the resolver is asking
the machine it is running on, not the tree it is checking.

**Found 2026-09-21 while fixing `PL-D1NT`** (the unguarded stat in the same
function), which stops the crash and leaves this behind. `PL-D1NT`'s brief
reads the split as root-versus-CI-user; that is half of it. Measured this
session:

| Interpreter | `Path("/root/.ccr/README.md").exists()` as root | as an unprivileged user |
| --- | --- | --- |
| 3.10 - 3.13 | `True` | raises `PermissionError` (now caught) |
| 3.14 | `True` | `False` |

3.14 rewrote `Path.exists` to `return os.path.exists(self)`; through 3.13 it
re-raises any `OSError` outside ENOENT, ENOTDIR, EBADF and ELOOP. After
`PL-D1NT` every interpreter answers alike - but the *user* still decides the
verdict, because root can stat what the CI runner cannot. One tree, one
commit, two answers.

**It is wider than the permission case.** Every absolute token asks the
container rather than the repository:

- `/etc/passwd` would resolve on any Linux box and be reported as a valid
  citation of this repository.
- `/home/user/open-anesthesia-sim/src/anesthesia_sim/core/alveolar.py`
  resolves in a session container and nowhere else.
- `/docs/MODEL.md` - the repo-anchored spelling `.claude/rules/*.md` uses in
  its `paths:` frontmatter - resolves against the filesystem root, so a file
  that *is* there is reported dangling.
- `/` alone is accepted by `_is_path_citation` (it ends in `/`) and always
  resolves.

**Measured over the queue, 2026-09-21.** 22 open and closed briefs carry 14
distinct absolute tokens that `_is_path_citation` accepts:

```text
/                                     12 briefs    always resolves
/root/.ccr/README.md                   3           root yes, CI no
/docs/worker.md                        2           exists in repo, reported dangling
/subprojects/docket/uv.lock            2           exists in repo, reported dangling
/README.md /docs/MODEL.md /docs/*.md /out/         same
/root/.claude/CLAUDE.md /root/.claude/rules/       root yes, CI no
/opt/pw-browsers/... /usr/lib/x86_64-linux-gnu/    container-dependent
/oas-mirror/                                       container-dependent
/home/user/open-anesthesia-sim/src/.../alveolar.py this checkout only
```

Reproduce with `tools/doc_check.py`'s own `CODE_SPAN_RE` and
`_is_path_citation` over `docs/items/*.md`, filtering to tokens starting `/`.

**Why it matters now.** None of these is currently scanned: `check_citations`
reads `DOC_GLOBS`, which is the authoritative documents only. `PL-1RTM` (path
citations are unchecked in the queue, where most of this project's prose is)
proposes handing the item files to `check_citations`, and the moment it lands
all 22 enter the scanned set at once - the repo-anchored spellings as false
errors on files that exist, the container paths as verdicts that differ by who
ran the check. That makes this a prerequisite for `PL-1RTM` rather than a
parallel cleanup, and the measurement above is part of the "worth measuring
before building" `PL-1RTM` asks for.

**Shape of a fix.** Decide the token by where it points rather than by whether
some filesystem holds it: a citation that resolves outside the repository root
is not a repository path citation. Two candidate readings, and the choice is
the design work -

1. Treat a leading `/` as repository-anchored, matching `.claude/rules`
   frontmatter and `.gitignore`. `/docs/MODEL.md` then resolves and
   `/root/.ccr/README.md` is reported as absent from the tree, on every machine
   and every user.
2. Refuse an absolute token outright, with a message naming the reason
   ("cites `X`, which is outside the repository"), and require prose to name
   such a file without marking it as code - which is what `PL-ZM48` did by
   hand to work around `PL-D1NT`.

Reading 1 fixes the false errors as well and is the better bet; it needs a
check that `/` and other degenerate tokens do not become citations of the root.

**One line of `PL-D1NT`'s fix reads slightly wrong until this lands.** An
unstattable path is reported as "cites `X`, which does not exist", where the
truth is that the checkout was refused permission to look. Left as-is
deliberately: it is one message shared by every dangling citation, the refused
case is rare, and under either reading above the absolute tokens stop reaching
it. Fold the wording into whichever is chosen rather than filing it separately.

**This brief is itself an instance**, and so is `PL-D1NT`'s: both have to
show the tokens they are about, in code spans, and both would be reported by
whichever reading lands. `check_line_citations` already has the escape and the
reasoning - `test_an_item_may_quote_the_broken_citation_it_reports`, "without
the escape, reporting the defect *is* the defect" - so the fix owes the same
treatment here rather than a rewording of these two briefs.

**Done when.** A path citation's verdict depends only on the repository
contents - the same commit gives the same answer as root, as an unprivileged
user, and on a machine where `/root/.ccr/README.md` does not exist - and
`tests/unit/test_doc_check.py` pins at least the repo-anchored case and the
outside-the-repository case.
