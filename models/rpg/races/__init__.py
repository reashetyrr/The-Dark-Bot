from .Demon import Demon
from .Elves import DarkElf, HighElf, WoodElf, SnowElf
from .Goblin import Goblin
from .God import God
from .Human import Human
from .Imp import Imp
from .Dwarf import Dwarf
from .Khajit import Khajit
from .Orc import Orc
from .Argonian import Argonian


races = [
    Demon.__name__,
    DarkElf.__name__,
    HighElf.__name__,
    SnowElf.__name__,
    WoodElf.__name__,
    Goblin.__name__,
    God.__name__,
    Human.__name__,
    Imp.__name__,
    Dwarf.__name__,
    Khajit.__name__,
    Orc.__name__,
    Argonian.__name__,
]

selectable = [
    DarkElf.__name__,
    HighElf.__name__,
    WoodElf.__name__,
    Human.__name__,
    Khajit.__name__,
    Argonian.__name__,
]
