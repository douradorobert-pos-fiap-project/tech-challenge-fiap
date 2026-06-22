import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ItemServicoInputDTO:
    servico_id: str


@dataclass
class ItemPecaInputDTO:
    peca_id: str
    quantidade: int


@dataclass
class AbrirOsDTO:
    cliente_id: str
    veiculo_id: str
    servicos: list[ItemServicoInputDTO]
    pecas: list[ItemPecaInputDTO]


@dataclass
class AprovarOrcamentoDTO:
    acao: str  # "APROVAR" | "RECUSAR"


@dataclass
class AtualizarStatusDTO:
    novo_status: str


@dataclass
class ItemServicoResponseDTO:
    servico_id: uuid.UUID
    nome: str
    preco: float


@dataclass
class ItemPecaResponseDTO:
    peca_id: uuid.UUID
    nome: str
    preco_unitario: float
    quantidade: int
    subtotal: float


@dataclass
class OrcamentoResponseDTO:
    total_servicos: float
    total_pecas: float
    total: float
    aprovado: bool
    recusado: bool
    itens_servico: list[ItemServicoResponseDTO]
    itens_peca: list[ItemPecaResponseDTO]


@dataclass
class OrdemServicoResponseDTO:
    id: uuid.UUID
    cliente_id: uuid.UUID
    veiculo_id: uuid.UUID
    status: str
    orcamento: OrcamentoResponseDTO
    criada_em: datetime
    atualizada_em: datetime


@dataclass
class StatusOsResponseDTO:
    id: uuid.UUID
    status: str
