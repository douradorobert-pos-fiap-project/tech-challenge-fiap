import pytest

from src.domain.entities.orcamento import Orcamento
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.exceptions.domain_exceptions import (
    OrcamentoJaAprovadoError,
    OrcamentoJaRecusadoError,
    TransicaoStatusInvalidaError,
)
from src.domain.value_objects.status_os import StatusOS


class TestOrdemServico:
    def _criar_os(self) -> OrdemServico:
        return OrdemServico(cliente_id=None, veiculo_id=None)

    def test_os_criada_com_status_recebida(self) -> None:
        os = self._criar_os()
        assert os.status == StatusOS.RECEBIDA
        assert os.deletada is False
        assert os.criada_em is not None

    def test_transicao_recebida_para_diagnostico(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        assert os.status == StatusOS.DIAGNOSTICO

    def test_transicao_diagnostico_para_aguardando(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        assert os.status == StatusOS.AGUARDANDO_APROVACAO

    def test_transicao_aguardando_para_execucao(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        assert os.status == StatusOS.EM_EXECUCAO

    def test_transicao_execucao_para_finalizada(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        os.finalizar()
        assert os.status == StatusOS.FINALIZADA
        assert os.finalizada_em is not None

    def test_transicao_finalizada_para_entregue(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        os.finalizar()
        os.entregar()
        assert os.status == StatusOS.ENTREGUE
        assert os.entregue_em is not None
        assert os.deletada is True

    def test_transicao_invalida_recebida_para_execucao(self) -> None:
        os = self._criar_os()
        with pytest.raises(TransicaoStatusInvalidaError):
            os.executar()

    def test_transicao_invalida_diagnostico_para_finalizada(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        with pytest.raises(TransicaoStatusInvalidaError):
            os.finalizar()

    def test_transicao_invalida_entregue_para_qualquer(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        os.finalizar()
        os.entregar()
        with pytest.raises(TransicaoStatusInvalidaError):
            os.iniciar_diagnostico()

    def test_cancelar_de_recebida(self) -> None:
        os = self._criar_os()
        os.cancelar()
        assert os.status == StatusOS.CANCELADA

    def test_cancelar_de_execucao(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        os.cancelar()
        assert os.status == StatusOS.CANCELADA

    def test_transicao_mesmo_status_e_noop(self) -> None:
        os = self._criar_os()
        os.transitar_status(StatusOS.RECEBIDA)
        assert os.status == StatusOS.RECEBIDA

    def test_aprovar_orcamento_transita_para_execucao(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.aprovar_orcamento()
        assert os.orcamento.aprovado is True
        assert os.status == StatusOS.EM_EXECUCAO

    def test_aprovar_orcamento_ja_aprovado_raises(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.aprovar_orcamento()
        with pytest.raises(OrcamentoJaAprovadoError):
            os.aprovar_orcamento()

    def test_recusar_orcamento_cancela_os(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.recusar_orcamento()
        assert os.orcamento.recusado is True
        assert os.status == StatusOS.CANCELADA

    def test_recusar_orcamento_ja_recusado_raises(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.recusar_orcamento()
        with pytest.raises(OrcamentoJaRecusadoError):
            os.recusar_orcamento()

    def test_recusar_orcamento_ja_aprovado_raises(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.aprovar_orcamento()
        with pytest.raises(OrcamentoJaAprovadoError):
            os.recusar_orcamento()

    def test_soft_delete(self) -> None:
        os = self._criar_os()
        os.soft_delete()
        assert os.deletada is True

    def test_deve_ser_ocultada_recebida(self) -> None:
        os = self._criar_os()
        assert os.deve_ser_ocultada is False

    def test_deve_ser_ocultada_finalizada(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        os.finalizar()
        assert os.deve_ser_ocultada is True

    def test_deve_ser_ocultada_entregue(self) -> None:
        os = self._criar_os()
        os.iniciar_diagnostico()
        os.aguardar_aprovacao()
        os.executar()
        os.finalizar()
        os.entregar()
        assert os.deve_ser_ocultada is True

    def test_deve_ser_ocultada_deletada(self) -> None:
        os = self._criar_os()
        os.soft_delete()
        assert os.deve_ser_ocultada is True


class TestOrcamento:
    def test_orcamento_vazio_total_zero(self) -> None:
        orcamento = Orcamento()
        assert orcamento.total.valor == 0
        assert orcamento.total_servicos.valor == 0
        assert orcamento.total_pecas.valor == 0

    def test_orcamento_pendente(self) -> None:
        orcamento = Orcamento()
        assert orcamento.pendente is True

    def test_aprovar_orcamento(self) -> None:
        orcamento = Orcamento()
        orcamento.aprovar()
        assert orcamento.aprovado is True
        assert orcamento.pendente is False

    def test_recusar_orcamento(self) -> None:
        orcamento = Orcamento()
        orcamento.recusar()
        assert orcamento.recusado is True
        assert orcamento.pendente is False

    def test_aprovar_ja_aprovado_raises(self) -> None:
        orcamento = Orcamento()
        orcamento.aprovar()
        with pytest.raises(ValueError, match="aprovado"):
            orcamento.aprovar()

    def test_recusar_ja_recusado_raises(self) -> None:
        orcamento = Orcamento()
        orcamento.recusar()
        with pytest.raises(ValueError, match="recusado"):
            orcamento.recusar()

    def test_aprovar_ja_recusado_raises(self) -> None:
        orcamento = Orcamento()
        orcamento.recusar()
        with pytest.raises(ValueError, match="recusado"):
            orcamento.aprovar()
