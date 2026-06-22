import uuid

import pytest

from src.domain.entities.peca import Peca
from src.domain.exceptions.domain_exceptions import EstoqueInsuficienteError
from src.domain.value_objects.dinheiro import Dinheiro


class TestPeca:
    def _criar_peca_valida(self, estoque: int = 10) -> Peca:
        return Peca(
            nome="Filtro de Oleo",
            sku="FO-001",
            preco=Dinheiro(25.50),
            quantidade_estoque=estoque,
            estoque_minimo=5,
        )

    def test_criar_peca_valida(self) -> None:
        peca = self._criar_peca_valida()
        assert peca.nome == "Filtro de Oleo"
        assert peca.sku == "FO-001"
        assert peca.quantidade_estoque == 10
        assert peca.ativo is True

    def test_nome_vazio_raises(self) -> None:
        with pytest.raises(ValueError, match="obrigatorio"):
            Peca(nome="", sku="FO-001", preco=Dinheiro(10), quantidade_estoque=5)

    def test_sku_vazio_raises(self) -> None:
        with pytest.raises(ValueError, match="obrigatorio"):
            Peca(nome="Filtro", sku="", preco=Dinheiro(10), quantidade_estoque=5)

    def test_estoque_negativo_raises(self) -> None:
        with pytest.raises(ValueError, match="negativa"):
            Peca(nome="Filtro", sku="FO-001", preco=Dinheiro(10), quantidade_estoque=-1)

    def test_baixar_estoque(self) -> None:
        peca = self._criar_peca_valida(estoque=10)
        peca.baixar_estoque(3)
        assert peca.quantidade_estoque == 7

    def test_baixar_estoque_insuficiente_raises(self) -> None:
        peca = self._criar_peca_valida(estoque=5)
        with pytest.raises(EstoqueInsuficienteError):
            peca.baixar_estoque(10)

    def test_baixar_estoque_zero_raises(self) -> None:
        peca = self._criar_peca_valida()
        with pytest.raises(ValueError, match="positiva"):
            peca.baixar_estoque(0)

    def test_repor_estoque(self) -> None:
        peca = self._criar_peca_valida(estoque=5)
        peca.repor_estoque(10)
        assert peca.quantidade_estoque == 15

    def test_ajustar_estoque(self) -> None:
        peca = self._criar_peca_valida()
        peca.ajustar_estoque(50)
        assert peca.quantidade_estoque == 50

    def test_ajustar_estoque_negativo_raises(self) -> None:
        peca = self._criar_peca_valida()
        with pytest.raises(ValueError, match="negativa"):
            peca.ajustar_estoque(-1)

    def test_estoque_baixo_true(self) -> None:
        peca = Peca(
            nome="Filtro",
            sku="FO-001",
            preco=Dinheiro(10),
            quantidade_estoque=3,
            estoque_minimo=5,
        )
        assert peca.estoque_baixo is True

    def test_estoque_baixo_false(self) -> None:
        peca = self._criar_peca_valida(estoque=20)
        assert peca.estoque_baixo is False

    def test_desativar_e_ativar(self) -> None:
        peca = self._criar_peca_valida()
        peca.desativar()
        assert peca.ativo is False
        peca.ativar()
        assert peca.ativo is True
