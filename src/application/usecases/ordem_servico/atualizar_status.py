import uuid
from datetime import UTC, datetime

from src.application.dtos.ordem_servico_dtos import (
    AtualizarStatusDTO,
    OrdemServicoResponseDTO,
)
from src.application.ports.external.email_port import EmailPort
from src.application.ports.repositories.ordem_servico_repository_port import (
    OrdemServicoRepositoryPort,
)
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase
from src.domain.exceptions.domain_exceptions import OrdemServicoNaoEncontradaError
from src.domain.value_objects.status_os import StatusOS
from src.infrastructure.observability.telemetry import record_event


class AtualizarStatusOsUseCase:
    def __init__(
        self,
        repository: OrdemServicoRepositoryPort,
        email_port: EmailPort | None = None,
    ) -> None:
        self._repository = repository
        self._email_port = email_port

    def execute(
        self, os_id: uuid.UUID, dto: AtualizarStatusDTO
    ) -> OrdemServicoResponseDTO:
        ordem = self._repository.get_by_id(os_id)
        if ordem is None:
            raise OrdemServicoNaoEncontradaError(str(os_id))

        novo_status = StatusOS.from_string(dto.novo_status)
        status_anterior = ordem.status
        status_started_at = ordem.atualizada_em
        ordem.transitar_status(novo_status)

        now = datetime.now(UTC)
        if status_started_at.tzinfo is None:
            now = now.replace(tzinfo=None)
        saved = self._repository.save(ordem)
        record_event(
            "ServiceOrderStatusChanged",
            order_id=str(saved.id),
            previous_status=status_anterior.name,
            new_status=saved.status.name,
        )
        if status_anterior != saved.status:
            record_event(
                "ServiceOrderStatusDuration",
                order_id=str(saved.id),
                status=status_anterior.name,
                duration_ms=max(0, (now - status_started_at).total_seconds() * 1000),
            )
        if self._email_port is not None and saved.status.is_finalizada:
            self._email_port.enviar_email(
                destinatario="",
                assunto=f"OS {saved.id} - Status atualizado",
                corpo=f"A ordem de servico {saved.id} foi atualizada para: {saved.status.name}",
            )

        return AbrirOsUseCase._to_response(saved)
