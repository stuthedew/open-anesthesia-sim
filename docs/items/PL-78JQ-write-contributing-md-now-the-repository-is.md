---
id: PL-78JQ
title: Write CONTRIBUTING.md now the repository is public: PL-8DDG deferred it to the go-public flip, PL-XYRN recorded it as owed, and no open item carries it
priority: P2
effort: S
status: done
classes: docs
feature: public-readiness
touches: CONTRIBUTING.md, README.md
added: 2026-09-08
closed: 2026-09-08
verify: python3 tools/doc_check.py check && grep -qF 'nothing checks your pull request for one' CONTRIBUTING.md
---

**Problem.** Write CONTRIBUTING.md now the repository is public: PL-8DDG
deferred it to the go-public flip, PL-XYRN recorded it as owed, and no open
item carries it.

`PL-8DDG` answered the question as "not yet" with an explicit condition: "a
real `CONTRIBUTING.md` when the repository goes public — recorded as a
candidate on `PL-XYRN`". `PL-XYRN` then listed it under "The pass itself keeps
its starting list" and closed on the visibility flip alone, which is what its
**Done when** required. So the condition was met on 2026-09-06 and the item
that would have carried the work was already closed. Nothing in the queue
named it, so `bin/docket next` could not offer it and no session would have
found it except by reading two closed items in sequence.

**Why it matters.** The holding position `PL-8DDG` left — a "Contributing"
section in the README saying "There are no separate contribution guidelines
yet" — was written while the repository was private and the contributor
audience did not exist. It has been wrong since the flip, and it is the first
thing a contributor reads.

It also had nowhere to put the answer to `PL-8P6D`. That item removes the
check that refused a contributor's pull request; this one is what tells them
the refusal is gone, that the `PL-XXXX` titles filling the pull request list
are not a format they have to match, and what CI will actually hold them to.
A route nobody can find is not a route.

**What was done.** `CONTRIBUTING.md` at the repository root: reporting a
problem, sending a change, what the `checks` and `pr-title` jobs each check,
the four standards a change is most often held to, the `docs/references/`
redistribution rule, and the licence. It leads with the queue being the
maintainer's bookkeeping and no id being owed, because that is the question
the pull request list raises before any other.

The README's "Contributing and getting help" section now points at it, in
place of the "no separate contribution guidelines yet" paragraph and the
four-clause summary that stood in for them.

**Deliberately not covered: how the project is developed, and what each
attribution trailer means.** That is `PL-XH1D`, still open, and it is a
different question with a different reader. Saying it twice, in two documents,
in two sessions' words, is how the two come to disagree.
