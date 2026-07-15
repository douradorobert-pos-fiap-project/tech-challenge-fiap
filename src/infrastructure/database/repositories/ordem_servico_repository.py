import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from src.application.ports.repositories.ordem_servico_repository_port import (
    OrdemServicoRepositoryPort,
)
from src.domain.entities.item import ItemPeca, ItemServico
from src.domain.entities.orcamento import Orcamento
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.value_objects.dinheiro import Dinheiro
from src.domain.value_objects.status_os import StatusOS
from src.infrastructure.database.models.ordem_servico_model import (
    ItemPecaModel,
    ItemServicoModel,
    OrdemServicoModel,
)


class SqlAlchemyOrdemServicoRepository(OrdemServicoRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, ordem: OrdemServico) -> OrdemServico:
        model = self._session.get(OrdemServicoModel, str(ordem.id))
        if model is None:
            model = OrdemServicoModel(
                id=str(ordem.id),
                cliente_id=str(ordem.cliente_id),
                veiculo_id=str(ordem.veiculo_id),
                status=ordem.status.name,
                orcamento_aprovado=ordem.orcamento.aprovado,
                orcamento_recusado=ordem.orcamento.recusado,
                observacoes=ordem.observacoes,
                deletada=ordem.deletada,
                criada_em=ordem.criada_em,
                atualizada_em=ordem.atualizada_em,
                finalizada_em=ordem.finalizada_em,
                entregue_em=ordem.entregue_em,
            )
            self._session.add(model)
            self._session.commit()
        else:
            self._session.query(ItemServicoModel).filter(
                ItemServicoModel.ordem_servico_id == str(ordem.id)
            ).delete()
            self._session.query(ItemPecaModel).filter(
                ItemPecaModel.ordem_servico_id == str(ordem.id)
            ).delete()

            model.status = ordem.status.name
            model.orcamento_aprovado = ordem.orcamento.aprovado
            model.orcamento_recusado = ordem.orcamento.recusado
            model.observacoes = ordem.observacoes
            model.deletada = ordem.deletada
            model.atualizada_em = ordem.atualizada_em
            model.finalizada_em = ordem.finalizada_em
            model.entregue_em = ordem.entregue_em

            self._session.commit()

        for item in ordem.orcamento.itens_servico:
            self._session.add(
                ItemServicoModel(
                    id=str(item.id),
                    ordem_servico_id=str(ordem.id),
                    servico_id=str(item.servico_id),
                    nome=item.nome,
                    preco=item.preco.valor,
                )
            )

        for item in ordem.orcamento.itens_peca:
            self._session.add(
                ItemPecaModel(
                    id=str(item.id),
                    ordem_servico_id=str(ordem.id),
                    peca_id=str(item.peca_id),
                    nome=item.nome,
                    preco_unitario=item.preco_unitario.valor,
                    quantidade=item.quantidade,
                )
            )

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, os_id: uuid.UUID) -> OrdemServico | None:
        model = self._session.get(OrdemServicoModel, str(os_id))
        if model is None:
            return None
        return self._to_entity(model)

    def list_ativas(self) -> list[OrdemServico]:
        models = (
            self._session.query(OrdemServicoModel)
            .filter(OrdemServicoModel.deletada == False)  # noqa: E712
            .filter(~OrdemServicoModel.status.in_(["FINALIZADA", "ENTREGUE"]))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_all(self) -> list[OrdemServico]:
        models = self._session.query(OrdemServicoModel).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: OrdemServicoModel) -> OrdemServico:
        itens_servico_models = (
            self._session.query(ItemServicoModel)
            .filter(ItemServicoModel.ordem_servico_id == model.id)
            .all()
        )
        itens_peca_models = (
            self._session.query(ItemPecaModel)
            .filter(ItemPecaModel.ordem_servico_id == model.id)
            .all()
        )

        orcamento = Orcamento(
            aprovado=model.orcamento_aprovado,
            recusado=model.orcamento_recusado,
            itens_servico=[
                ItemServico(
                    servico_id=uuid.UUID(m.servico_id),
                    nome=m.nome,
                    preco=Dinheiro(Decimal(str(m.preco))),
                    id=uuid.UUID(m.id),
                )
                for m in itens_servico_models
            ],
            itens_peca=[
                ItemPeca(
                    peca_id=uuid.UUID(m.peca_id),
                    nome=m.nome,
                    preco_unitario=Dinheiro(Decimal(str(m.preco_unitario))),
                    quantidade=m.quantidade,
                    id=uuid.UUID(m.id),
                )
                for m in itens_peca_models
            ],
        )

        return OrdemServico(
            id=uuid.UUID(model.id),
            cliente_id=uuid.UUID(model.cliente_id),
            veiculo_id=uuid.UUID(model.veiculo_id),
            orcamento=orcamento,
            status=StatusOS.from_string(model.status),
            observacoes=model.observacoes or "",
            criada_em=model.criada_em,
            atualizada_em=model.atualizada_em,
            finalizada_em=model.finalizada_em,
            entregue_em=model.entregue_em,
            deletada=model.deletada,
        )
