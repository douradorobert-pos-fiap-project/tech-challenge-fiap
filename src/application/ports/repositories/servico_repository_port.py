import abc
import uuid

from src.domain.entities.servico import Servico


class ServicoRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, servico: Servico) -> Servico: ...

    @abc.abstractmethod
    def get_by_id(self, servico_id: uuid.UUID) -> Servico | None: ...

    @abc.abstractmethod
    def list_all(self) -> list[Servico]: ...

    @abc.abstractmethod
    def list_ativos(self) -> list[Servico]: ...

    @abc.abstractmethod
    def delete(self, servico_id: uuid.UUID) -> None: ...
