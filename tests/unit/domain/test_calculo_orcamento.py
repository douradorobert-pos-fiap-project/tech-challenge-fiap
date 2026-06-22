import uuid
from decimal import Decimal

from src.domain.entities.item import ItemPeca, ItemServico
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.entities.peca import Peca
from src.domain.entities.servico import Servico
from src.domain.services.calculo_orcamento import CalculoOrcamentoService
from src.domain.value_objects.dinheiro import Dinheiro


class TestCalculoOrcamentoService:
    def _criar_servicos(self) -> list[Servico]:
        return [
            Servico(nome="Troca de Oleo", descricao="Troca de oleo e filtro", preco_base=Dinheiro(80)),
            Servico(nome="Alinhamento", descricao="Alinhamento e balanceamento", preco_base=Dinheiro(120)),
        ]

    def _criar_pecas(self) -> list[Peca]:
        return [
            Peca(nome="Filtro de Oleo", sku="FO-001", preco=Dinheiro(25.50), quantidade_estoque=20),
            Peca(nome="Oleo Motor 5W30", sku="OL-001", preco=Dinheiro(45.00), quantidade_estoque=15),
        ]

    def test_calcular_com_servicos_e_pecas(self) -> None:
        service = CalculoOrcamentoService()
        servicos = self._criar_servicos()
        pecas = self._criar_pecas()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=servicos,
            pecas=pecas,
            servico_ids=[servicos[0].id, servicos[1].id],
            peca_quantidades={pecas[0].id: 2, pecas[1].id: 4},
        )

        assert len(ordem.orcamento.itens_servico) == 2
        assert len(ordem.orcamento.itens_peca) == 2

    def test_total_calculado_corretamente(self) -> None:
        service = CalculoOrcamentoService()
        servicos = self._criar_servicos()
        pecas = self._criar_pecas()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=servicos,
            pecas=pecas,
            servico_ids=[servicos[0].id, servicos[1].id],
            peca_quantidades={pecas[0].id: 2, pecas[1].id: 4},
        )

        total_servicos = Decimal("200.00")
        total_pecas = Decimal("231.00")
        total_esperado = total_servicos + total_pecas

        assert ordem.orcamento.total.valor == total_esperado

    def test_calcular_apenas_servicos(self) -> None:
        service = CalculoOrcamentoService()
        servicos = self._criar_servicos()
        pecas = self._criar_pecas()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=servicos,
            pecas=pecas,
            servico_ids=[servicos[0].id],
            peca_quantidades={},
        )

        assert len(ordem.orcamento.itens_servico) == 1
        assert len(ordem.orcamento.itens_peca) == 0
        assert ordem.orcamento.total.valor == Decimal("80.00")

    def test_calcular_apenas_pecas(self) -> None:
        service = CalculoOrcamentoService()
        servicos = self._criar_servicos()
        pecas = self._criar_pecas()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=servicos,
            pecas=pecas,
            servico_ids=[],
            peca_quantidades={pecas[0].id: 3},
        )

        assert len(ordem.orcamento.itens_servico) == 0
        assert len(ordem.orcamento.itens_peca) == 1
        assert ordem.orcamento.total.valor == Decimal("76.50")

    def test_calcular_total_orcamento_vazio(self) -> None:
        service = CalculoOrcamentoService()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=[],
            pecas=[],
            servico_ids=[],
            peca_quantidades={},
        )

        assert ordem.orcamento.total.valor == Decimal("0.00")

    def test_servico_inexistente_e_ignorado(self) -> None:
        service = CalculoOrcamentoService()
        servicos = self._criar_servicos()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=servicos,
            pecas=[],
            servico_ids=[uuid.uuid4()],
            peca_quantidades={},
        )

        assert len(ordem.orcamento.itens_servico) == 0

    def test_peca_inexistente_e_ignorada(self) -> None:
        service = CalculoOrcamentoService()
        pecas = self._criar_pecas()
        ordem = OrdemServico(cliente_id=uuid.uuid4(), veiculo_id=uuid.uuid4())

        service.calcular(
            ordem=ordem,
            servicos=[],
            pecas=pecas,
            servico_ids=[],
            peca_quantidades={uuid.uuid4(): 5},
        )

        assert len(ordem.orcamento.itens_peca) == 0
