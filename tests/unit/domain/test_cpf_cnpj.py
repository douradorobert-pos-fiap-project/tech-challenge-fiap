import pytest

from src.domain.exceptions.domain_exceptions import CNPJInvalidoError, CPFInvalidoError
from src.domain.value_objects.cpf_cnpj import CpfCnpj


class TestCPF:
    def test_cpf_valido_sem_formatacao(self) -> None:
        cpf = CpfCnpj("52998224725")
        assert cpf.valor == "52998224725"
        assert cpf.is_cpf is True
        assert cpf.is_cnpj is False

    def test_cpf_valido_com_formatacao(self) -> None:
        cpf = CpfCnpj("529.982.247-25")
        assert cpf.valor == "52998224725"
        assert cpf.formatado == "529.982.247-25"

    def test_cpf_todos_digitos_iguais_e_invalido(self) -> None:
        with pytest.raises(CPFInvalidoError):
            CpfCnpj("11111111111")

    def test_cpf_digito_verificador_invalido(self) -> None:
        with pytest.raises(CPFInvalidoError):
            CpfCnpj("52998224726")

    def test_cpf_com_letras_e_invalido(self) -> None:
        with pytest.raises((CPFInvalidoError, CNPJInvalidoError)):
            CpfCnpj("5299822472X")

    def test_cpf_muito_curto(self) -> None:
        with pytest.raises((CPFInvalidoError, CNPJInvalidoError)):
            CpfCnpj("123")

    def test_igualdade_entre_cpfs(self) -> None:
        cpf1 = CpfCnpj("52998224725")
        cpf2 = CpfCnpj("529.982.247-25")
        assert cpf1 == cpf2

    def test_str_retorna_formatado(self) -> None:
        cpf = CpfCnpj("52998224725")
        assert str(cpf) == "529.982.247-25"

    def test_hash_consistente(self) -> None:
        cpf1 = CpfCnpj("52998224725")
        cpf2 = CpfCnpj("529.982.247-25")
        assert hash(cpf1) == hash(cpf2)


class TestCNPJ:
    def test_cnpj_valido_sem_formatacao(self) -> None:
        cnpj = CpfCnpj("11444777000161")
        assert cnpj.valor == "11444777000161"
        assert cnpj.is_cnpj is True
        assert cnpj.is_cpf is False

    def test_cnpj_valido_com_formatacao(self) -> None:
        cnpj = CpfCnpj("11.444.777/0001-61")
        assert cnpj.valor == "11444777000161"
        assert cnpj.formatado == "11.444.777/0001-61"

    def test_cnpj_todos_digitos_iguais_e_invalido(self) -> None:
        with pytest.raises(CNPJInvalidoError):
            CpfCnpj("11111111111111")

    def test_cnpj_digito_verificador_invalido(self) -> None:
        with pytest.raises(CNPJInvalidoError):
            CpfCnpj("11444777000162")

    def test_cnpj_com_pontuacao_extra(self) -> None:
        cnpj = CpfCnpj("  11.444.777/0001-61  ")
        assert cnpj.valor == "11444777000161"

    def test_igualdade_entre_cnpjs(self) -> None:
        cnpj1 = CpfCnpj("11444777000161")
        cnpj2 = CpfCnpj("11.444.777/0001-61")
        assert cnpj1 == cnpj2
