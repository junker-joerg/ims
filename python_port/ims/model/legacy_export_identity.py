from typing import TypeAlias


ExportSelectorValue: TypeAlias = int | str | None
ExportIdentity: TypeAlias = tuple[str, str, str, str, ExportSelectorValue]

LEVEL_IV_SELECTOR_KIND = "all"
LEVEL_IV_CANONICAL_SELECTOR_VALUE = "SK1"
LEVEL_IV_SELECTOR_ALIASES = frozenset({"all", LEVEL_IV_CANONICAL_SELECTOR_VALUE})


def canonicalize_legacy_export_selector(
    level: str,
    selector_kind: str,
    selector_value: ExportSelectorValue,
) -> ExportSelectorValue:
    if (
        level == "IV"
        and selector_kind == LEVEL_IV_SELECTOR_KIND
        and selector_value in LEVEL_IV_SELECTOR_ALIASES
    ):
        return LEVEL_IV_CANONICAL_SELECTOR_VALUE
    return selector_value


def build_legacy_export_identity(
    filename: str,
    subject_type: str,
    level: str,
    selector_kind: str,
    selector_value: ExportSelectorValue,
) -> ExportIdentity:
    return (
        filename,
        subject_type,
        level,
        selector_kind,
        canonicalize_legacy_export_selector(level, selector_kind, selector_value),
    )


def format_legacy_export_identity(identity: ExportIdentity) -> str:
    filename, subject_type, level, selector_kind, selector_value = identity
    return f"{filename} ({subject_type}/{level}/{selector_kind}={selector_value})"
