import uuid

from sqlalchemy.orm import Session

from src.application.ports.repositories.veiculo_repository_port import (
    VeiculoRepositoryPort,
)
from src.domain.entities.veiculo import Veiculo
from src.domain.value_objects.placa import Placa
from src.infrastructure.database.models.veiculo_model import VeiculoModel


class SqlAlchemyVeiculoRepository(VeiculoRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, veiculo: Veiculo) -> Veiculo:
        model = self._session.get(VeiculoModel, str(veiculo.id))
        if model is None:
            model = VeiculoModel(
                id=str(veiculo.id),
                cliente_id=str(veiculo.cliente_id),
                placa=veiculo.placa.valor,
                marca=veiculo.marca,
                modelo=veiculo.modelo,
                ano=veiculo.ano,
            )
            self._session.add(model)
        else:
            model.placa = veiculo.placa.valor
            model.marca = veiculo.marca
            model.modelo = veiculo.modelo
            model.ano = veiculo.ano
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, veiculo_id: uuid.UUID) -> Veiculo | None:
        model = self._session.get(VeiculoModel, str(veiculo_id))
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_placa(self, placa: str) -> Veiculo | None:
        model = (
            self._session.query(VeiculoModel)
            .filter(VeiculoModel.placa == placa.upper())
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_cliente(self, cliente_id: uuid.UUID) -> list[Veiculo]:
        models = (
            self._session.query(VeiculoModel)
            .filter(VeiculoModel.cliente_id == str(cliente_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_all(self) -> list[Veiculo]:
        models = self._session.query(VeiculoModel).all()
        return [self._to_entity(m) for m in models]

    def delete(self, veiculo_id: uuid.UUID) -> None:
        model = self._session.get(VeiculoModel, str(veiculo_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: VeiculoModel) -> Veiculo:
        return Veiculo(
            id=uuid.UUID(model.id),
            cliente_id=uuid.UUID(model.cliente_id),
            placa=Placa(model.placa),
            marca=model.marca,
            modelo=model.modelo,
            ano=model.ano,
        )
