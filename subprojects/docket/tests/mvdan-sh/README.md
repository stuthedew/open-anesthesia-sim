# mvdan/sh's parse and error inputs

`cases.json` holds the 1,165 distinct shell inputs in the parser tests of
mvdan/sh, the Go shell parser behind `shfmt` (https://github.com/mvdan/sh).
`subprojects/docket/tests/test_shell.py` reads it, to hold `docket.shell` to
`bash -n` (`PL-NPPV`). The copy was taken on 2026-10-18 from commit
`c873cb44a6a0ade219d132c7dcd837ff631a4173`. `LICENSE` carries the project's
BSD 3-Clause notice. The SHA-256 of `syntax/filetests_test.go` was
`e670c49bf0aefd82bfbf8f030ba4962e78a3609be0a6a6aa472d2cf8ac7f3d93`, and that of
`syntax/parser_test.go` was
`7090d1fb06504f3881ae2d0d1dd49d03d0d86211ee0e7be645aa8aaf1ed4f437`.

Each entry keeps the input and its `source`. A `file` input is one string of a
`fileTest` in `syntax/filetests_test.go`, which mvdan/sh parses and prints. An
`error` input opens an `errCase` in the `errorCases` table of
`syntax/parser_test.go`, which mvdan/sh refuses. Its authors confirmed each
case against bash, dash, mksh and zsh, so an `error` input may still be one that
bash reads. An input that repeats an earlier one, holds a NUL or is not UTF-8
was left out.

To take it again, download those two files from
`https://raw.githubusercontent.com/mvdan/sh/COMMIT/syntax/`. Then read every Go
string literal inside each `fileTest([]string{...})`, and the first argument of
each `errCase(` after `var errorCases = []errorCase{`, decoding Go's escapes.
