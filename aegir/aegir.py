from pathlib import Path
from typing import List, Optional, Union, cast

import libcst
from libcst import BaseExpression

from aegir import FormatError, ParsedData, SourceFile
from aegir.bot_items import MainFile
from aegir.bot_items.command import Command
from aegir.bot_items.event import Event
from aegir.exceptions import InvalidDirPath
from aegir.util import Import, ImportFrom, ImportEntry


class Aegir:
    def __init__(
        self,
        dir_path: Union[str, Path],
        cog_directory_path: Optional[Path] = None,
        *,
        bot_variable: str,
    ):
        if not isinstance(dir_path, Path):
            dir_path = Path(dir_path)

        self._main_file_path: Path = dir_path.absolute()
        self._cog_directory_path: Optional[Path] = cog_directory_path

        self._main_file: Optional[MainFile] = None
        self._bot_variable: str = bot_variable

        if not self._main_file_path.exists():
            raise InvalidDirPath

        self.has_been_converted: bool = False

    @staticmethod
    def as_cst(file_path: Union[Path, str]) -> libcst.Module:
        """Parse a given file."""
        if isinstance(file_path, Path):
            source = file_path.read_text()
        else:
            source = file_path
        tree = libcst.parse_module(source)
        return tree

    @staticmethod
    def parse_out_import(cst: libcst.Import) -> Import:
        """Given an Import return the imported module name"""
        entries: List[ImportEntry] = []
        for item in cst.names:
            entries.append(ImportEntry(cst=item, item_imported=item.name.value))

        all_imports = Import(cst=cst, imports=entries)
        return all_imports

    @classmethod
    def parse_out_import_from(cls, cst: libcst.ImportFrom) -> ImportFrom:
        import_path = cls.recursive_attribute_resolution(cst.module, "")

        entries: List[ImportEntry] = []
        for item in cst.names:
            entries.append(ImportEntry(cst=item, item_imported=item.name.value))

        return ImportFrom(cst=cst, from_module=import_path, items_imported=entries)

    @classmethod
    def recursive_attribute_resolution(
        cls, cst: libcst.Attribute, imported_from: str
    ) -> str:
        if isinstance(cst, libcst.Call):
            imported_from = cls.recursive_attribute_resolution(cst.func, imported_from)  # type: ignore

        elif isinstance(cst.value, libcst.Attribute):
            # Recurse till Attr value is the base module, I.e. Nextcord
            imported_from = cls.recursive_attribute_resolution(cst.value, imported_from)

        else:
            # This should be the base package name now
            if isinstance(cst.value, libcst.Name):
                # Type check guard
                imported_from = cst.value.value

        if isinstance(cst, libcst.Name):
            imported_from = (
                f"{imported_from}.{cst.value}" if imported_from else cst.value
            )
        else:
            if not isinstance(cst, libcst.Call):
                imported_from = (
                    f"{imported_from}.{cst.attr.value}"
                    if imported_from
                    else cst.attr.value
                )

        return imported_from

    def convert(self):
        # Handle main file first
        self._main_file = MainFile(
            self._main_file_path,
            self._cog_directory_path,
            backref=self,
            bot_variable=self._bot_variable,
        )
        self._main_file.convert()

        # for file in self._dir_path.glob("**/*.py"):
        #     ast_module = self.as_ast(file)
        #     for _ast in ast_module.body:
        #         self.parse_ast(_ast)

        self.has_been_converted = True

    @classmethod
    def convert_source(cls, source: str) -> ParsedData:
        source = SourceFile(source, backref=cls)
        return source.convert()

    @property
    def errors(self) -> List[FormatError]:
        errors: List[FormatError] = []
        for event in self._main_file.events:
            errors.extend(event.errors)

        for command in self._main_file.commands:
            errors.extend(command.errors)

        return errors
