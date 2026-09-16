---
id: PL-RCQM
title: PL-4L6Z's verify command runs the whole reference suite, exceeds check --verify's 120s limit, and turns every push to main red
status: untriaged
added: 2026-09-16
---

**Problem.** PL-4L6Z's verify command runs the whole reference suite, exceeds check --verify's 120s limit, and turns every push to main red

**Where it shows.** `main` is red and no pull request shows it. Run #2104 on
`ff4be610` and run #2106 on `d7a3b05` both failed the `checks` job on

```
PL-4L6Z: `verify:` command killed at the 120s limit, so nothing is claimed
about it - the command is either too slow for a check that runs on every
`make check`, or it hangs
```

The command is `uv run pytest tests/reference/ && grep -rq 'def
test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value'
tests/reference/`. Its first half is a whole test directory, which is what the
`verify:` guidance in `.claude/skills/docket/SKILL.md` asks for in the
coverage case and not here.

**Why it is not visible on a branch.** `.github/workflows/quality.yml` runs the
scoped `bin/docket check --verify --verify-base "$VERIFY_BASE"` on a pull
request and the whole-store `bin/docket check --verify` on a push to `main`. A
branch replays only the items its own diff touched, so no pull request replays
`PL-4L6Z` and none of them goes red. Every merge to `main` does.

**Why it is worth interrupting for.** It is `CLAUDE.md`'s "being routed around"
test rather than merely a defect: a `main` that has been red since at least
2026-09-16 17:32 trains every session to read past `main`'s CI status, which is
the same status a base-recovery notice and the drive-to-green rules are read
from. It also makes the whole-store replay useless as a gate - it fails on this
one item regardless of what else the store is doing.

**Found 2026-09-16** while implementing `PL-83LS`, from the session-start
digest's `main's quality run #2104 ... concluded failure` line.

**Where.** `docs/items/PL-4L6Z-*.md`'s `verify:` field, and possibly the limit
itself in `subprojects/docket/src/docket/`.

**Options, not yet decided.** Narrow the command to the one reference test the
item adds, paired with a `grep` as the skill's own table prescribes; raise the
per-command limit, which makes the whole-store replay slower for everyone and
does not answer whether this command hangs; or record `not-delegable:` and drop
the command, which loses what it proves. The first looks right and the item is
`PL-4L6Z`'s own author's to confirm - the test it names does not exist yet, so
whoever writes it decides what proves it.

**Related.** `PL-0HPV` (`make check` omits the verify replay, so this failure
class is only ever found from CI) is why nobody running `make check` locally
sees it. `PL-FSH9` (no workflow sets `timeout-minutes`) is the other half of a
hung command.
