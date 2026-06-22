import uuid

from src.application.dtos.ordem_servico_dtos import (
    AbrirOsDTO,
    ItemPecaResponseDTO,
    ItemServicoResponseDTO,
    OrcamentoResponseDTO,
    OrdemServicoResponseDTO,
)
from src.application.ports.repositories.cliente_repository_port import ClienteRepositoryPort
from src.application.ports.repositories.ordem_servico_repository_port import OrdemServicoRepositoryPort
from src.application.ports.repositories.peca_repository_port import PecaRepositoryPort
from src.application.ports.repositories.servico_repository_port import ServicoRepositoryPort
from src.application.ports.repositories.veiculo_repository_port import VeiculoRepositoryPort
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.exceptions.domain_exceptions import (
    ClienteNaoEncontradoError,
    VeiculoNaoEncontradoError,
)
from src.domain.services.calculo_orcamento import CalculoOrcamentoService


class AbrirOsUseCase:
    def __init__(
        self,
        os_repository: OrdemServicoRepositoryPort,
        cliente_repository: ClienteRepositoryPort,
        veiculo_repository: VeiculoRepositoryPort,
        servico_repository: ServicoRepositoryPort,
        peca_repository: PecaRepositoryPort,
    ) -> None:
        self._os_repository = os_repository
        self._cliente_repository = cliente_repository
        self._veiculo_repository = veiculo_repository
        self._servico_repository = servico_repository
        self._peca_repository = peca_repository
        self._calculo_service = CalculoOrcamentoService()

    def execute(self, dto: AbrirOsDTO) -> OrdemServicoResponseDTO:
        cliente_id = uuid.UUID(dto.cliente_id)
        veiculo_id = uuid.UUID(dto.veiculo_id)

        cliente = self._cliente_repository.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(dto.cliente_id)

        veiculo = self._veiculo_repository.get_by_id(veiculo_id)
        if veiculo is None:
            raise VeiculoNaoEncontradoError(dto.veiculo_id)

        servico_ids = [uuid.UUID(s.servico_id) for s in dto.servicos]
        servicos = []
        for sid in servico_ids:
            s = self._servico_repository.get_by_id(sid)
            if s is not None:
                servicos.append(s)

        peca_quantidades = {uuid.UUID(p.peca_id): p.quantidade for p in dto.pecas}
        pecas = []
        for pid in peca_quantidades:
            p = self._peca_repository.get_by_id(pid)
            if p is not None:
                pecas.append(p)

        ordem = OrdemServico(cliente_id=cliente_id, veiculo_id=veiculo_id)

        self._calculo_service.calcular(
            ordem=ordem,
            servicos=servicos,
            pecas=pecas,
            servico_ids=servico_ids,
            peca_quantidades=peca_quantidades,
        )

        ordem.iniciar_diagnostico()
        ordem.aguardar_aprovacao()

        saved = self._os_repository.save(ordem)
        return self._to_response(saved)

    @staticmethod
    def _to_response(ordem: OrdemServico) -> OrdemServicoResponseDTO:
        orcamento = OrcamentoResponseDTO(
            total_servicos=float(ordem.orcamento.total_servicos.valor),
            total_pecas=float(ordem.orcamento.total_pecas.valor),
            total=float(ordem.orcamento.total.valor),
            aprovado=ordem.orcamento.aprovado,
            recusado=ordem.orcamento.recusado,
            itens_servico=[
                ItemServicoResponseDTO(
                    servico_id=item.servico_id,
                    nome=item.nome,
                    preco=float(item.preco.valor),
                )
                for item in ordem.orcamento.itens_servico
            ],
            itens_peca=[
                ItemPecaResponseDTO(
                    peca_id=item.peca_id,
                    nome=item.nome,
                    preco_unitario=float(item.preco_unitario.valor),
                    quantidade=item.quantidade,
                    subtotal=float(item.subtotal.valor),
                )
                for item in ordem.orcamento.itens_peca
            ],
        )
        return OrdemServicoResponseDTO(
            id=ordem.id,
            cliente_id=ordem.cliente_id,
            veiculo_id=ordem.veiculo_id,
            status=ordem.status.name,
            orcamento=orcamento,
            criada_em=ordem.criada_em,
            atualizada_em=ordem.atualizada_em,
        )
