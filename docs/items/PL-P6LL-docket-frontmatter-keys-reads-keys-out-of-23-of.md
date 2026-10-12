---
id: PL-P6LL
title: docket.frontmatter.keys reads keys out of 23 of the YAML Test Suite's 51 invalid in-domain documents, so a front matter a conformant parser refuses still passes docket's checks
priority: P3
effort: M
status: ready
classes: defect
feature: reader-checks
touches: subprojects/docket/src/docket/frontmatter.py, subprojects/docket/tests/test_frontmatter_suite.py, subprojects/docket/tests/yaml-test-suite
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed at capture, 2026-10-12
added: 2026-10-12
payoff: a rule or skill whose front matter a YAML parser refuses fails docket's checks, instead of passing while Claude Code may read no paths: from it
verify: grep -rq 'def test_keys_refuses_the_yaml_test_suite_error_cases' subprojects/docket/tests
---

**Problem.** docket.frontmatter.keys reads keys out of 23 of the YAML Test Suite's 51 invalid in-domain documents, so a front matter a conformant parser refuses still passes docket's checks

Filed 2026-10-12 from the thread answering the owner's question of that day,
whether a published test corpus exists to verify this repository's lexers
against ("Agree with recs", project owner, 21:54 UTC). The measurements, sources
and rerunnable probes are in `/mnt/project-files/v0.6.0/lexer-corpora.md` and
`/mnt/project-files/v0.6.0/lexer-corpora-probes/`, outside the repository.

**Measured 2026-10-12 against the YAML Test Suite**
(https://github.com/yaml/yaml-test-suite, MIT; the npm `yaml-test-suite` 0.1.0
copy). Of 402 cases, 148 hold a `---`, `...` or `%` line no front matter can
hold; of the 254 left, 203 are valid and 51 must be refused. On the 175 valid
ones carrying an expected value, `docket.frontmatter.keys` never misread: it
read the suite's own key names for all 68 mappings it read, and declined 23
mappings in forms no front matter here writes and all 84 non-mappings. **On the
51 invalid ones it declined 28 and read keys out of 23**, among them a list
entry indented less than its siblings, text after a closing quote
(`key2: "quoted2" trailing content`), `a: b: c: d`, a tab standing as
indentation and `key: "value"# comment`.

**The oracle is the suite, not PyYAML.** `test_frontmatter_reference.py`
generates only YAML PyYAML composes into one mapping, so this is untested by
design. PyYAML implements YAML 1.1 and itself accepts 4 of the 51 invalid
cases and departs from the suite on 37 of the 175 valid ones, so it cannot
judge this. The consumer of rule and skill front matter is Claude Code, whose
YAML library could not be determined (its bundle carries both js-yaml's and the
`yaml` package's messages).

**Decision** (project owner, 2026-10-12, ratified, "Agree with recs" in the
thread at 21:54 UTC, over leaving `keys` reading what a conformant parser
refuses): `keys` refuses YAML a conformant parser rejects, within the forms it
reads, rather than reading keys out of it.

**Why it matters.** A rule or skill whose front matter a strict parser refuses
passes docket's checks today, while Claude Code may read no `paths:` from it,
so the rule would silently stop loading. That is the floor in
`.claude/rules/apparatus-standard.md`: an answer is true or says it could not
answer.

**Done when.** `keys` raises `Unread` on each of the suite's in-domain error
cases it reads keys from today, and a test in `subprojects/docket/tests/` runs
the suite's in-domain cases, vendored with their licence, holding that `keys`
either declines or agrees with the suite's expected JSON on every valid case
and never reads keys out of an error case.

**Generator check.** A one-off: the fact it misreads, whether a front matter is
YAML at all, is named by no head, and no other item misreads it.
