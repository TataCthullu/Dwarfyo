# player.py

from dataclasses import dataclass, field
from typing import Dict

# avatar base por defecto
DEFAULT_AVATAR_ID = "dwarf_male"


@dataclass
class Inventory:
    items: Dict[str, int] = field(default_factory=dict)
    equipped: Dict[str, str] = field(default_factory=dict)


@dataclass
class Settings:
    music: bool = True
    sound: bool = True
    decimals: int = 2


@dataclass
class Loadout:
    avatar_id: str = DEFAULT_AVATAR_ID

    # representaciones visuales del bot
    tp_item: str = "tp_base"
    sl_item: str = "sl_base"
    hodl_staff: str = "hodl_base"


@dataclass
class Player:
    username: str

    loadout: Loadout = field(default_factory=Loadout)
    inventory: Inventory = field(default_factory=Inventory)
    settings: Settings = field(default_factory=Settings)

    def __repr__(self):
        return f"<Player {self.username}>"
