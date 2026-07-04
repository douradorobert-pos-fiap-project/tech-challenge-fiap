import uuid

import pytest

from src.application.dtos.ordem_servico_dtos import (
    AbrirOsDTO,
    AprovarOrcamentoDTO,
    AtualizarStatusDTO,
    ItemPecaInputDTO,
    ItemServicoInputDTO,
)
from src.application.ports.repositories.cliente_repository_port import (
    ClienteRepositoryPort,
)
from src.application.ports.repositories.ordem_servico_repository_port import (
    OrdemServicoRepositoryPort,
)
from src.application.ports.repositories.peca_repository_port import PecaRepositoryPort
from src.application.ports.repositories.servico_repository_port import (
    ServicoRepositoryPort,
)
from src.application.ports.repositories.veiculo_repository_port import (
    VeiculoRepositoryPort,
)
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase
from src.application.usecases.ordem_servico.aprovar_orcamento import (
    AprovarOrcamentoUseCase,
)
from src.application.usecases.ordem_servico.atualizar_status import (
    AtualizarStatusOsUseCase,
)
from src.application.usecases.ordem_servico.consultar_status import (
    ConsultarStatusOsUseCase,
)
from src.application.usecases.ordem_servico.detalhar_os import DetalharOsUseCase
from src.application.usecases.ordem_servico.listar_os import ListarOsUseCase
from src.domain.entities.cliente import Cliente
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.entities.peca import Peca
from src.domain.entities.servico import Servico
from src.domain.entities.veiculo import Veiculo
from src.domain.exceptions.domain_exceptions import (
    OrdemServicoNaoEncontradaError,
    TransicaoStatusInvalidaError,
)
from src.domain.value_objects.cpf_cnpj import CpfCnpj
from src.domain.value_objects.dinheiro import Dinheiro
from src.domain.value_objects.email import Email
from src.domain.value_objects.placa import Placa


class FakeClienteRepository(ClienteRepositoryPort):
    def __init__(self) -> None:
        self._data: dict[uuid.UUID, Cliente] = {}

    def save(self, cliente: Cliente) -> Cliente:
        self._data[cliente.id] = cliente
        return cliente

    def get_by_id(self, cliente_id: uuid.UUID) -> Cliente | None:
        return self._data.get(cliente_id)

    def get_by_cpf_cnpj(self, cpf_cnpj: str) -> Cliente | None:
        for c in self._data.values():
            if c.cpf_cnpj.valor == cpf_cnpj:
                return c
        return None

    def list_all(self) -> list[Cliente]:
        return list(self._data.values())

    def delete(self, cliente_id: uuid.UUID) -> None:
        self._data.pop(cliente_id, None)


class FakeVeiculoRepository(VeiculoRepositoryPort):
    def __init__(self) -> None:
        self._data: dict[uuid.UUID, Veiculo] = {}

    def save(self, veiculo: Veiculo) -> Veiculo:
        self._data[veiculo.id] = veiculo
        return veiculo

    def get_by_id(self, veiculo_id: uuid.UUID) -> Veiculo | None:
        return self._data.get(veiculo_id)

    def get_by_placa(self, placa: str) -> Veiculo | None:
        for v in self._data.values():
            if v.placa.valor == placa:
                return v
        return None

    def list_by_cliente(self, cliente_id: uuid.UUID) -> list[Veiculo]:
        return [v for v in self._data.values() if v.cliente_id == cliente_id]

    def list_all(self) -> list[Veiculo]:
        return list(self._data.values())

    def delete(self, veiculo_id: uuid.UUID) -> None:
        self._data.pop(veiculo_id, None)


class FakeServicoRepository(ServicoRepositoryPort):
    def __init__(self) -> None:
        self._data: dict[uuid.UUID, Servico] = {}

    def save(self, servico: Servico) -> Servico:
        self._data[servico.id] = servico
        return servico

    def get_by_id(self, servico_id: uuid.UUID) -> Servico | None:
        return self._data.get(servico_id)

    def list_all(self) -> list[Servico]:
        return list(self._data.values())

    def list_ativos(self) -> list[Servico]:
        return [s for s in self._data.values() if s.ativo]

    def delete(self, servico_id: uuid.UUID) -> None:
        self._data.pop(servico_id, None)


class FakePecaRepository(PecaRepositoryPort):
    def __init__(self) -> None:
        self._data: dict[uuid.UUID, Peca] = {}

    def save(self, peca: Peca) -> Peca:
        self._data[peca.id] = peca
        return peca

    def get_by_id(self, peca_id: uuid.UUID) -> Peca | None:
        return self._data.get(peca_id)

    def get_by_sku(self, sku: str) -> Peca | None:
        for p in self._data.values():
            if p.sku == sku:
                return p
        return None

    def list_all(self) -> list[Peca]:
        return list(self._data.values())

    def list_ativos(self) -> list[Peca]:
        return [p for p in self._data.values() if p.ativo]

    def delete(self, peca_id: uuid.UUID) -> None:
        self._data.pop(peca_id, None)


class FakeOsRepository(OrdemServicoRepositoryPort):
    def __init__(self) -> None:
        self._data: dict[uuid.UUID, OrdemServico] = {}

    def save(self, ordem: OrdemServico) -> OrdemServico:
        self._data[ordem.id] = ordem
        return ordem

    def get_by_id(self, os_id: uuid.UUID) -> OrdemServico | None:
        return self._data.get(os_id)

    def list_ativas(self) -> list[OrdemServico]:
        return [o for o in self._data.values() if not o.deve_ser_ocultada]

    def list_all(self) -> list[OrdemServico]:
        return list(self._data.values())


def _setup_repositories() -> tuple[
    FakeOsRepository,
    FakeClienteRepository,
    FakeVeiculoRepository,
    FakeServicoRepository,
    FakePecaRepository,
]:
    os_repo = FakeOsRepository()
    cliente_repo = FakeClienteRepository()
    veiculo_repo = FakeVeiculoRepository()
    servico_repo = FakeServicoRepository()
    peca_repo = FakePecaRepository()

    cliente = Cliente(
        nome="Joao Silva",
        cpf_cnpj=CpfCnpj("52998224725"),
        email=Email("joao@example.com"),
        telefone="11999999999",
    )
    cliente_repo.save(cliente)

    veiculo = Veiculo(
        cliente_id=cliente.id,
        placa=Placa("ABC1D23"),
        marca="Toyota",
        modelo="Corolla",
        ano=2023,
    )
    veiculo_repo.save(veiculo)

    servico1 = Servico(
        nome="Troca de Oleo",
        descricao="Troca de oleo e filtro",
        preco_base=Dinheiro(80),
    )
    servico2 = Servico(
        nome="Alinhamento",
        descricao="Alinhamento e balanceamento",
        preco_base=Dinheiro(120),
    )
    servico_repo.save(servico1)
    servico_repo.save(servico2)

    peca1 = Peca(
        nome="Filtro de Oleo",
        sku="FO-001",
        preco=Dinheiro(25.50),
        quantidade_estoque=20,
    )
    peca2 = Peca(
        nome="Oleo Motor 5W30",
        sku="OL-001",
        preco=Dinheiro(45.00),
        quantidade_estoque=15,
    )
    peca_repo.save(peca1)
    peca_repo.save(peca2)

    return os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo


def _get_ids(repos) -> dict[str, uuid.UUID]:
    _, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
    cliente = cliente_repo.list_all()[0]
    veiculo = veiculo_repo.list_all()[0]
    servicos = servico_repo.list_all()
    pecas = peca_repo.list_all()
    return {
        "cliente": cliente.id,
        "veiculo": veiculo.id,
        "servico1": servicos[0].id,
        "servico2": servicos[1].id,
        "peca1": pecas[0].id,
        "peca2": pecas[1].id,
    }


class TestAbrirOsUseCase:
    def test_abrir_os_com_sucesso(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        use_case = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )

        result = use_case.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[
                    ItemServicoInputDTO(servico_id=str(ids["servico1"])),
                    ItemServicoInputDTO(servico_id=str(ids["servico2"])),
                ],
                pecas=[
                    ItemPecaInputDTO(peca_id=str(ids["peca1"]), quantidade=2),
                    ItemPecaInputDTO(peca_id=str(ids["peca2"]), quantidade=4),
                ],
            )
        )

        assert result.id is not None
        assert result.status == "AGUARDANDO_APROVACAO"
        assert len(result.orcamento.itens_servico) == 2
        assert len(result.orcamento.itens_peca) == 2
        assert result.orcamento.total == 431.00

    def test_abrir_os_apenas_servicos(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        use_case = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )

        result = use_case.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        assert result.orcamento.total == 80.00
        assert len(result.orcamento.itens_servico) == 1
        assert len(result.orcamento.itens_peca) == 0

    def test_abrir_os_cliente_inexistente_raises(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        use_case = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )

        with pytest.raises(Exception):
            use_case.execute(
                AbrirOsDTO(
                    cliente_id=str(uuid.uuid4()),
                    veiculo_id=str(ids["veiculo"]),
                    servicos=[],
                    pecas=[],
                )
            )


class TestConsultarStatusOsUseCase:
    def test_consultar_status_os_existente(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        consultar_uc = ConsultarStatusOsUseCase(os_repo)
        result = consultar_uc.execute(created.id)

        assert result.id == created.id
        assert result.status == "AGUARDANDO_APROVACAO"

    def test_consultar_status_inexistente_raises(self) -> None:
        repos = _setup_repositories()
        os_repo = repos[0]

        consultar_uc = ConsultarStatusOsUseCase(os_repo)
        with pytest.raises(OrdemServicoNaoEncontradaError):
            consultar_uc.execute(uuid.uuid4())


class TestAprovarOrcamentoUseCase:
    def test_aprovar_orcamento(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        aprovar_uc = AprovarOrcamentoUseCase(os_repo)
        result = aprovar_uc.execute(created.id, AprovarOrcamentoDTO(acao="APROVAR"))

        assert result.status == "EM_EXECUCAO"
        assert result.orcamento.aprovado is True

    def test_recusar_orcamento(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        aprovar_uc = AprovarOrcamentoUseCase(os_repo)
        result = aprovar_uc.execute(created.id, AprovarOrcamentoDTO(acao="RECUSAR"))

        assert result.status == "CANCELADA"
        assert result.orcamento.recusado is True

    def test_acao_invalida_raises(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        aprovar_uc = AprovarOrcamentoUseCase(os_repo)
        with pytest.raises(ValueError):
            aprovar_uc.execute(created.id, AprovarOrcamentoDTO(acao="INVALIDO"))


class TestListarOsUseCase:
    def test_listar_ordenado_por_status_e_data(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )

        os1 = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )
        abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico2"]))],
                pecas=[],
            )
        )

        aprovar_uc = AprovarOrcamentoUseCase(os_repo)
        aprovar_uc.execute(os1.id, AprovarOrcamentoDTO(acao="APROVAR"))

        listar_uc = ListarOsUseCase(os_repo)
        result = listar_uc.execute()

        assert len(result) == 2
        assert result[0].status == "EM_EXECUCAO"
        assert result[1].status == "AGUARDANDO_APROVACAO"

    def test_listar_exlui_finalizadas_e_entregues(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        os1 = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        aprovar_uc = AprovarOrcamentoUseCase(os_repo)
        aprovar_uc.execute(os1.id, AprovarOrcamentoDTO(acao="APROVAR"))

        atualizar_uc = AtualizarStatusOsUseCase(os_repo)
        atualizar_uc.execute(os1.id, AtualizarStatusDTO(novo_status="FINALIZADA"))

        listar_uc = ListarOsUseCase(os_repo)
        result = listar_uc.execute()

        assert len(result) == 0

    def test_listar_vazio(self) -> None:
        repos = _setup_repositories()
        os_repo = repos[0]

        listar_uc = ListarOsUseCase(os_repo)
        assert listar_uc.execute() == []


class TestDetalharOsUseCase:
    def test_detalhar_os_existente(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[ItemPecaInputDTO(peca_id=str(ids["peca1"]), quantidade=2)],
            )
        )

        detalhar_uc = DetalharOsUseCase(os_repo)
        result = detalhar_uc.execute(created.id)

        assert result.id == created.id
        assert len(result.orcamento.itens_servico) == 1
        assert len(result.orcamento.itens_peca) == 1
        assert result.orcamento.itens_peca[0].subtotal == 51.00

    def test_detalhar_inexistente_raises(self) -> None:
        repos = _setup_repositories()
        os_repo = repos[0]

        detalhar_uc = DetalharOsUseCase(os_repo)
        with pytest.raises(OrdemServicoNaoEncontradaError):
            detalhar_uc.execute(uuid.uuid4())


class TestAtualizarStatusOsUseCase:
    def test_atualizar_status_valido(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        aprovar_uc = AprovarOrcamentoUseCase(os_repo)
        aprovar_uc.execute(created.id, AprovarOrcamentoDTO(acao="APROVAR"))

        atualizar_uc = AtualizarStatusOsUseCase(os_repo)
        result = atualizar_uc.execute(
            created.id, AtualizarStatusDTO(novo_status="FINALIZADA")
        )

        assert result.status == "FINALIZADA"

    def test_atualizar_status_invalido_raises(self) -> None:
        repos = _setup_repositories()
        os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo = repos
        ids = _get_ids(repos)

        abrir_uc = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        created = abrir_uc.execute(
            AbrirOsDTO(
                cliente_id=str(ids["cliente"]),
                veiculo_id=str(ids["veiculo"]),
                servicos=[ItemServicoInputDTO(servico_id=str(ids["servico1"]))],
                pecas=[],
            )
        )

        atualizar_uc = AtualizarStatusOsUseCase(os_repo)
        with pytest.raises(TransicaoStatusInvalidaError):
            atualizar_uc.execute(
                created.id, AtualizarStatusDTO(novo_status="FINALIZADA")
            )

    def test_atualizar_inexistente_raises(self) -> None:
        repos = _setup_repositories()
        os_repo = repos[0]

        atualizar_uc = AtualizarStatusOsUseCase(os_repo)
        with pytest.raises(OrdemServicoNaoEncontradaError):
            atualizar_uc.execute(
                uuid.uuid4(), AtualizarStatusDTO(novo_status="FINALIZADA")
            )
