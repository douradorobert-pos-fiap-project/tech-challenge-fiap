from decimal import Decimal

from src.domain.exceptions.domain_exceptions import DinheiroNegativoError


class Dinheiro:
    _CASAS_DECIMAIS = 2

    def __init__(self, valor: Decimal | float | int | str) -> None:
        valor_decimal = Decimal(str(valor))
        if valor_decimal < 0:
            raise DinheiroNegativoError(str(valor))
        self._valor = valor_decimal.quantize(Decimal(f"0.{'0' * self._CASAS_DECIMAIS}"))

    @property
    def valor(self) -> Decimal:
        return self._valor

    def somar(self, outro: "Dinheiro") -> "Dinheiro":
        return Dinheiro(self._valor + outro._valor)

    def subtrair(self, outro: "Dinheiro") -> "Dinheiro":
        resultado = self._valor - outro._valor
        if resultado < 0:
            raise DinheiroNegativoError(str(resultado))
        return Dinheiro(resultado)

    def multiplicar(self, fator: int | float | Decimal) -> "Dinheiro":
        if isinstance(fator, (int, float)):
            fator = Decimal(str(fator))
        resultado = self._valor * fator
        if resultado < 0:
            raise DinheiroNegativoError(str(resultado))
        return Dinheiro(resultado)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dinheiro):
            return False
        return self._valor == other._valor

    def __lt__(self, other: "Dinheiro") -> bool:
        return self._valor < other._valor

    def __le__(self, other: "Dinheiro") -> bool:
        return self._valor <= other._valor

    def __gt__(self, other: "Dinheiro") -> bool:
        return self._valor > other._valor

    def __ge__(self, other: "Dinheiro") -> bool:
        return self._valor >= other._valor

    def __hash__(self) -> int:
        return hash(self._valor)

    def __str__(self) -> str:
        return f"R$ {self._valor:.2f}"

    def __repr__(self) -> str:
        return f"Dinheiro({self._valor!r})"
