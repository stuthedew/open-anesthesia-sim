---
id: PL-0MC5
title: required_checks_check reads workflow YAML by hand with no reference parser: hold triggers and steps to a YAML parser over generated workflows, as test_frontmatter_reference.py holds docket.frontmatter
priority: P3
effort: M
status: done
classes: test
feature: reader-checks
milestone: v0.5.28
touches: tests/unit/test_required_checks_reference.py, docket.toml
added: 2026-10-12
closed: 2026-10-18
pr: 1568
payoff: a workflow form required_checks_check misreads fails the pull request that first writes it, rather than surfacing as an item after it merges
verify: grep -rq 'def test_required_checks_reads_generated_workflows_as_yaml_does' tests/unit
---

**Problem.** required_checks_check reads workflow YAML by hand with no reference parser: hold triggers and steps to a YAML parser over generated workflows, as test_frontmatter_reference.py holds docket.frontmatter

Filed 2026-10-12 from the thread answering the owner's question of that day,
whether a published test corpus exists to verify this repository's lexers
against ("Agree with recs", project owner, 21:54 UTC). The measurements, sources
and rerunnable probes are in `/mnt/project-files/v0.6.0/lexer-corpora.md` and
`/mnt/project-files/v0.6.0/lexer-corpora-probes/`, outside the repository.

**What reads it, and what holds it.** `tools/required_checks_check.py` reads a
workflow's `on:`, its jobs and their steps by hand (`triggers`, `steps`), and
raises `Undecidable` for the YAML it does not read: block scalars, aliases,
tags, explicit keys, and a node carried past its line. Its tests
(`tests/unit/test_required_checks_check.py`) are hand-written, with no
reference parser. Seven workflow misreads have closed as items, each found after
merge: `PL-4T49`, `PL-848V`, `PL-CK3F`, `PL-GWQ7`, `PL-TMX9`, `PL-PZP7`,
`PL-S3XS`.

**The oracle.** The consumer is GitHub. Its open-source workflow parser,
`@actions/workflow-parser` (actions/languageservices), parses with the `yaml`
npm package, whose README says it passes all of the YAML Test Suite. PyYAML,
already a dev dependency, is the practical oracle in Python, with two known
departures the test must handle: it implements YAML 1.1, so the key `on` loads
as `True` and has to be mapped back, and it departs from the YAML Test Suite on
37 of 175 valid in-domain cases (tabs, flow-collection edges, anchors, tags;
measured 2026-10-12), so the generator draws only the forms GitHub and PyYAML
read alike.

**Measured 2026-10-12.** On the six tracked workflows the reader and PyYAML
agree: the same events and the same step counts (3, 15, 4, 33, 3, 3). So this
is regression cover, not a known departure.

**Why it matters.** Workflow misreads decide which checks a pull request is
held to, and each of the seven was found after the form merged. A generated
comparison fails the pull request that first writes the form.

**Done when.** A test in `tests/unit/` generates workflows with Hypothesis,
derandomized, from the forms the closed items name (an `on:` value on the next
line, block-sequence and flow-mapping `on:`, four-space indents, a
`pull_request` trigger as a list entry or flow mapping, a commented line, a
continued job name, `run:` beside other keys), and holds `triggers` and `steps`
to PyYAML's reading with `True` mapped back to `on`. Where the reader raises
`Undecidable` the test accepts the decline; where it answers, the answer must
match.

**Generator check.** Work the owner asked for. The closed members misread the
fact `PL-848V`'s head names; this item is the oracle that would have caught
them, not another instance.

**Built 2026-10-18.** `tests/unit/test_required_checks_reference.py` draws
1,000 workflows with Hypothesis, derandomized, and holds `triggers` and `steps`
to PyYAML 6.0.3's composed nodes. Reading nodes rather than loaded values keeps
the key's text `on`, so nothing has to be mapped back from `True`. The strategy
draws the forms the closed items name, and a second test holds the tracked
workflows the same way. On `main` at `684c1f66` both readers answered all
1,000 drawn workflows, with no decline, and agreed with PyYAML on every one.
Four planted reader bugs each turned the generated test red: a filter list cut
to its first name, a `run:` key's column off by one, a list entry's line off
by one, and a list at its key's column read as ending the value. The generated
test takes about 8 seconds.
