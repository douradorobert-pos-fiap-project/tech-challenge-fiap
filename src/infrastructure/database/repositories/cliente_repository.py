import uuid

from sqlalchemy.orm import Session

from src.application.ports.repositories.cliente_repository_port import (
    ClienteRepositoryPort,
)
from src.domain.entities.cliente import Cliente
from src.domain.value_objects.cpf_cnpj import CpfCnpj
from src.domain.value_objects.email import Email
from src.infrastructure.database.models.cliente_model import ClienteModel


class SqlAlchemyClienteRepository(ClienteRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, cliente: Cliente) -> Cliente:
        model = self._session.get(ClienteModel, str(cliente.id))
        if model is None:
            model = ClienteModel(
                id=str(cliente.id),
                nome=cliente.nome,
                cpf_cnpj=cliente.cpf_cnpj.valor,
                email=cliente.email.valor,
                telefone=cliente.telefone,
                ativo=cliente.ativo,
            )
            self._session.add(model)
        else:
            model.nome = cliente.nome
            model.cpf_cnpj = cliente.cpf_cnpj.valor
            model.email = cliente.email.valor
            model.telefone = cliente.telefone
            model.ativo = cliente.ativo
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, cliente_id: uuid.UUID) -> Cliente | None:
        model = self._session.get(ClienteModel, str(cliente_id))
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_cpf_cnpj(self, cpf_cnpj: str) -> Cliente | None:
        model = (
            self._session.query(ClienteModel)
            .filter(ClienteModel.cpf_cnpj == cpf_cnpj)
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Cliente]:
        models = self._session.query(ClienteModel).all()
        return [self._to_entity(m) for m in models]

    def delete(self, cliente_id: uuid.UUID) -> None:
        model = self._session.get(ClienteModel, str(cliente_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: ClienteModel) -> Cliente:
        return Cliente(
            id=uuid.UUID(model.id),
            nome=model.nome,
            cpf_cnpj=CpfCnpj(model.cpf_cnpj),
            email=Email(model.email),
            telefone=model.telefone,
            ativo=model.ativo,
        )
