from typing import NamedTuple, List

import libcst


class ImportEntry(NamedTuple):
    item_imported: str
    cst: libcst.ImportAlias


class Import(NamedTuple):
    imports: List[ImportEntry]
    cst: libcst.Import


class ImportFrom(NamedTuple):
    from_module: str
    items_imported: List[ImportEntry]
    cst: libcst.ImportFrom
