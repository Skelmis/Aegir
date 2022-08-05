from enum import Enum


class RunMode(Enum):
    bot_run = 1
    asyncio_run = 2
    unknown = 3
