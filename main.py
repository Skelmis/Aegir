from pathlib import Path

from aegir import Aegir

Aegir(Path("test/main.py"), bot_variable="bot").convert()
