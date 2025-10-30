from dataclasses import dataclass
from typing import List
from enum import Enum

class TipoCaja(Enum):
    NORMAL = "Normal"
    EXPRESS = "Express"

@dataclass
class Cliente:
    """Representa un cliente en la fila"""
    id: int
    num_articulos: int
    tiempo_cobro: float
    
    def __repr__(self):
        return f"👤({self.num_articulos})"

@dataclass
class Caja:
    """Representa una caja del supermercado"""
    numero: int
    tipo: TipoCaja
    tiempo_escaneo: float  # segundos por artículo
    clientes: List[Cliente]
    max_articulos: int = None
    
    def calcular_tiempo_total(self) -> float:
        """Calcula el tiempo total de atención en esta caja"""
        tiempo_total = 0
        for cliente in self.clientes:
            tiempo_total += (cliente.num_articulos * self.tiempo_escaneo) + cliente.tiempo_cobro
        return tiempo_total
    
    def atender_cliente(self) -> Cliente:
        """Atiende y retorna el primer cliente de la fila"""
        if self.clientes:
            return self.clientes.pop(0)
        return None
    
    def puede_usar_caja(self, num_articulos: int) -> bool:
        """Verifica si un cliente puede usar esta caja"""
        if self.max_articulos is None:
            return True
        return num_articulos <= self.max_articulos
    
    def agregar_cliente(self, cliente: Cliente):
        """Agrega un cliente a la fila"""
        self.clientes.append(cliente)