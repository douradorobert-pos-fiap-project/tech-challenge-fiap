import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from src.application.ports.repositories.peca_repository_port import PecaRepositoryPort
from src.domain.entities.peca import Peca
from src.domain.value_objects.dinheiro import Dinheiro
from src.infrastructure.database.models.peca_model import PecaModel


class SqlAlchemyPecaRepository(PecaRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, peca: Peca) -> Peca:
        model = self._session.get(PecaModel, str(peca.id))
        if model is None:
            model = PecaModel(
                id=str(peca.id),
                nome=peca.nome,
                sku=peca.sku,
                preco=peca.preco.valor,
                quantidade_estoque=peca.quantidade_estoque,
                estoque_minimo=peca.estoque_minimo,
                ativo=peca.ativo,
            )
            self._session.add(model)
        else:
            model.nome = peca.nome
            model.sku = peca.sku
            model.preco = peca.preco.valor
            model.quantidade_estoque = peca.quantidade_estoque
            model.estoque_minimo = peca.estoque_minimo
            model.ativo = peca.ativo
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, peca_id: uuid.UUID) -> Peca | None:
        model = self._session.get(PecaModel, str(peca_id))
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_sku(self, sku: str) -> Peca | None:
        model = (
            self._session.query(PecaModel)
            .filter(PecaModel.sku == sku)
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Peca]:
        models = self._session.query(PecaModel).all()
        return [self._to_entity(m) for m in models]

    def list_ativos(self) -> list[Peca]:
        models = (
            self._session.query(PecaModel)
            .filter(PecaModel.ativo == True)  # noqa: E712
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete(self, peca_id: uuid.UUID) -> None:
        model = self._session.get(PecaModel, str(peca_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: PecaModel) -> Peca:
        return Peca(
            id=uuid.UUID(model.id),
            nome=model.nome,
            sku=model.sku,
            preco=Dinheiro(Decimal(str(model.preco))),
            quantidade_estoque=model.quantidade_estoque,
            estoque_minimo=model.estoque_minimo,
            ativo=model.ativo,
        )
