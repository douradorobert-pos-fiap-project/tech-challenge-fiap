import pytest

from src.domain.exceptions.domain_exceptions import PlacaInvalidaError
from src.domain.value_objects.placa import Placa


class TestPlaca:
    def test_placa_mercosul_valida(self) -> None:
        placa = Placa("ABC1D23")
        assert placa.valor == "ABC1D23"
        assert placa.is_mercosul is True

    def test_placa_mercosul_com_espacos(self) -> None:
        placa = Placa("  ABC1D23  ")
        assert placa.valor == "ABC1D23"

    def test_placa_antiga_valida(self) -> None:
        placa = Placa("ABC1234")
        assert placa.valor == "ABC1234"
        assert placa.is_mercosul is False

    def test_placa_minuscula_e_normalizada(self) -> None:
        placa = Placa("abc1d23")
        assert placa.valor == "ABC1D23"

    def test_placa_com_hifen(self) -> None:
        placa = Placa("ABC-1D23")
        assert placa.valor == "ABC1D23"

    def test_placa_invalida_muito_curta(self) -> None:
        with pytest.raises(PlacaInvalidaError):
            Placa("ABC")

    def test_placa_invalida_muito_longa(self) -> None:
        with pytest.raises(PlacaInvalidaError):
            Placa("ABC1D2345")

    def test_placa_invalida_formato_completo_errado(self) -> None:
        with pytest.raises(PlacaInvalidaError):
            Placa("12ABCD3")

    def test_placa_vazia(self) -> None:
        with pytest.raises(PlacaInvalidaError):
            Placa("")

    def test_igualdade_entre_placas(self) -> None:
        placa1 = Placa("ABC1D23")
        placa2 = Placa("abc1d23")
        assert placa1 == placa2

    def test_str_retorna_valor(self) -> None:
        placa = Placa("ABC1D23")
        assert str(placa) == "ABC1D23"

    def test_hash_consistente(self) -> None:
        placa1 = Placa("ABC1D23")
        placa2 = Placa("abc1d23")
        assert hash(placa1) == hash(placa2)
