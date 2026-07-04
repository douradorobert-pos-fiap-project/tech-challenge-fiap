import abc


class NotificacaoPort(abc.ABC):
    @abc.abstractmethod
    def notificar_aprovacao_orcamento(self, os_id: str, destinatario: str) -> None: ...

    @abc.abstractmethod
    def notificar_status_atualizado(
        self, os_id: str, status: str, destinatario: str
    ) -> None: ...
