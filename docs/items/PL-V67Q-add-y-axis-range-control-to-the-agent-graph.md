---
id: PL-V67Q
title: Add y-axis range control to the agent graph: optional auto-scale, and a settable MAC / volume-percent scale
status: untriaged
added: 2026-09-08
---

**Problem.** Add y-axis range control to the agent graph: optional auto-scale, and a settable MAC / volume-percent scale

Raised by the project owner, 2026-09-08, as a passing want rather than a
scoped request: the agent graph's y-axis should either auto-scale to the
data or be set explicitly, for MAC and for volume-percent values.

**Two mechanisms, and they are not alternatives.** A plotting surface that
offers "auto" normally also offers "fixed", because each fails where the
other works: a fixed axis wastes most of its height on a low-dose case, and
an auto axis makes a 0.05 % drift fill the plot. The item is one feature
with a mode, not a choice between two features.

**Open questions for the design round, not answered here.**

- Do MAC and volume-percent share one axis, or does each get its own range?
  They are different units, and a single control governing both would have
  to say which one it is setting.
- What are the fixed defaults, and are they per-agent? Sevoflurane at 2 %
  and desflurane at 6 % are the same MAC-ish depth on very different
  volume-percent scales, so one fixed volume-percent range across agents is
  either too tall for one or clips the other.
- Does the range persist across a run, or reset with it?

**Auto-scale is the half with a safety-critical edge, and it is why this is
not a pure convenience item.** An axis that rescales itself changes what the
same physiology looks like: a trace that is visually flat under a 0-3 MAC
axis becomes a dramatic climb the moment the axis shrinks to the data, and
nothing about the patient changed. Two consequences follow, both to be
settled when the item is worked rather than assumed now — whether auto is
off by default and visibly marked when on, and whether the axis limits are
readable on the plot itself rather than only in a settings panel. This sits
squarely under `CLAUDE.md`'s clinical-output standard ("a visually
attractive but misleading graph is a defect") and under
`.claude/rules/expert-review.md`'s data-visualization domain. The design
round owes a look at the actual human-factors literature on autoscaling
trend displays; nothing here has consulted it.
