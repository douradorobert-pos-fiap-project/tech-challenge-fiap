import abc
import uuid

from src.domain.entities.peca import Peca


class PecaRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, peca: Peca) -> Peca: ...

    @abc.abstractmethod
    def get_by_id(self, peca_id: uuid.UUID) -> Peca | None: ...

    @abc.abstractmethod
    def get_by_sku(self, sku: str) -> Peca | None: ...

    @abc.abstractmethod
    def list_all(self) -> list[Peca]: ...

    @abc.abstractmethod
    def list_ativos(self) -> list[Peca]: ...

    @abc.abstractmethod
    def delete(self, peca_id: uuid.UUID) -> None: ...
