from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Pedido:
    id: int
    rack: str
    cod_yazaki: str
    codigo_cabo: str
    seccao: str
    cor: str
    cliente: str
    locacao: str
    projeto: Optional[str] = None
    cod_oes: Optional[str] = None
    status: str = ''  # Campo mantido para compatibilidade, mas não utilizado
    data_criacao: datetime = datetime.now()
    data_atualizacao: Optional[datetime] = None

    @staticmethod
    def status_validos():
        return ['Pendente', 'Aceito', 'Em Preparação', 'Concluído']

    def atualizar_status(self, novo_status: str):
        if novo_status not in self.status_validos():
            raise ValueError(f"Status inválido. Status permitidos: {self.status_validos()}")
        self.status = novo_status
        self.data_atualizacao = datetime.now() 