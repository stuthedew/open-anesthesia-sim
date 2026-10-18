"""Where a Python statement ends: the one reading `verify` and doc_check share.

The integrity checks and doc_check's definition readers each hold the reading
to a case of their own; these hold what makes it one reading under every
interpreter that may run it (`PL-TC2D`).
"""

from __future__ import annotations

import ast
import tokenize
from collections.abc import Callable, Iterator

import pytest

from docket.arming import imports_product
from docket.python import UNTOKENIZABLE, docstrings, imports, places, read_logical_lines, refusal


def test_an_error_token_is_a_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    """3.11 hands back as an error token what 3.12 raises on, so it is refused.

    Read past, the token would leave a file split into statements one way by
    the bare `python3` docket runs on and another by the project's own. No
    source yields an error token under every interpreter, so the tokenizer is
    made to hand one back here, as 3.11's does.
    """
    real = tokenize.generate_tokens

    def handing_back_an_error(readline: Callable[[], str]) -> Iterator[tokenize.TokenInfo]:
        for token in real(readline):
            marked = token.string == "marked"
            yield token._replace(type=tokenize.ERRORTOKEN) if marked else token

    monkeypatch.setattr(tokenize, "generate_tokens", handing_back_an_error)

    with pytest.raises(UNTOKENIZABLE) as refused:
        read_logical_lines("ok = 1\nx = marked + 1\n")

    assert refusal(refused.value) == "an error token at 'marked + 1', line 2"


def test_a_formatted_string_is_one_piece_cut_as_written() -> None:
    """3.12 hands a formatted string over in parts and 3.11 as one token; both read it whole.

    Its text is the source as written, so a fold keyed on a statement's pieces
    says the same of it under either interpreter, and its code is blank.
    """
    source = 'value = f"{name!r:>{width}} {{kept}}" + "plain"\n'

    [line] = read_logical_lines(source)

    assert [piece.text for piece in line.pieces] == [
        "value",
        "=",
        'f"{name!r:>{width}} {{kept}}"',
        "+",
        '"plain"',
    ]
    assert line.code == 'value = "" + ""'


def test_a_statement_belongs_to_its_definition_and_a_decorator_to_the_one_it_decorates() -> None:
    """`PL-W6ZD`: the definition the suppression fold counts each statement in.

    A decorator of a stack, however many, belongs to the definition under it,
    as `ast` holds it in that definition's node; a statement after a nested
    definition closes belongs to the one around it again.
    """
    source = (
        "import pytest\n"
        "@pytest.mark.skip\n"
        "@pytest.mark.parametrize('a', [1])\n"
        "def test_a(a):\n"
        "    assert a\n"
        "class TestX:\n"
        "    @staticmethod\n"
        "    async def test_b():\n"
        "        pytest.skip('b')\n"
        "    pytestmark = pytest.mark.skip\n"
        "after = 1\n"
    )
    lines = read_logical_lines(source)

    assert places(lines) == (
        "",
        "test_a",
        "test_a",
        "test_a",
        "test_a",
        "TestX",
        "TestX::test_b",
        "TestX::test_b",
        "TestX::test_b",
        "TestX",
        "",
    )


def test_an_attribute_docstring_is_a_docstring() -> None:
    """`PL-8W1J`: a string standing alone under an assignment documents it.

    `glyph_check` read it as documentation, `fixture_id_check` scanned it as a
    value, and `doc_check` read no citation in it. A string that is a value is
    not documentation wherever it sits.
    """
    tree = ast.parse(
        '"""The module."""\n'
        "LIMIT = 3\n"
        '"""The attribute."""\n'
        'NAME = "a value"\n'
        "def f():\n"
        '    """The function."""\n'
        '    "a note in the body"\n'
        '    return "returned"\n'
    )

    assert [node.value for node in docstrings(tree)] == [
        "The module.",
        "The attribute.",
        "The function.",
        "a note in the body",
    ]


def test_a_literal_importlib_name_is_an_import_to_arming_and_the_boundary_check() -> None:
    """`PL-8W1J`: `importlib.import_module("anesthesia_sim.core")` imports the simulator.

    `tools/import_boundary_check.py` read the call as an import and
    `arming.imports_product` did not, so a test loading the simulator that way
    was the tooling's to `arm` and the simulator's to the boundary check.
    """
    dynamic = ast.parse('import importlib\ncore = importlib.import_module("anesthesia_sim.core")\n')
    computed = ast.parse('import importlib\ncore = importlib.import_module(NAME + ".core")\n')

    assert [entry.names for entry in imports(dynamic)] == [("importlib",), ("anesthesia_sim.core",)]
    assert imports_product(dynamic)
    assert not imports_product(computed)
    assert imports_product(ast.parse("from anesthesia_sim.core import patient\n"))
    assert not imports_product(ast.parse('"""import anesthesia_sim"""\nimport os\n'))
