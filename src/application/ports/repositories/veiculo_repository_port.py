import abc
import uuid

from src.domain.entities.veiculo import Veiculo


class VeiculoRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def save(self, veiculo: Veiculo) -> Veiculo: ...

    @abc.abstractmethod
    def get_by_id(self, veiculo_id: uuid.UUID) -> Veiculo | None: ...

    @abc.abstractmethod
    def get_by_placa(self, placa: str) -> Veiculo | None: ...

    @abc.abstractmethod
    def list_by_cliente(self, cliente_id: uuid.UUID) -> list[Veiculo]: ...

    @abc.abstractmethod
    def list_all(self) -> list[Veiculo]: ...

    @abc.abstractmethod
    def delete(self, veiculo_id: uuid.UUID) -> None: ...
