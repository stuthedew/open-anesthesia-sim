"""Which model and reasoning effort each kind of work uses, read from one table.

The table is `docket.toml`'s `[models]`, and this module is its one reader
(`PL-0XDM`). The project owner asked for it on 2026-10-25: "Make things that
say which model and effort to use use a single source of truth", and "it will
need to be extendible because may end up wanting this model or strength for
this arbitrary category(ies) and a different default".

So the table holds a default model and effort, and an ordered list of rules
that override them. A rule's `match` names any categories, and a reader passes
the facts it knows as a mapping from category to value. A rule holds when
every category it names has the value it gives, and the first rule that holds
decides. A new category is therefore a data edit: a reader that knows the fact
passes it, and a rule that names a category no reader passes never holds.

`areas` names parts of the tree by path, so a rule can match where the work
is, such as the simulator's core against the interface. An item's areas are
those its `touches` reach.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass

from .model import Item, is_under

#: The table's name in `docket.toml`.
MODELS_TABLE = "models"
#: The keys the table may hold.
TABLE_KEYS = frozenset({"default", "areas", "prices", "rule"})
#: The keys a rule may hold. `match` is required, with `model`, `effort` or both.
RULE_KEYS = frozenset({"match", "model", "effort", "why"})
#: The effort levels Claude Code accepts, lowest first (Claude Code docs,
#: "Model configuration", section "Adjust effort level",
#: https://code.claude.com/docs/en/model-config, read 2026-10-19).
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")

#: What a reader knows about the work: each category's value, or several
#: values where the work has more than one, such as an item's classes.
Facts = Mapping[str, str | Collection[str]]


@dataclass(frozen=True)
class Choice:
    """The model and effort the table chose, and which rule chose them."""

    model: str
    effort: str
    #: The deciding rule's position in the table, counted from 1, or `None`
    #: where no rule held and the default decided.
    rule: int | None

    def describe(self) -> str:
        """The choice as `next` and `show` print it."""
        return f"{self.model} at {self.effort} effort"


@dataclass(frozen=True)
class ModelRule:
    """One override: the facts it needs, and the model or effort it sets."""

    match: tuple[tuple[str, str], ...]
    model: str | None
    effort: str | None

    def holds(self, facts: Facts) -> bool:
        """Whether every category this rule names has the value it gives."""
        for category, value in self.match:
            fact = facts.get(category)
            if fact is None:
                return False
            if isinstance(fact, str):
                if fact != value:
                    return False
            elif value not in fact:
                return False
        return True


@dataclass(frozen=True)
class ModelTable:
    """The `[models]` table of `docket.toml`."""

    model: str
    effort: str
    #: Each area's name and the paths it covers.
    areas: tuple[tuple[str, tuple[str, ...]], ...] = ()
    rules: tuple[ModelRule, ...] = ()
    #: Each model's list price, as the model id with its input and output
    #: prices in US dollars per million tokens. A tool that spends API credit
    #: bounds its cost from these, so a model the table chooses has its price
    #: beside it rather than in the tool.
    prices: tuple[tuple[str, float, float], ...] = ()

    def price(self, model: str) -> tuple[float, float] | None:
        """The input and output list price of `model` per million tokens, or `None`."""
        return next(((i, o) for name, i, o in self.prices if name == model), None)

    def areas_of(self, paths: Collection[str]) -> frozenset[str]:
        """The areas any of `paths` reaches.

        A path reaches an area when it lies inside one of the area's paths, or
        when it is a directory holding one, since work declared on `src/` may
        change anything under it.
        """
        reached: set[str] = set()
        for name, roots in self.areas:
            for path in paths:
                if is_under(path, roots) or any(is_under(root, (path,)) for root in roots):
                    reached.add(name)
        return frozenset(reached)

    def choose(self, facts: Facts) -> Choice:
        """Return the first rule that holds for these facts, or the default."""
        for position, rule in enumerate(self.rules, start=1):
            if rule.holds(facts):
                return Choice(rule.model or self.model, rule.effort or self.effort, position)
        return Choice(self.model, self.effort, None)


def item_facts(
    item: Item, table: ModelTable, workflow_paths: tuple[str, ...], *, delegable: bool
) -> dict[str, str | frozenset[str]]:
    """The facts an item gives the table.

    `role` is `strongest` where `Item.model_guidance` asks for the strongest
    model, `delegable` where a cheaper model may take the item, and empty
    otherwise. `size` is the item's `effort:` field, named apart from the
    reasoning effort the table sets.
    """
    if item.model_guidance is not None:
        role = "strongest"
    elif delegable:
        role = "delegable"
    else:
        role = ""
    return {
        "class": frozenset(item.classes),
        "lane": item.lane(workflow_paths),
        "feature": item.feature,
        "status": item.status,
        "size": item.effort,
        "area": table.areas_of(item.touches),
        "role": role,
    }


def parse(data: Mapping[str, object], source: str) -> ModelTable:
    """Read a parsed `[models]` table, refusing anything malformed.

    A malformed entry is refused rather than skipped, for the reason a
    malformed `docket.toml` is: a rule that looks applied but is not is worse
    than none.
    """
    unknown = sorted(set(data) - TABLE_KEYS)
    if unknown:
        raise ValueError(f"{source}: [{MODELS_TABLE}] has no key named {', '.join(unknown)}")
    default = data.get("default")
    if not isinstance(default, dict) or set(default) != {"model", "effort"}:
        raise ValueError(
            f"{source}: [{MODELS_TABLE}] default must name exactly `model` and `effort`"
        )
    model = _model(default["model"], f"{source}: [{MODELS_TABLE}] default.model")
    effort = _effort(default["effort"], f"{source}: [{MODELS_TABLE}] default.effort")
    areas_data = data.get("areas", {})
    if not isinstance(areas_data, dict):
        raise ValueError(f"{source}: [{MODELS_TABLE}.areas] must be a table of path lists")
    areas = tuple(
        (name, _strings(paths, f"{source}: [{MODELS_TABLE}.areas] {name}"))
        for name, paths in areas_data.items()
    )
    rows = data.get("rule", [])
    if not isinstance(rows, list):
        raise ValueError(
            f"{source}: `{MODELS_TABLE}.rule` must be an array of tables, [[{MODELS_TABLE}.rule]]"
        )
    names = {name for name, _ in areas}
    rules = tuple(
        _rule(row, names, f"{source}: [[{MODELS_TABLE}.rule]] {n}") for n, row in enumerate(rows, 1)
    )
    prices_data = data.get("prices", {})
    if not isinstance(prices_data, dict):
        raise ValueError(f"{source}: [{MODELS_TABLE}.prices] must be a table of model prices")
    prices = tuple(
        (name, *_price(entry, f"{source}: [{MODELS_TABLE}.prices] {name}"))
        for name, entry in prices_data.items()
    )
    return ModelTable(model, effort, areas, rules, prices)


def _price(entry: object, where: str) -> tuple[float, float]:
    if not isinstance(entry, dict) or set(entry) != {"input", "output"}:
        raise ValueError(f"{where} must name exactly `input` and `output`, in US dollars")
    values = []
    for key in ("input", "output"):
        value = entry[key]
        if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
            raise ValueError(f"{where}: `{key}` must be a positive number of US dollars")
        values.append(float(value))
    return values[0], values[1]


def _rule(row: object, areas: Collection[str], where: str) -> ModelRule:
    if not isinstance(row, dict):
        raise ValueError(f"{where} is not a table")
    unknown = sorted(set(row) - RULE_KEYS)
    if unknown:
        raise ValueError(f"{where} has no key named {', '.join(unknown)}")
    match = row.get("match")
    if not isinstance(match, dict) or not match:
        raise ValueError(f"{where}: `match` must be a table naming at least one category")
    pairs: list[tuple[str, str]] = []
    for category, value in match.items():
        if not isinstance(value, str) or not value:
            raise ValueError(f"{where}: `match.{category}` must be a non-empty string")
        if category == "area" and value not in areas:
            raise ValueError(
                f"{where}: `match.area` is {value!r}, which [{MODELS_TABLE}.areas] does not name"
            )
        pairs.append((category, value))
    if "model" not in row and "effort" not in row:
        raise ValueError(f"{where} sets neither `model` nor `effort`")
    model = _model(row["model"], f"{where}: model") if "model" in row else None
    effort = _effort(row["effort"], f"{where}: effort") if "effort" in row else None
    return ModelRule(tuple(pairs), model, effort)


def _model(value: object, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where} must be a model id, as `[models.prices]` names one")
    return value


def _effort(value: object, where: str) -> str:
    if value not in EFFORT_LEVELS:
        raise ValueError(f"{where} is {value!r}, not one of {', '.join(EFFORT_LEVELS)}")
    return str(value)


def _strings(value: object, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
        raise ValueError(f"{where} must be a list of non-empty strings")
    return tuple(value)
