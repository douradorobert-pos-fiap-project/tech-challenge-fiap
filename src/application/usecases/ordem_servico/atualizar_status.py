import uuid

from src.application.dtos.ordem_servico_dtos import (
    AtualizarStatusDTO,
    OrdemServicoResponseDTO,
)
from src.application.ports.repositories.ordem_servico_repository_port import OrdemServicoRepositoryPort
from src.application.ports.external.email_port import EmailPort
from src.domain.exceptions.domain_exceptions import OrdemServicoNaoEncontradaError
from src.domain.value_objects.status_os import StatusOS
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase


class AtualizarStatusOsUseCase:
    def __init__(
        self,
        repository: OrdemServicoRepositoryPort,
        email_port: EmailPort | None = None,
    ) -> None:
        self._repository = repository
        self._email_port = email_port

    def execute(self, os_id: uuid.UUID, dto: AtualizarStatusDTO) -> OrdemServicoResponseDTO:
        ordem = self._repository.get_by_id(os_id)
        if ordem is None:
            raise OrdemServicoNaoEncontradaError(str(os_id))

        novo_status = StatusOS.from_string(dto.novo_status)
        ordem.transitar_status(novo_status)

        saved = self._repository.save(ordem)

        if self._email_port is not None and saved.status.is_finalizada:
            self._email_port.enviar_email(
                destinatario="",
                assunto=f"OS {saved.id} - Status atualizado",
                corpo=f"A ordem de servico {saved.id} foi atualizada para: {saved.status.name}",
            )

        return AbrirOsUseCase._to_response(saved)
