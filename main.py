# © 2025 Dungeon M  rket (Khazâd - main)
# Todos los derechos reservados.

from codigo_principala import TradingBot
from interfaz import BotInterfaz

if __name__ == "__main__":
    bot = TradingBot()
    bot.debug_enabled = True
    bot.debug_every_loop = False
    app = BotInterfaz(bot)
    try:
        app.run()
    except KeyboardInterrupt:
        pass

