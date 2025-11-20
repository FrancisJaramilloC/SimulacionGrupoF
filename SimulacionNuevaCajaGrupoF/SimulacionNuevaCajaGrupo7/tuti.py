from typing import List, Optional
from .modelos import Caja, TipoCaja
from .generador_clientes import GeneradorClientes

class Tuti:
    def __init__(self):
        self.cajas: List[Caja] = []
        self.generador = GeneradorClientes()

    def agregar_caja(self, tipo: TipoCaja, tiempo_escaneo: float, num_clientes: int = 0):
        numero = len(self.cajas) + 1
        max_articulos = 10 if tipo == TipoCaja.EXPRESS else None
        clientes = self.generador.generar_multiples_clientes(num_clientes, max_articulos or 20)
        caja = Caja(numero, tipo, tiempo_escaneo, clientes, max_articulos)
        self.cajas.append(caja)
        return caja

    def encontrar_mejor_caja(self, num_articulos: int) -> Optional[Caja]:
        candidatas = [c for c in self.cajas if c.puede_usar_caja(num_articulos)]
        if not candidatas:
            return None
        def carga(caja: Caja):
            return sum(caja.calcular_tiempo_servicio_cliente(cli) for cli in caja.clientes)
        return min(candidatas, key=carga)

    def total_clientes_esperando(self) -> int:
        return sum(max(0, len(c.clientes)) for c in self.cajas)
