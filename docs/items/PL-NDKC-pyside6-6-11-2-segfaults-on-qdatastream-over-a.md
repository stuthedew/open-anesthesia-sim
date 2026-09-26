---
id: PL-NDKC
title: PySide6 6.11.2 segfaults on QDataStream over a temporary QByteArray, and a QBuffer over one reads zeros with status Ok, which the first Qt code to decode a byte payload will meet
priority: P3
effort: S
status: done
classes: defect, infra
feature: interface-areas
touches: docs/WORKING_NOTES.md, ROADMAP.md
added: 2026-09-16
closed: 2026-09-26
verify: grep -qF 'QBuffer::readData' docs/WORKING_NOTES.md && python3 tools/doc_check.py check
---

**Problem.** On PySide6 6.11.2 / Qt 6.11.2,
`QDataStream(QByteArray(blob), QIODevice.OpenModeFlag.ReadOnly)` segfaults on
its first read, inside `QBuffer::readData`, and `QBuffer(QByteArray(blob))` read
through a stream returns zeros with `status()` still `Ok`. Both constructors
keep a pointer to the caller's array, Qt makes the caller responsible for
keeping it alive, and PySide6 declares nothing to keep it alive, so a temporary
is freed as soon as the constructor returns. Binding the array to a name first
avoids both.

**Why it matters.** Found 2026-09-16 while decoding `QSplitter.saveState()`
blobs for the v0.6.0 scoping. The segfault is the lesser half: the `QBuffer`
door hands back a plausible wrong value and no error, which is the failure shape
this project's standard ranks below an obvious one. The brief as filed placed
the first encounter in `PL-SSQW`'s persistence work, but `PL-C842` has since
made the saved workspace versioned JSON written from a pure-Python
`LayoutModel`, and v0.6.0's adapter calls no `saveState()`, so that path decodes
no Qt blob. Where it would be met is the Qt code built around the model: a drag
payload for `PL-2KXB`'s Area swap, a geometry blob if `PL-Y04W`'s break-out
persists window placement that way, or a test that decodes a Qt state blob, as
the 2026-09-16 measurement did. None of it exists yet.

**Done when.** The reproduction, the measured outcome of each constructor form
and the workaround are recorded in `docs/WORKING_NOTES.md`, in a thread naming
the items whose Qt code could construct such a stream so that `bin/docket show`
points each of them at it, with the PySide6, Qt and Python versions measured
against.

*Re-confirmed 2026-09-26, changed shape.* The crash reproduces as filed, 25 runs
of 25. The forecast that the persistence work meets it did not survive
`PL-C842`, and a second door, `QBuffer`, turned out to read silently wrong
rather than crash, so the brief above replaces the one filed.
