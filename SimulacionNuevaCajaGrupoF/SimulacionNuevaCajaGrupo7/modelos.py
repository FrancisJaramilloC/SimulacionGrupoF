from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class TipoCaja(Enum):
    NORMAL = "Normal"
    EXPRESS = "Express"

@dataclass
class Cliente:
    id: int
    num_articulos: int
    tiempo_cobro: float
    tiempo_llegada: float = 0.0
    tiempo_inicio_servicio: float = None
    tiempo_fin_servicio: float = None

@dataclass
class Caja:
    numero: int
    tipo: TipoCaja
    tiempo_escaneo: float
    clientes: List[Cliente] = field(default_factory=list)
    max_articulos: Optional[int] = None
    busy_time: float = 0.0
    ultimo_inicio_ocupado: float = None

    def puede_usar_caja(self, num_articulos: int) -> bool:
        if self.max_articulos is None:
            return True
        return num_articulos <= self.max_articulos

    def agregar_cliente(self, cliente: Cliente):
        self.clientes.append(cliente)

    def pop_cliente(self):
        return self.clientes.pop(0) if self.clientes else None

    def calcular_tiempo_servicio_cliente(self, cliente: Cliente) -> float:
        return cliente.num_articulos * self.tiempo_escaneo + cliente.tiempo_cobro
