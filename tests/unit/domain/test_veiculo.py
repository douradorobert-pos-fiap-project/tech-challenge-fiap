import uuid

import pytest

from src.domain.entities.veiculo import Veiculo
from src.domain.value_objects.placa import Placa


class TestVeiculo:
    def _criar_veiculo_valido(self) -> Veiculo:
        return Veiculo(
            cliente_id=uuid.uuid4(),
            placa=Placa("ABC1D23"),
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
        )

    def test_criar_veiculo_valido(self) -> None:
        veiculo = self._criar_veiculo_valido()
        assert veiculo.marca == "Toyota"
        assert veiculo.modelo == "Corolla"
        assert veiculo.ano == 2023
        assert veiculo.id is not None

    def test_marca_vazia_raises(self) -> None:
        with pytest.raises(ValueError, match="obrigatoria"):
            Veiculo(
                cliente_id=uuid.uuid4(),
                placa=Placa("ABC1D23"),
                marca="",
                modelo="Corolla",
                ano=2023,
            )

    def test_modelo_vazio_raises(self) -> None:
        with pytest.raises(ValueError, match="obrigatorio"):
            Veiculo(
                cliente_id=uuid.uuid4(),
                placa=Placa("ABC1D23"),
                marca="Toyota",
                modelo="",
                ano=2023,
            )

    def test_ano_abaixo_de_1900_raises(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            Veiculo(
                cliente_id=uuid.uuid4(),
                placa=Placa("ABC1D23"),
                marca="Toyota",
                modelo="Corolla",
                ano=1899,
            )

    def test_ano_acima_de_2100_raises(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            Veiculo(
                cliente_id=uuid.uuid4(),
                placa=Placa("ABC1D23"),
                marca="Toyota",
                modelo="Corolla",
                ano=2101,
            )

    def test_atualizar_marca(self) -> None:
        veiculo = self._criar_veiculo_valido()
        veiculo.atualizar_dados(marca="Honda")
        assert veiculo.marca == "Honda"

    def test_atualizar_ano_invalido_raises(self) -> None:
        veiculo = self._criar_veiculo_valido()
        with pytest.raises(ValueError, match="invalido"):
            veiculo.atualizar_dados(ano=1800)
