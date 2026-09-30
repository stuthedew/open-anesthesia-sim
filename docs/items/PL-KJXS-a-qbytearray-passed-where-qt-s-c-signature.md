---
id: PL-KJXS
title: A QByteArray passed where Qt's C++ signature takes QByteArray *, at any of the six entry points PL-NDKC measured, is a use-after-free that segfaults or reads silently wrong zeros, and nothing fails make check when src/ writes one
priority: P3
effort: M
status: ready
classes: infra
feature: qbytearray-pointer-trap
touches: tools/qbytearray_pointer_check.py, tests/unit/test_qbytearray_pointer_check.py, Makefile, .github/workflows/quality.yml, docket.toml
added: 2026-09-26
payoff: a QByteArray handed to one of the six Qt entry points that keep a pointer to it fails make check when it is written, instead of segfaulting or reading silent zeros at run time
verify: grep -rq 'def test_a_qbytearray_where_qt_keeps_a_pointer_fails' tests/unit/
recurrences: 2026-09-30 PL-NDGS withdrawn 2026-09-30 PL-NDGS
---

**Problem.** Six Qt entry points keep the `QByteArray *` they are given, and
PySide6 6.11.2 keeps no reference to the array at any of them, so an array
nothing else holds is freed while Qt still points at it. `PL-NDKC`'s thread in
`docs/WORKING_NOTES.md` measured the outcomes - segfaults, and zeros read back
with `status()` still `Ok` - and states the rule: never pass a `QByteArray`
where Qt's C++ signature takes `QByteArray *`. Nothing under `src/` or `tests/`
does it on 2026-09-26, and nothing would fail `make check` if something did.

The six, as the Python calls that bind them:

- `QBuffer(array)` and `buffer.setBuffer(array)`;
- `QDataStream(array, mode)`, with two arguments only - the one-argument
  `QDataStream(array)` binds `const QByteArray &` and copies;
- `QTextStream(array)` and `QTextStream(array, mode)` - both, because PySide6
  removes the copying overload Qt has;
- `QXmlStreamWriter(array)` and `QCborStreamWriter(array)`.

**The design question is types.** A call does not show its overload.
`QTextStream`, `QXmlStreamWriter` and `QCborStreamWriter` also take a
`QIODevice`, and `QBuffer` a parent `QObject`, which are the safe forms, and a
check reading the syntax tree cannot tell `QTextStream(device)` from
`QTextStream(array)` without inferring the argument's type. So it chooses
between flagging every such call with a way to mark the safe ones, and matching
only arguments it can see are `QByteArray`s. `QDataStream`'s split by argument
count and `setBuffer` are the decidable cases.

**Why it matters.** Both outcomes are the kind the safety-critical standard
ranks worst: a crash, or zeros read back with `status()` still `Ok` - a
plausible wrong value with no error. The rule exists only as prose in
`PL-NDKC`'s thread in `docs/WORKING_NOTES.md`, which a session writing the call
has no reason to open, and the thread names the first likely site: a drag
payload for `PL-2KXB`'s Area swap, where Qt's own
Draggable Icons example becomes the trap when ported to Python. A check puts
the rule where the call is written, before any site exists.

**Done when.** `make check` fails on each of the six Python call forms above
under `src/` and `tests/`, and passes on the safe forms the thread lists: the
one-argument `QDataStream`, `QBuffer()` with `setData`, and a `QIODevice`
argument.

The check parses `src/` and `tests/`, which are 3.14 source, so it runs under
`uv run python` as `tools/import_boundary_check.py` does, in both `make check`
and `quality.yml`, which gate parity requires. Whether it infers an argument's
type or flags every overloaded call with a way to mark the safe ones is the
implementing session's choice; the Done-when above holds either way.
