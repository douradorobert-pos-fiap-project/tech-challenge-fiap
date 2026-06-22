import pytest

from src.domain.exceptions.domain_exceptions import EmailInvalidoError
from src.domain.value_objects.email import Email


class TestEmail:
    def test_email_valido(self) -> None:
        email = Email("cliente@example.com")
        assert email.valor == "cliente@example.com"

    def test_email_com_subdominio(self) -> None:
        email = Email("user@mail.example.com")
        assert email.valor == "user@mail.example.com"

    def test_email_com_mais_e_arroba(self) -> None:
        email = Email("user+tag@example.com")
        assert email.valor == "user+tag@example.com"

    def test_email_com_espacos_e_stripped(self) -> None:
        email = Email("  user@example.com  ")
        assert email.valor == "user@example.com"

    def test_email_sem_arroba(self) -> None:
        with pytest.raises(EmailInvalidoError):
            Email("userexample.com")

    def test_email_sem_dominio(self) -> None:
        with pytest.raises(EmailInvalidoError):
            Email("user@")

    def test_email_sem_usuario(self) -> None:
        with pytest.raises(EmailInvalidoError):
            Email("@example.com")

    def test_email_com_espaco_no_meio(self) -> None:
        with pytest.raises(EmailInvalidoError):
            Email("user @example.com")

    def test_email_vazio(self) -> None:
        with pytest.raises(EmailInvalidoError):
            Email("")

    def test_igualdade(self) -> None:
        assert Email("user@example.com") == Email("user@example.com")

    def test_str_retorna_valor(self) -> None:
        assert str(Email("user@example.com")) == "user@example.com"
