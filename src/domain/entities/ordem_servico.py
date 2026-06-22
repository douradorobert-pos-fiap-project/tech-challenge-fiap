import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.entities.item import ItemPeca, ItemServico
from src.domain.entities.orcamento import Orcamento
from src.domain.exceptions.domain_exceptions import (
    OrcamentoJaAprovadoError,
    OrcamentoJaRecusadoError,
    TransicaoStatusInvalidaError,
)
from src.domain.value_objects.status_os import StatusOS


_TRANSICOES_VALIDAS: dict[StatusOS, set[StatusOS]] = {
    StatusOS.RECEBIDA: {StatusOS.DIAGNOSTICO, StatusOS.CANCELADA},
    StatusOS.DIAGNOSTICO: {StatusOS.AGUARDANDO_APROVACAO, StatusOS.CANCELADA},
    StatusOS.AGUARDANDO_APROVACAO: {StatusOS.EM_EXECUCAO, StatusOS.CANCELADA},
    StatusOS.EM_EXECUCAO: {StatusOS.FINALIZADA, StatusOS.CANCELADA},
    StatusOS.FINALIZADA: {StatusOS.ENTREGUE},
    StatusOS.ENTREGUE: set(),
    StatusOS.CANCELADA: set(),
}


@dataclass
class OrdemServico:
    cliente_id: uuid.UUID
    veiculo_id: uuid.UUID
    orcamento: Orcamento = field(default_factory=Orcamento)
    status: StatusOS = StatusOS.RECEBIDA
    observacoes: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    criada_em: datetime = field(default_factory=lambda: datetime.now(UTC))
    atualizada_em: datetime = field(default_factory=lambda: datetime.now(UTC))
    finalizada_em: datetime | None = None
    entregue_em: datetime | None = None
    deletada: bool = False

    def adicionar_servico(self, item: ItemServico) -> None:
        self.orcamento.itens_servico.append(item)
        self.atualizada_em = datetime.now(UTC)

    def adicionar_peca(self, item: ItemPeca) -> None:
        self.orcamento.itens_peca.append(item)
        self.atualizada_em = datetime.now(UTC)

    def calcular_orcamento(self) -> None:
        self.atualizada_em = datetime.now(UTC)

    def transitar_status(self, novo_status: StatusOS) -> None:
        if novo_status == self.status:
            return
        permitidos = _TRANSICOES_VALIDAS.get(self.status, set())
        if novo_status not in permitidos:
            raise TransicaoStatusInvalidaError(self.status.name, novo_status.name)
        self.status = novo_status
        self.atualizada_em = datetime.now(UTC)
        if novo_status == StatusOS.FINALIZADA:
            self.finalizada_em = datetime.now(UTC)
        if novo_status == StatusOS.ENTREGUE:
            self.entregue_em = datetime.now(UTC)
            self.deletada = True

    def iniciar_diagnostico(self) -> None:
        self.transitar_status(StatusOS.DIAGNOSTICO)

    def aguardar_aprovacao(self) -> None:
        self.transitar_status(StatusOS.AGUARDANDO_APROVACAO)

    def executar(self) -> None:
        self.transitar_status(StatusOS.EM_EXECUCAO)

    def finalizar(self) -> None:
        self.transitar_status(StatusOS.FINALIZADA)

    def entregar(self) -> None:
        self.transitar_status(StatusOS.ENTREGUE)

    def cancelar(self) -> None:
        self.transitar_status(StatusOS.CANCELADA)

    def aprovar_orcamento(self) -> None:
        if self.orcamento.aprovado:
            raise OrcamentoJaAprovadoError(str(self.id))
        if self.orcamento.recusado:
            raise OrcamentoJaRecusadoError(str(self.id))
        self.orcamento.aprovar()
        self.executar()

    def recusar_orcamento(self) -> None:
        if self.orcamento.aprovado:
            raise OrcamentoJaAprovadoError(str(self.id))
        if self.orcamento.recusado:
            raise OrcamentoJaRecusadoError(str(self.id))
        self.orcamento.recusar()
        self.cancelar()

    def soft_delete(self) -> None:
        self.deletada = True

    @property
    def deve_ser_ocultada(self) -> bool:
        return self.deletada or self.status.deve_ser_ocultada
