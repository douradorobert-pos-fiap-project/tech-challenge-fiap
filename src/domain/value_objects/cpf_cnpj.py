import re

from src.domain.exceptions.domain_exceptions import CNPJInvalidoError, CPFInvalidoError


class CpfCnpj:
    _CPF_PATTERN = re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
    _CNPJ_PATTERN = re.compile(r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$")
    _CPF_LENGTH = 11
    _CNPJ_LENGTH = 14

    def __init__(self, valor: str) -> None:
        self._valor = self._validar(valor)

    @property
    def valor(self) -> str:
        return self._valor

    @property
    def is_cpf(self) -> bool:
        return len(self._valor) == self._CPF_LENGTH

    @property
    def is_cnpj(self) -> bool:
        return len(self._valor) == self._CNPJ_LENGTH

    @property
    def formatado(self) -> str:
        digitos = self._valor
        if self.is_cpf:
            return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"

    def _validar(self, valor: str) -> str:
        valor = re.sub(r"[^0-9]", "", valor)

        if len(valor) == self._CPF_LENGTH:
            if not self._validar_cpf(valor):
                raise CPFInvalidoError(valor)
            return valor

        if len(valor) == self._CNPJ_LENGTH:
            if not self._validar_cnpj(valor):
                raise CNPJInvalidoError(valor)
            return valor

        if len(valor) == self._CPF_LENGTH:
            raise CPFInvalidoError(valor)
        raise CNPJInvalidoError(valor)

    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        if len(set(cpf)) == 1:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        digito1 = 0 if resto == 10 else resto
        if digito1 != int(cpf[9]):
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        digito2 = 0 if resto == 10 else resto
        return digito2 == int(cpf[10])

    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        if len(set(cnpj)) == 1:
            return False

        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        if digito1 != int(cnpj[12]):
            return False

        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        return digito2 == int(cnpj[13])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CpfCnpj):
            return False
        return self._valor == other._valor

    def __hash__(self) -> int:
        return hash(self._valor)

    def __str__(self) -> str:
        return self.formatado

    def __repr__(self) -> str:
        return f"CpfCnpj({self.formatado!r})"
