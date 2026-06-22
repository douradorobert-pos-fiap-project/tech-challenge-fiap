import re

from src.domain.exceptions.domain_exceptions import PlacaInvalidaError


class Placa:
    _PLACA_MERCOSUL_PATTERN = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")
    _PLACA_ANTIGA_PATTERN = re.compile(r"^[A-Z]{3}[0-9]{4}$")

    def __init__(self, valor: str) -> None:
        self._valor = self._validar(valor)

    @property
    def valor(self) -> str:
        return self._valor

    @property
    def is_mercosul(self) -> bool:
        return bool(self._PLACA_MERCOSUL_PATTERN.match(self._valor))

    def _validar(self, valor: str) -> str:
        valor = valor.upper().replace("-", "").replace(" ", "")

        if self._PLACA_MERCOSUL_PATTERN.match(valor):
            return valor

        if self._PLACA_ANTIGA_PATTERN.match(valor):
            return valor

        raise PlacaInvalidaError(valor)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Placa):
            return False
        return self._valor == other._valor

    def __hash__(self) -> int:
        return hash(self._valor)

    def __str__(self) -> str:
        return self._valor

    def __repr__(self) -> str:
        return f"Placa({self._valor!r})"
