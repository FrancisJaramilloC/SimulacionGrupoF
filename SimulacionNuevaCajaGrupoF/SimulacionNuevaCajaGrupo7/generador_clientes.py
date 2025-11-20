import random
from typing import List
from .modelos import Cliente

class GeneradorClientes:
    def __init__(self, semilla: int = None):
        if semilla is not None:
            random.seed(semilla)
        self.contador = 0

    def generar_cliente(self, max_articulos: int = 20) -> Cliente:
        self.contador += 1
        num_articulos = random.randint(1, max_articulos)
        tiempo_cobro = random.uniform(15, 30) / 60.0
        return Cliente(self.contador, num_articulos, tiempo_cobro)

    def generar_multiples_clientes(self, cantidad: int, max_articulos: int = 20) -> List[Cliente]:
        return [self.generar_cliente(max_articulos) for _ in range(cantidad)]
