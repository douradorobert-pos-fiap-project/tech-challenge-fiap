import uuid

from src.domain.entities.item import ItemPeca, ItemServico
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.entities.peca import Peca
from src.domain.entities.servico import Servico
from src.domain.value_objects.dinheiro import Dinheiro


class CalculoOrcamentoService:

    def calcular(
        self,
        ordem: OrdemServico,
        servicos: list[Servico],
        pecas: list[Peca],
        servico_ids: list[uuid.UUID],
        peca_quantidades: dict[uuid.UUID, int],
    ) -> None:
        servico_map = {s.id: s for s in servicos}
        peca_map = {p.id: p for p in pecas}

        for servico_id in servico_ids:
            servico = servico_map.get(servico_id)
            if servico is None:
                continue
            item = ItemServico(
                servico_id=servico.id,
                nome=servico.nome,
                preco=servico.preco_base,
            )
            ordem.adicionar_servico(item)

        for peca_id, quantidade in peca_quantidades.items():
            peca = peca_map.get(peca_id)
            if peca is None:
                continue
            item = ItemPeca(
                peca_id=peca.id,
                nome=peca.nome,
                preco_unitario=peca.preco,
                quantidade=quantidade,
            )
            ordem.adicionar_peca(item)

        ordem.calcular_orcamento()

    def calcular_total(self, ordem: OrdemServico) -> Dinheiro:
        return ordem.orcamento.total
