from typing import List
import time
from .modelos import Caja, TipoCaja
from .generador_clientes import GeneradorClientes
from .estadisticas import EstadisticasSupermercado

class Tuti:
    """Administra todas las cajas del tuti"""
    
    def __init__(self):
        self.cajas: List[Caja] = []
        self.generador = GeneradorClientes()
        self.estadisticas = EstadisticasSupermercado()  # ← CRÍTICO: Inicializar estadísticas
        self.tiempo_inicio_caja = {}  # Para rastrear cuándo empezó a atender cada caja
        
    def agregar_caja(self, tipo: TipoCaja, tiempo_escaneo: float, num_clientes: int):
        """Agrega una nueva caja al tuti"""
        numero = len(self.cajas) + 1
        max_articulos = 10 if tipo == TipoCaja.EXPRESS else None
        
        # Generar clientes, respetando el límite de la caja express
        clientes = self.generador.generar_multiples_clientes(
            num_clientes,
            max_articulos=max_articulos if max_articulos else 20
        )
        
        # Registrar clientes en estadísticas
        for _ in clientes:
            self.estadisticas.registrar_cliente_en_cola()
        
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
        tiempo_actual = time.time()
        
        for caja in self.cajas:
            if caja.clientes:
                # Calcular tiempo de espera (tiempo que estuvo en cola)
                tiempo_en_cola = caja.calcular_tiempo_total()
                tiempo_cliente_actual = (caja.clientes[0].num_articulos * caja.tiempo_escaneo + caja.clientes[0].tiempo_cobro)
                tiempo_espera = max(0, tiempo_en_cola - tiempo_cliente_actual)
                
                # Registrar inicio de atención
                self.estadisticas.registrar_inicio_atencion(caja.numero, tiempo_espera)
                
                # Atender cliente
                cliente = caja.atender_cliente()
                tiempo_atencion = (cliente.num_articulos * caja.tiempo_escaneo) + cliente.tiempo_cobro
                
                # Registrar fin de atención
                self.estadisticas.registrar_fin_atencion(caja.numero, tiempo_atencion)
                
                atenciones.append((caja, cliente, tiempo_atencion))
                
                # Registrar tiempo de inicio para esta caja
                self.tiempo_inicio_caja[caja.numero] = tiempo_actual
            else:
                # Si la caja está inactiva, registrar tiempo inactivo
                if caja.numero in self.tiempo_inicio_caja:
                    tiempo_inactivo = tiempo_actual - self.tiempo_inicio_caja[caja.numero]
                    self.estadisticas.registrar_tiempo_inactivo(caja.numero, tiempo_inactivo)
        
        return atenciones
    
    def obtener_estadisticas(self) -> EstadisticasSupermercado:
        """Retorna el objeto de estadísticas"""
        return self.estadisticas