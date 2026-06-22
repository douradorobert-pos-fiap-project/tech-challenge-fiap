import abc
import uuid

from src.domain.entities.ordem_servico import OrdemServico


class OrdemServicoRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, ordem: OrdemServico) -> OrdemServico: ...

    @abc.abstractmethod
    def get_by_id(self, os_id: uuid.UUID) -> OrdemServico | None: ...

    @abc.abstractmethod
    def list_ativas(self) -> list[OrdemServico]: ...

    @abc.abstractmethod
    def list_all(self) -> list[OrdemServico]: ...
