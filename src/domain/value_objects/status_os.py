from enum import IntEnum


class StatusOS(IntEnum):
    RECEBIDA = 1
    DIAGNOSTICO = 2
    AGUARDANDO_APROVACAO = 3
    EM_EXECUCAO = 4
    FINALIZADA = 5
    ENTREGUE = 6
    CANCELADA = 7

    @classmethod
    def from_string(cls, valor: str) -> "StatusOS":
        mapping = {
            "RECEBIDA": cls.RECEBIDA,
            "DIAGNOSTICO": cls.DIAGNOSTICO,
            "AGUARDANDO_APROVACAO": cls.AGUARDANDO_APROVACAO,
            "EM_EXECUCAO": cls.EM_EXECUCAO,
            "FINALIZADA": cls.FINALIZADA,
            "ENTREGUE": cls.ENTREGUE,
            "CANCELADA": cls.CANCELADA,
        }
        return mapping[valor.upper()]

    def __str__(self) -> str:
        return self.name

    @property
    def ordem_listagem(self) -> int:
        ordem = {
            StatusOS.EM_EXECUCAO: 0,
            StatusOS.AGUARDANDO_APROVACAO: 1,
            StatusOS.DIAGNOSTICO: 2,
            StatusOS.RECEBIDA: 3,
            StatusOS.FINALIZADA: 4,
            StatusOS.ENTREGUE: 5,
            StatusOS.CANCELADA: 6,
        }
        return ordem[self]

    @property
    def is_finalizada(self) -> bool:
        return self in (StatusOS.FINALIZADA, StatusOS.ENTREGUE)

    @property
    def deve_ser_ocultada(self) -> bool:
        return self.is_finalizada
