---
id: PL-Y2GG
title: Add a LICENSE file and a pyproject license field before the repository goes public
priority: P2
effort: S
status: done
classes: docs, infra
milestone: v0.2.5
touches: LICENSE, pyproject.toml, README.md
added: 2026-08-25
closed: 2026-08-25
commit: d40ff83
---

**Problem.** Add a LICENSE file and a pyproject license field before the repository goes public

**Why it matters.** With no licence, default copyright applies and nobody may
legally use, copy, modify or contribute - so a public repository would be open
in appearance only, and any contribution offered back would sit in a grey area.
`pyproject.toml`'s `license` field is separately what packaging metadata reads.

**Decision needed.** Which licence. The usual choice for a tool that wants wide
academic and clinical-education use is MIT or Apache-2.0; both are permissive
and differ mainly in that Apache-2.0 carries an explicit patent grant and a
contribution clause. Recommend **Apache-2.0**, on the grounds that the patent
grant is worth having for anything medical-adjacent and it is the more common
choice for scientific software intended to be built on. This is the project
owner's call, not a recommendation with legal weight - worth a moment's
thought about whether any employer or institution has a claim here.

**Where.** `LICENSE` (new), `pyproject.toml`, and the README's footer.

**Done when.** A LICENSE file exists, `pyproject.toml` declares the same
licence, and the README names it.

**Where.**

**Done when.**
