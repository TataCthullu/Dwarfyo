# © 2025 Dungeon Market (Khazâd - Trading Bot)
# Todos los derechos reservados.

from codigo_principala import TradingBot
from interfaz import BotInterfaz

if __name__ == "__main__":
    bot = TradingBot()
    app = BotInterfaz(bot)
    try:
        app.run()
    except KeyboardInterrupt:
        pass

