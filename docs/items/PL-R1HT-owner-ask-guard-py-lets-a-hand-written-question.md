---
id: PL-R1HT
title: owner_ask_guard.py lets a hand-written question, options and recommendation carry an ask past arm's 'send the owner nothing' state, because arm --owner-ask exits 3 for six different answers and the hook then falls back to the form check meant for the coordinator
status: untriaged
feature: owner-ask-by-state
added: 2026-11-03
---

**Problem.** owner_ask_guard.py lets a hand-written question, options and recommendation carry an ask past arm's 'send the owner nothing' state, because arm --owner-ask exits 3 for six different answers and the hook then falls back to the form check meant for the coordinator

**Reproduced 2026-11-03.** `refusal()` was run with `owner_ask` stubbed to return exit 3 and arm's line "send the owner nothing: hold - its pull request waits on the owner read, and no Owner-ask record says what to ask". "Read #1950 and merge it." is refused. The same text is let through once this is added: `Which unit should the label show? Option "mcg": keeps the label short. Option "mg": matches the pump. I recommend "mcg": it is what the item specifies.` The cause is in `subprojects/docket/src/docket/cli.py`. With `--owner-ask`, every answer that is not sendable returns `arming.NO_ASK`, so the hook cannot tell a held thread from the coordinator. `.claude/hooks/owner_ask_guard.py`'s `refusal()` then accepts any message that `renders_owner_ask` matches. `docs/maintainer.md` tells the owner "A thread cannot send the ask anyway", which this reproduction shows is false. The test in `tests/unit/test_owner_ask_guard.py` gives the coordinator exit 3, and it passes whether or not this is fixed.
