from src.domain.value_objects.status_os import StatusOS


class TestStatusOS:
    def test_ordem_listagem_em_execucao_primeiro(self) -> None:
        assert StatusOS.EM_EXECUCAO.ordem_listagem == 0

    def test_ordem_listagem_aguardando_aprovacao_segundo(self) -> None:
        assert StatusOS.AGUARDANDO_APROVACAO.ordem_listagem == 1

    def test_ordem_listagem_diagnostico_terceiro(self) -> None:
        assert StatusOS.DIAGNOSTICO.ordem_listagem == 2

    def test_ordem_listagem_recebida_quarto(self) -> None:
        assert StatusOS.RECEBIDA.ordem_listagem == 3

    def test_ordem_listagem_finalizada(self) -> None:
        assert StatusOS.FINALIZADA.ordem_listagem == 4

    def test_ordem_listagem_entregue(self) -> None:
        assert StatusOS.ENTREGUE.ordem_listagem == 5

    def test_ordem_correta(self) -> None:
        assert (
            StatusOS.EM_EXECUCAO.ordem_listagem
            < StatusOS.AGUARDANDO_APROVACAO.ordem_listagem
            < StatusOS.DIAGNOSTICO.ordem_listagem
            < StatusOS.RECEBIDA.ordem_listagem
            < StatusOS.FINALIZADA.ordem_listagem
            < StatusOS.ENTREGUE.ordem_listagem
        )

    def test_is_finalizada_para_finalizada(self) -> None:
        assert StatusOS.FINALIZADA.is_finalizada is True

    def test_is_finalizada_para_entregue(self) -> None:
        assert StatusOS.ENTREGUE.is_finalizada is True

    def test_is_finalizada_para_recebida(self) -> None:
        assert StatusOS.RECEBIDA.is_finalizada is False

    def test_deve_ser_ocultada_para_finalizada(self) -> None:
        assert StatusOS.FINALIZADA.deve_ser_ocultada is True

    def test_deve_ser_ocultada_para_entregue(self) -> None:
        assert StatusOS.ENTREGUE.deve_ser_ocultada is True

    def test_deve_ser_ocultada_para_recebida(self) -> None:
        assert StatusOS.RECEBIDA.deve_ser_ocultada is False

    def test_from_string(self) -> None:
        assert StatusOS.from_string("RECEBIDA") == StatusOS.RECEBIDA
        assert StatusOS.from_string("em_execucao") == StatusOS.EM_EXECUCAO

    def test_str(self) -> None:
        assert str(StatusOS.RECEBIDA) == "RECEBIDA"
