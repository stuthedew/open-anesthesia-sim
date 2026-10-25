---
id: PL-2CPD
title: During product focus the session-start digest still leads with the bare next pick, a workflow generator item, so a product session that follows its Top line is handed apparatus work; only the docket skill's text routes it to the By lane product entry
priority: P3
effort: S
status: done
classes: infra
feature: workflow-stress-2026-09
milestone: v0.6.7
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_config.py, subprojects/docket/README.md, docket.toml, CLAUDE.md, docs/resident-instructions.md, .claude/skills/docket/SKILL.md, .claude/skills/docket/modes/picking.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
blocked-by: PL-NZC0, PL-GPJ7, PL-HMZZ, PL-MB2W, PL-PVW2, PL-QHCW, PL-XBV4
added: 2026-09-25
closed: 2026-10-25
pr: 1801
payoff: a product session that follows the digest's first pick line is handed product work, not an apparatus item
verify: grep -q 'def test_the_digest_leads_with_the_product_pick_under_product_focus' subprojects/docket/tests/test_cli.py
---

**Problem.** During product focus the session-start digest still leads with the bare next pick, a workflow generator item, so a product session that follows its Top line is handed apparatus work; only the docket skill's text routes it to the By lane product entry

**Found** while writing `PL-2866`'s text, 2026-09-25. The digest's `Top:` line is `next` with no lane, so under product focus it names whatever ranks first overall - on the day of the switch, `PL-FX5Q`, a workflow item ranked above every band as a generator's blocker. `.claude/skills/docket/SKILL.md`'s Implementation paragraph now tells a product session to take the `By lane` line's product entry instead, but that holds only once the skill has loaded, and the digest is read at launch. `PL-NZC0`'s fallback, if the trial fails its bar, makes the digest's top line the pick; if the trial passes, nothing changes this line. Captured, not built: it is a new mechanism under the generator pause.

**Correction (triage, 2026-09-25).** The skill is not the only carrier. `CLAUDE.md` § "What this project is", resident and landed in the same #1014, says a session given no particular work "picks from `bin/docket next product`". What stays true is that the digest's `Top:` line, the most prominent line a session reads at launch, contradicts both.

Reproduced 2026-09-25 against 46954a81: `bin/docket digest` prints `Top: PL-HMZZ ...`, a workflow generator head at `needs-decision` marked "ranked above every band but P0", and names product `PL-WMCJ` only on the `By lane` line. #1014 (`PL-2866`) changed nothing under `subprojects/`, only `CLAUDE.md`, the skill, `docs/resident-instructions.md` and item files, so the digest is as it was.

**Why it matters.** A session that follows the digest's first line over a paragraph deep in `CLAUDE.md` starts apparatus work under product focus, which is what `PL-2866` exists to stop. The cost is a misdirected session each time, not a wrong value.

**Blocked, triage 2026-09-25.**
- **Held by the pause.** As captured, it is a new mechanism. The digest would have to learn a focus that today lives only in `CLAUDE.md` prose, through a new setting or a new meaning for `Top:`. It is not a defect in what exists, because the line is true for what it claims: the top of the unlaned ranking.
- **Shaped by `PL-NZC0`'s verdict.** If the trial fails its bar, `PL-2866`'s fallback makes the digest's top line the pick, and this item closes into it. If the trial passes, this is the standing work.
- `blocked-by` names `PL-NZC0` and the six items carrying `generator: live` that day. Before unblocking, check that `bin/docket generators` marks no head "still generating"; a head can be recorded spent while open, or a new one arrive, without touching this list.

**Checked 2026-10-25:** unblocked. `PL-NZC0` closed with the trial passing both bars, so this is the standing work and `PL-2866`'s fallback does not follow. Every other blocker has closed. `bin/docket generators` marks three heads still generating, `PL-58D7`, `PL-HJKN` and `PL-N7MM`, and all three are product-lane heads, so the workflow-lane pause does not hold this item. The brief's reproduction is 30 days old, so the session that takes it re-runs `bin/docket digest` first.

**Done when.** Under a declared product focus, the digest's first pick line names the product lane's top item, with a test in `subprojects/docket/tests/test_cli.py`. Or this item is dropped into `PL-NZC0`'s fallback, naming it.

**Done 2026-10-25.** Re-run first, as the check above asked: `bin/docket
digest` printed `Top: PL-HJKN`, a product item, so the reproduction did not
hold that day. The defect still did, because the line was the unlaned top and
named a product item only by chance. The focus now has one record that code
reads: `docket.toml`'s `focus` key, set to `product`. `docket.config` refuses a
value that names no lane. `format_digest` ranks the `Top:` line in that lane
alone and labels it `Top, product focus:`. Where the lane has nothing
startable, the line says so rather than naming the other lane's work. The `By
lane` line is unchanged. `CLAUDE.md`'s product-focus paragraph now says that
ending the focus removes the key too, and `docs/resident-instructions.md`
records that edit. The skill's Implementation paragraph and `picking.md` no
longer send a product session to the `By lane` line. A key was chosen over
reading the `CLAUDE.md` paragraph, because parsing prose for a mode would be
the "sharper heuristic" the one-source rule refuses.

**Generator check.** One-off. The fact is which lane a session given no particular work takes: a mode declared on 2026-09-25 in `CLAUDE.md` prose that no code reads yet, and the digest predates it. No head's `misread:` states it.
