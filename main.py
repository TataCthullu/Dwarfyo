# © 2025 Khazâd Trading Bot
# Todos los derechos reservados.

from codigo_principala import TradingBot
from interfaz import BotInterface

if __name__ == "__main__":
    bot = TradingBot()
    app = BotInterface(bot)
    app.run()

