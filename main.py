from pathlib import Path

from aegir import Aegir

aegir = Aegir(Path("test/main.py"), bot_variable="bot")
aegir.convert()
print(aegir.errors)
