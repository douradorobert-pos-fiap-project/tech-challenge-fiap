class DomainException(Exception):
    pass


class CPFInvalidoError(DomainException):
    def __init__(self, valor: str) -> None:
        super().__init__(f"CPF invalido: {valor}")


class CNPJInvalidoError(DomainException):
    def __init__(self, valor: str) -> None:
        super().__init__(f"CNPJ invalido: {valor}")


class PlacaInvalidaError(DomainException):
    def __init__(self, valor: str) -> None:
        super().__init__(f"Placa invalida: {valor}")


class EmailInvalidoError(DomainException):
    def __init__(self, valor: str) -> None:
        super().__init__(f"Email invalido: {valor}")


class DinheiroNegativoError(DomainException):
    def __init__(self, valor: str) -> None:
        super().__init__(f"Valor monetario nao pode ser negativo: {valor}")


class EstoqueInsuficienteError(DomainException):
    def __init__(self, peca_nome: str, solicitado: int, disponivel: int) -> None:
        super().__init__(
            f"Estoque insuficiente para {peca_nome}: solicitado={solicitado}, disponivel={disponivel}"
        )


class TransicaoStatusInvalidaError(DomainException):
    def __init__(self, status_atual: str, novo_status: str) -> None:
        super().__init__(
            f"Transicao de status invalida: {status_atual} -> {novo_status}"
        )


class OrdemServicoNaoEncontradaError(DomainException):
    def __init__(self, os_id: str) -> None:
        super().__init__(f"Ordem de servico nao encontrada: {os_id}")


class OrcamentoJaAprovadoError(DomainException):
    def __init__(self, os_id: str) -> None:
        super().__init__(f"Orcamento ja aprovado para OS: {os_id}")


class OrcamentoJaRecusadoError(DomainException):
    def __init__(self, os_id: str) -> None:
        super().__init__(f"Orcamento ja recusado para OS: {os_id}")


class ClienteNaoEncontradoError(DomainException):
    def __init__(self, cliente_id: str) -> None:
        super().__init__(f"Cliente nao encontrado: {cliente_id}")


class VeiculoNaoEncontradoError(DomainException):
    def __init__(self, veiculo_id: str) -> None:
        super().__init__(f"Veiculo nao encontrado: {veiculo_id}")


class ServicoNaoEncontradoError(DomainException):
    def __init__(self, servico_id: str) -> None:
        super().__init__(f"Servico nao encontrado: {servico_id}")


class PecaNaoEncontradaError(DomainException):
    def __init__(self, peca_id: str) -> None:
        super().__init__(f"Peca nao encontrada: {peca_id}")
