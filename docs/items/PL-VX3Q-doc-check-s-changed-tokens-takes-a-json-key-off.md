---
id: PL-VX3Q
title: doc_check's changed_tokens takes a JSON key off the one diff line it reads, so a changed value continued past its key's line - an array entry, or a key whose colon sits on the next line - seeds no key term, and documents naming that key are left off the candidates list; live in form
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** doc_check's changed_tokens takes a JSON key off the one diff line it reads, so a changed value continued past its key's line - an array entry, or a key whose colon sits on the next line - seeds no key term, and documents naming that key are left off the candidates list; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s third part.
`changed_tokens` seeds the close-out's candidates list from a diff, and for a
`.json` file it reads a key with `JSON_KEY_RE` off each changed line. JSON
allows whitespace, newlines included, between any two tokens (RFC 8259 § 2),
so the key a changed value belongs to can stand lines above it, and a key's
colon can stand on the next line.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against `json.loads`:

```text
"blood_gas_partition": [
  0.65,
  0.69
]
(0.69 changed to 0.70)

"renamed_key"
    : 2
```

Each gives only the file's name and stem as terms, where the same change on
one line gives the key too. Live in form: 27 value lines in the eight tracked
`.json` files hold no key on their line (one in `.claude/settings.json`), so
editing any of them seeds no key term; nothing on the list was wrong today.
A parameter file's value changed inside an array is the case this list exists
to catch, since the documents that state the value are the ones to re-read.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the JSON
twin of closed `PL-V2HK`'s Python fix.

**Done when.** A changed JSON line seeds the key path `json` gives the value
it sits in (both files parsed, the changed values located), or the file is
declined by name; a test pins both forms above.
