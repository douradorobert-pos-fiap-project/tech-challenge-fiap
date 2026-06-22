import abc


class EmailPort(abc.ABC):
    @abc.abstractmethod
    def enviar_email(self, destinatario: str, assunto: str, corpo: str) -> None: ...
