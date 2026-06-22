from decimal import Decimal

import pytest

from src.domain.exceptions.domain_exceptions import DinheiroNegativoError
from src.domain.value_objects.dinheiro import Dinheiro


class TestDinheiro:
    def test_criar_dinheiro_com_decimal(self) -> None:
        d = Dinheiro(Decimal("10.50"))
        assert d.valor == Decimal("10.50")

    def test_criar_dinheiro_com_float(self) -> None:
        d = Dinheiro(10.5)
        assert d.valor == Decimal("10.50")

    def test_criar_dinheiro_com_int(self) -> None:
        d = Dinheiro(100)
        assert d.valor == Decimal("100.00")

    def test_criar_dinheiro_com_string(self) -> None:
        d = Dinheiro("99.99")
        assert d.valor == Decimal("99.99")

    def test_dinheiro_negativo_raises_error(self) -> None:
        with pytest.raises(DinheiroNegativoError):
            Dinheiro(-10)

    def test_dinheiro_zero_e_valido(self) -> None:
        d = Dinheiro(0)
        assert d.valor == Decimal("0.00")

    def test_somar(self) -> None:
        resultado = Dinheiro(10).somar(Dinheiro(20))
        assert resultado.valor == Decimal("30.00")

    def test_subtrair(self) -> None:
        resultado = Dinheiro(30).subtrair(Dinheiro(10))
        assert resultado.valor == Decimal("20.00")

    def test_subtrair_resultando_negativo_raises(self) -> None:
        with pytest.raises(DinheiroNegativoError):
            Dinheiro(10).subtrair(Dinheiro(20))

    def test_multiplicar(self) -> None:
        resultado = Dinheiro(10).multiplicar(3)
        assert resultado.valor == Decimal("30.00")

    def test_multiplicar_por_zero(self) -> None:
        resultado = Dinheiro(10).multiplicar(0)
        assert resultado.valor == Decimal("0.00")

    def test_igualdade(self) -> None:
        assert Dinheiro(10) == Dinheiro("10.00")

    def test_comparacao_maior(self) -> None:
        assert Dinheiro(20) > Dinheiro(10)

    def test_comparacao_menor_ou_igual(self) -> None:
        assert Dinheiro(10) <= Dinheiro(10)
        assert Dinheiro(5) <= Dinheiro(10)

    def test_str_formatado(self) -> None:
        assert str(Dinheiro(10.5)) == "R$ 10.50"

    def test_arredondamento_duas_casas(self) -> None:
        d = Dinheiro("10.999")
        assert d.valor == Decimal("11.00")
