from typing import List
from .modelos import Caja, TipoCaja, Cliente
from .generador_clientes import GeneradorClientes

class Tuti:
    """Administra todas las cajas del supermercado"""
    
    def __init__(self):
        self.cajas: List[Caja] = []
        self.generador = GeneradorClientes()
        
    def agregar_caja(self, tipo: TipoCaja, tiempo_escaneo: float, num_clientes: int):
        """Agrega una nueva caja al supermercado"""
        numero = len(self.cajas) + 1
        max_articulos = 10 if tipo == TipoCaja.EXPRESS else None
        
        # Generar clientes
        clientes = self.generador.generar_multiples_clientes(
            num_clientes, 
            max_articulos if max_articulos else 50
        )
        
        caja = Caja(numero, tipo, tiempo_escaneo, clientes, max_articulos)
        self.cajas.append(caja)
        return caja
    
    def encontrar_mejor_caja(self, num_articulos: int) -> Caja:
        """Encuentra la caja con menor tiempo de espera para un cliente"""
        cajas_disponibles = [c for c in self.cajas if c.puede_usar_caja(num_articulos)]
        
        if not cajas_disponibles:
            return None
        
        mejor_caja = min(cajas_disponibles, key=lambda c: c.calcular_tiempo_total())
        return mejor_caja
    
    def tiene_clientes_en_espera(self) -> bool:
        """Verifica si hay clientes esperando en alguna caja"""
        return any(len(caja.clientes) > 0 for caja in self.cajas)
    
    def atender_todos(self) -> List[tuple]:
        """Atiende un cliente de cada caja que tenga clientes"""
        atenciones = []
        for caja in self.cajas:
            if caja.clientes:
                cliente = caja.atender_cliente()
                tiempo_atencion = (cliente.num_articulos * caja.tiempo_escaneo) + cliente.tiempo_cobro
                atenciones.append((caja, cliente, tiempo_atencion))
        return atenciones