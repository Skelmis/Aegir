from typing import Union

from aegir import FormatError
from aegir.bot_items import Listener, Command, Event


class ParsedData:
    def __init__(
        self,
        *,
        commands: list[Command],
        errors: list[FormatError],
        events: list[Union[Event, Listener]],
    ):
        self.commands: list[Command] = commands
        self.errors: list[FormatError] = errors
        self.events: list[Union[Event, Listener]] = events
