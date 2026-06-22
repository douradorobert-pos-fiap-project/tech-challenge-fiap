import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from src.application.ports.repositories.servico_repository_port import ServicoRepositoryPort
from src.domain.entities.servico import Servico
from src.domain.value_objects.dinheiro import Dinheiro
from src.infrastructure.database.models.servico_model import ServicoModel


class SqlAlchemyServicoRepository(ServicoRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, servico: Servico) -> Servico:
        model = self._session.get(ServicoModel, str(servico.id))
        if model is None:
            model = ServicoModel(
                id=str(servico.id),
                nome=servico.nome,
                descricao=servico.descricao,
                preco_base=servico.preco_base.valor,
                ativo=servico.ativo,
            )
            self._session.add(model)
        else:
            model.nome = servico.nome
            model.descricao = servico.descricao
            model.preco_base = servico.preco_base.valor
            model.ativo = servico.ativo
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, servico_id: uuid.UUID) -> Servico | None:
        model = self._session.get(ServicoModel, str(servico_id))
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Servico]:
        models = self._session.query(ServicoModel).all()
        return [self._to_entity(m) for m in models]

    def list_ativos(self) -> list[Servico]:
        models = (
            self._session.query(ServicoModel)
            .filter(ServicoModel.ativo == True)  # noqa: E712
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete(self, servico_id: uuid.UUID) -> None:
        model = self._session.get(ServicoModel, str(servico_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: ServicoModel) -> Servico:
        return Servico(
            id=uuid.UUID(model.id),
            nome=model.nome,
            descricao=model.descricao,
            preco_base=Dinheiro(Decimal(str(model.preco_base))),
            ativo=model.ativo,
        )
