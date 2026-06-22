import abc
import uuid

from src.domain.entities.cliente import Cliente


class ClienteRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, cliente: Cliente) -> Cliente: ...

    @abc.abstractmethod
    def get_by_id(self, cliente_id: uuid.UUID) -> Cliente | None: ...

    @abc.abstractmethod
    def get_by_cpf_cnpj(self, cpf_cnpj: str) -> Cliente | None: ...

    @abc.abstractmethod
    def list_all(self) -> list[Cliente]: ...

    @abc.abstractmethod
    def delete(self, cliente_id: uuid.UUID) -> None: ...
