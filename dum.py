# © 2025 Dungeon Market (Dum) 
# Todos los derechos reservados.

from __future__ import annotations


from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional, Any


SLOT_1_OBSIDIANA = Decimal("5000")


@dataclass(frozen=True)
class DumResultado:
    usuario: str
    motivo: str
    slot: Decimal
    resultado_total: Decimal       # total final (equivalente USDT) leído del bot
    obsidiana_vuelve: Decimal      # lo que vuelve a la cuenta como Obsidiana (<= slot)
    quad_ganado: Decimal           # excedente (>= 0), NO reinvertible


class DumTranslator:
    def __init__(
        self,
        slot_1: Decimal = SLOT_1_OBSIDIANA,
        persist_callback: Optional[Callable[[DumResultado], None]] = None,
    ):
        self.slot_1 = self._to_decimal(slot_1)
        self.persist_callback = persist_callback

    def cerrar_run(self, usuario: str, bot: Any, motivo: str = "detener") -> DumResultado:
        total = self._leer_total_bot(bot)
        raw = getattr(bot, "_dum_slot_frozen", None)
        if raw is None:
            raw = getattr(bot, "dum_slot_used", None)

        if raw is None:
            slot = self.slot_1
        else:
            slot = self._to_decimal(raw)

        if slot < 0:
            slot = Decimal("0")
        if slot > self.slot_1:
            slot = self.slot_1

        if total > slot:
            quad = total - slot
            obsidiana = slot
        else:
            quad = Decimal("0")
            obsidiana = total

        resultado = DumResultado(
            usuario=str(usuario),
            motivo=str(motivo),
            slot=slot,
            resultado_total=total,
            obsidiana_vuelve=obsidiana,
            quad_ganado=quad,
        )

        if self.persist_callback:
            self.persist_callback(resultado)

        return resultado

    # ----------------- helpers -----------------

    def _leer_total_bot(self, bot: Any) -> Decimal:
        # 1) preferir un total ya calculado por el bot (si existe)
        for attr in ("resultado_total", "total_final", "balance_total", "valor_total", "equity_usdt", "total_usdt"):
            if hasattr(bot, attr):
                return self._to_decimal(getattr(bot, attr, 0))

        # 2) fallback: usdt + btc_usdt (solo si tu bot los mantiene coherentes)
        usdt = self._to_decimal(getattr(bot, "usdt", 0))
        btc_usdt = self._to_decimal(getattr(bot, "btc_usdt", 0))
        return usdt + btc_usdt

    def _to_decimal(self, value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        try:
            # str(...) evita issues típicos de float binario
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")
