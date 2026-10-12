---
id: PL-4S6C
title: Nothing in the repository refuses a second reading of a fact it already answers, so one-answer closed spent three times on bounded sweeps (PL-PVW2, PL-KGYT, PL-5DZ8) and re-entered each time; make one source of truth for a shared fact a hard principle of the code, enforced where a check can decide it (project owner, 2026-10-12)
priority: P1
effort: M
status: needs-decision
classes: defect
feature: one-answer
touches: CLAUDE.md, .claude/rules/apparatus-standard.md, docs/resident-instructions.md, tools, tests/unit/test_fact_home_check.py, Makefile, .github/workflows/quality.yml, docket.toml, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recorded as a generator head by its own design round, 2026-10-12
added: 2026-10-12
payoff: a second reader of git, the GitHub API, the tree, the item store or a shell command outside that fact's home fails make check, so one-answer stops re-entering one tool at a time and a head's spent verdict holds
root-cause-of: PL-PVW2, PL-KGYT, PL-5DZ8, PL-D23H
generator: live - three heads stating this fact closed spent on an enumerated sweep and were re-entered (PL-PVW2 by six filings, PL-KGYT by five, PL-5DZ8 by PL-D23H on the day it closed, per bin/docket inflow 2026-10-12), and nothing in make check refuses a reader of git, the GitHub API, the tree, the item store or a shell command outside that fact's home, so the next tool that needs one writes its own
misread: Which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it
reenters: PL-5DZ8
---

**Problem.** Nothing in the repository refuses a second reading of a fact it already answers, so one-answer closed spent three times on bounded sweeps (PL-PVW2, PL-KGYT, PL-5DZ8) and re-entered each time; make one source of truth for a shared fact a hard principle of the code, enforced where a check can decide it (project owner, 2026-10-12)

**The record, read 2026-10-12 at 98673556.** Three heads state one fact, in
one wording, and each closed `spent` on a sweep bounded by an enumeration:

- `PL-PVW2` (closed 2026-09-26): the nine predicates it had named, unified.
  Six readers of facts it never named were filed four days later, and
  `bin/docket inflow` records it re-entered by six filings.
- `PL-KGYT` (closed 2026-10-03): every name `model`, `vcs` and `release`
  export. Five readers outside those three modules were filed after it, and
  `inflow` records it re-entered by five.
- `PL-5DZ8` (closed 2026-10-12): every module under `subprojects/docket/`,
  `.claude/hooks/` and `tools/`, 72 facts filed as 19 members, and `spent`
  on the ground that "a new reader meets the write-time rule in
  `.claude/rules/apparatus-standard.md`". `PL-D23H`, a second reading of the
  lines a fence holds, was filed the day it closed.

The write-time rule is § "Read the fact from its record; where none exists,
write one" in `.claude/rules/apparatus-standard.md`, which loads only on an
apparatus path and ends by saying it "is prose rather than a check because
whether a reader infers or reads is the judgment half" (project owner,
2026-10-01, `PL-HC8P`). `PL-5DZ8`'s **Not built.** paragraph judged that a
check on names defined in two trees would find under a fifth of its 72 facts,
and built none. So the repository has a rule every session may read and
nothing that refuses the copy, and the record above is what that produces:
cleanup, head by head, with the mechanism in place for the next.

**The owner's words, 2026-10-12**, in the Ship v0.6.0 project chat, answering
that finding: "I want this to be a hard coding principle. Shared facts should
be one source of truth", and "Starting ASAP. That is a generator". *Hard*
overrides `PL-HC8P`'s prose-not-check call for the decidable part: that call
was a session's recommendation the owner agreed with, and the measurement
that reopens it is the three re-entries above (project owner, 2026-10-12,
over keeping the rule as prose alone). The judgment half - whether two
readers read one fact where neither reaches a primitive a check can name -
stays prose, as `CLAUDE.md` § "Prefer deterministic tooling over repeated
model work" refuses to script it.

**Measured 2026-10-12, on main at 98673556.**

- `subprocess` is imported in 15 files under `tools/`, 6 under
  `subprojects/docket/src/docket/` and 3 under `.claude/hooks/`; git is run
  from 26 call sites in 20 files outside `vcs.py`, four of them docket's own
  (`claiming.py`, `cli.py`, `lines.py`, `verify.py`).
- 81 string literals of a pattern, path or option shape are defined in two or
  more apparatus files: `--name-only` in nine, `merge-base` in eight,
  `docs/items` in seven, the GitHub API's URL and headers in four to six
  tools, the same four cache-directory names in three tree walkers.
- Of the twelve members filed after a head said spent (`PL-KGYT`'s six,
  `PL-5DZ8`'s five, `PL-D23H`), eight reach git, the tree, the item store's
  files, a branch literal or a table another file already defines - the
  shapes a boundary can name - and four are a second grammar for Markdown or
  shell text inside one tool, which no boundary reaches. Five of `PL-KGYT`'s
  six are the first kind.
- The pause: no open item carried `generator: live` before this one
  (`PL-40SJ` and `PL-MT3R` carry it closed). Recording this head live
  re-engages `CLAUDE.md`'s pause on new workflow mechanisms, which holds
  apparatus features and housekeeping and not defects. Read through docket's
  own `Item.lane` over the open store: the workflow lane holds 155 open
  items, 94 carrying a debt class, 4 at `needs-decision` and 57 neither. The
  57 are what the pause holds until this head says spent.

**Decided in this round**, each on a rule the repository already states:

- *It reaches the whole repository.* The owner's sentence names no half, and
  the simulator already holds it wherever a check could reach: numbers
  through `tools/literal_home_check.py` (`PL-40SJ`), colours through
  `check_colors_live_in_the_theme` in `tools/contrast_check.py`, parameters
  through the data files `core/parameters.py` validates. Nothing new is built
  under `src/` here; a second home found there is filed as `PL-40SJ`'s
  members were.
- *It is written resident*, as one bullet of `CLAUDE.md` § "Architecture and
  development discipline", beside the principles it belongs with, and
  recorded in `docs/resident-instructions.md` with what it costs. The moment
  is a session about to write a new reader, before any read a `paths:` scope
  could fire on; `PL-40SJ` found no resident sentence stating it, and the
  path-scoped rule is the one the three heads re-entered under. The closing
  sentence of § "Read the fact from its record" in
  `.claude/rules/apparatus-standard.md` is rewritten to name the check and
  keep the judgment half as prose.
- *The hooks keep a second home.* `.claude/hooks/` cannot import docket
  (`#1095` recorded why), so its one shared module, today `shell_split.py`,
  is the home for what a hook reads of git and of a Bash command, and the
  check names it as a home rather than refusing it.
- *`PL-SNQR` and `PL-9NMR` are not members.* Each is one reader diverging
  from what it reads (GitHub's trailer group; bash's reserved words), not a
  second spelling, and `PL-9NMR`'s own generator check places it under
  `PL-R417`. Both carry `feature: one-answer` by label and stay there for
  their triage.
- *`PL-PVW2`'s stale `verify:` is not filed.* It names
  `test_a_roadmap_only_branch_is_queue_work_but_not_armable`, which `#1320`
  renamed, so the command exits 1 run by hand; but `bin/docket check
  --verify` replays open items only (the two replay steps in
  `.github/workflows/quality.yml`), so `main` is not red from it, and
  `.claude/rules/citation-drift.md` makes drift in a closed brief a record
  rather than a finding.

**Decision needed.** How the principle is enforced: the one question here
whose answer adds a standing mechanism and opens a class of follow-on work.

- **A. A home-boundary check with a baseline that only shrinks.**
  `tools/fact_home_check.py`, standard library only, floor-parseable, wired
  bare beside `tools/branch_id_check.py` in `make check` and CI. It
  declares, with the reason beside each, which module owns each primitive
  that produces a shared fact, and refuses a reader outside the home: a
  `subprocess` call running `git` outside `docket.vcs` and the hooks'
  module; a call to the GitHub API outside the one client in `tools/`;
  `os.walk`, `rglob` or `git ls-files` outside the one tracked-file reader;
  an `open()` of, or a path literal under, `docs/items` outside
  `docket.model` and `docket.store`; a `main` or `origin/main` literal
  outside `docket.vcs`; `shlex` or a lexer outside `docket.shell` and
  `shell_split.py`. A second rule refuses a module-level name or table
  defined in two apparatus files, the name check `PL-5DZ8` sized at a fifth,
  folded in because it is forty lines beside the first. Today's sites go in
  a `BASELINE` keyed by file, scope and primitive, never by line, that fails
  when it grows and fails when an entry goes stale, as
  `literal_home_check.py`'s does; the 19 open members drain it, and a copy
  they remove cannot return. Effort M, the shape of
  `tools/import_boundary_check.py` (586 lines) and `literal_home_check.py`
  (525). It would have named eight of the twelve post-close members above.
- **B. The duplicate-definition rule alone.** A's second rule as its own
  tool: a name, or a literal of a pattern, path or option shape, defined in
  two apparatus files. Effort S. Finds the copies - `OPERATORS`, the cache
  names, the API headers - and none of the re-entries that reach git, the
  tree or the store with a spelling of their own: three of the twelve.
- **C. Prose alone**, made resident. What the repository has had since
  `PL-HC8P`, one tier up; the three re-entries are its measurement.

**Recommendation: A.** The number that would change it: were the next
re-entries mostly second grammars inside one tool, the four of twelve no
boundary reaches, a boundary would be upkeep for nothing and B would do.
They were not: eight of twelve reached a primitive, five of `PL-KGYT`'s six
among them. The cost A carries and B does not is an allowed list every new
legitimate home must join, the list `import_boundary_check.py` has carried
for the simulator since 2026-09-04. The hierarchy of effectiveness `PL-40SJ`
cited for the number check orders the three options the same way, forcing
functions above policy and education (Crozier N, Robinson E, Murtagh NC,
Coyne BD, *Hosp Pharm*, doi:10.1177/00185787231207995, as `PL-40SJ` cites
it), and that check has held since 2026-10-03 with no member filed against
a numeric copy.

**Decision needed.** Whether the pause this head re-engages stands until the
check lands. **Recommendation: let it stand**, and build the check in the
sitting that follows the answer, so the window is hours rather than a week:
the pause exists so that no new reader is written while nothing refuses one,
which is this head's mechanism exactly, and the 57 items it holds are
features and housekeeping that lose nothing by waiting a day. The
alternative is the owner's word lifting it for Order items 32 and 34, which
`CLAUDE.md` § "What this project is" provides for and this brief would
record.

**Why it matters.** Three heads have said spent and been followed by members,
so the store's own record says this fact is finished while it is not; each
new second spelling costs an item and, at the moment a hook or a check is
trusted, answers differently from docket's. A rule every session may read
has been the only guard for eleven days, and the fact re-entered under it.

**Done when.** Written for A; the decided form replaces this once the owner
answers. `CLAUDE.md` § "Architecture and development discipline" carries the
principle in one bullet and `docs/resident-instructions.md` records its
cost; § "Read the fact from its record" in
`.claude/rules/apparatus-standard.md` names the check and keeps the judgment
half as prose; `make check` fails on a reader of git, the GitHub API, the
tree, the item store or a shell command outside that fact's home, and on a
name or table defined in two apparatus files; the baseline only shrinks;
then `generator:` says spent and the head closes. `PL-5DZ8`'s 19 members
drain the baseline and stay their own items.

**Generator check.** The family head over `PL-PVW2`, `PL-KGYT` and
`PL-5DZ8`, which state one fact in one wording that no head named at family
altitude (`.claude/skills/docket/modes/triage.md`, the grooming pass's first
outcome): `misread:` is written in their words so the four sort together in
`bin/docket generators --misread`, and the mechanism this head names is the
one above them - nothing refuses the copy, so each sweep's remainder
re-enters. `PL-D23H` is its fourth member, a second reading filed the day
`PL-5DZ8` closed, with `reenters: PL-R417` as its other cause. This head
`reenters: PL-5DZ8`, whose spent verdict rested on the prose rule meeting a
new reader.
