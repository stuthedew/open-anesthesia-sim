---
id: PL-SR8F
title: docs/MODEL.md calls the case-opening displacement 'two orders milder at every rate' but the figures in the same sentence are 0.8 to 1.3 orders apart, so a reader sizing the ordinary manoeuvre against the binding one is told the wrong ratio
priority: P1
effort: S
status: done
classes: safety, docs
feature: presentation-safety
touches: docs/MODEL.md
added: 2026-09-06
pr: 420
closed: 2026-09-07
verify: python3 tools/doc_check.py check && python3 -c "import pathlib; t=' '.join(pathlib.Path('docs/MODEL.md').read_text().split()); raise SystemExit(1 if 'two orders milder' in t else 0)"
---

**Problem.** `docs/MODEL.md` § "Supported simulation step" reads, under the
playback-rate displacement table: "The binding case is the ventilator start
with desflurane throughout; the case opening is two orders milder at every
rate, reaching 1.5 pp at 300x." The measurements in that section do not
support "two orders", and they contradict it at both ends of the rate ladder:

| Rate | Ventilator start (binding) | Case opening | Separation |
| --- | --- | --- | --- |
| 1x (0.1 s step) | 1.4x10^-1 pp | 6.7x10^-3 pp | 21x, 1.3 orders |
| 300x | 1.0x10^1 pp | 1.5 pp | 6.7x, 0.8 orders |

The 1x figures are the section's own manoeuvre table; the 300x figures are the
rate table and the sentence itself. So the claimed ratio is wrong at every
rate, by between five and fifteen times, and it is furthest wrong exactly
where the sentence quotes a number.

**Why it matters.** The table this sentence glosses is a safety claim, not a
performance note: it bounds how far a displayed value can sit from the value
the model would show had a control change acted at the instant it was made,
which is what a reader consults to decide whether a number on screen can be
trusted during a manoeuvre. A reader who takes "two orders milder" at face
value sizes the ordinary manoeuvre - opening the case - at about 0.1 pp at
300x when the measured figure is 1.5 pp, understating the displacement of the
common action by more than an order of magnitude. `CLAUDE.md`'s safety-critical
standard counts a misleading statement about a displayed value as a
presentation failure whatever the underlying number does, and `docs/MODEL.md`
is the specification a reader checks the display against.

**Where.** `docs/MODEL.md`, the sentence at lines 1009-1011 under the
playback-rate table in § "Supported simulation step"; the manoeuvre table at
lines 950-954 in the same section carries the 1x figures the ratio is computed
from.

**Done when.** The sentence states the separation the measurements support -
the range across rates, or the ratio at the rate it quotes - and asserts no
figure the numbers beside it contradict. Verified 2026-09-06 against the two
tables; `PL-ZVS7` (the control-resolution tolerance table is a measured safety
claim with no regression test) is what would keep it true afterwards, and this
item only makes it true now.

**The `verify:` command normalizes whitespace before looking for the claim**, so
rewrapping the paragraph does not satisfy it. Run 2026-09-06 before the work:
exit 1, `doc_check` passing and the phrase present.

**Closed 2026-09-07 as already done, under `PL-CL8J`.** The work landed in
`67b279b` (#420, `PL-ZVS7`, which pinned the control-resolution tolerance table
with a reference test). That gate's first run found this same wrong claim, so
the correction rode it rather than this item.

Substance verified rather than inferred from the phrase's absence, this being
`classes: safety`. `docs/MODEL.md` § "Supported simulation step" now reads: "the
case opening is about 21x milder at 1x, and **the gap narrows as the grid
coarsens** - to 19x at 20x, 16x at 60x and about 7x at 300x". That is the
per-rate relation this item asked for, in place of the "two orders milder at
every rate" that held at no rate.

Established by replaying all 80 commits touching `docs/MODEL.md` under the same
whitespace normalisation this item's own `verify:` command uses. That
normalisation is load-bearing: the phrase was hard-wrapped in the source, so
`grep` and `git log -S` both report it absent from every revision. `PL-0ZGK`
independently named `67b279b`, and the replay agrees.
