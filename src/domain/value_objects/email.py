import re

from src.domain.exceptions.domain_exceptions import EmailInvalidoError


class Email:
    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, valor: str) -> None:
        self._valor = self._validar(valor)

    @property
    def valor(self) -> str:
        return self._valor

    def _validar(self, valor: str) -> str:
        valor = valor.strip()
        if not self._EMAIL_PATTERN.match(valor):
            raise EmailInvalidoError(valor)
        return valor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self._valor == other._valor

    def __hash__(self) -> int:
        return hash(self._valor)

    def __str__(self) -> str:
        return self._valor

    def __repr__(self) -> str:
        return f"Email({self._valor!r})"
