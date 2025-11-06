import random
from typing import List
from .modelos import Cliente

class GeneradorClientes:
    """Genera clientes con características aleatorias"""
    
    def __init__(self):
        self.contador = 0
    
    def generar_cliente(self, max_articulos: int = 20) -> Cliente:
        """Genera un cliente con artículos y tiempo de cobro aleatorios"""
        self.contador += 1
        num_articulos = random.randint(1, max_articulos)
        tiempo_cobro = random.uniform(15, 30)
        return Cliente(self.contador, num_articulos, tiempo_cobro)
    
    def generar_multiples_clientes(self, cantidad: int, max_articulos: int = 20) -> List[Cliente]:
        """Genera múltiples clientes"""
        return [self.generar_cliente(max_articulos) for _ in range(cantidad)]
