import os
from .modelos import Caja, TipoCaja, Cliente
from .tuti import Tuti

class Visualizador:
    """Maneja la visualización del estado del tuti"""
    
    @staticmethod
    def limpiar_pantalla():
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def mostrar_cabecera():
        """Muestra la cabecera del programa"""
        print("=" * 80)
        print("SIMULACIÓN DE CAJAS DEL TUTI".center(80))
        print("=" * 80)
        print()
    
    @staticmethod
    def mostrar_caja(caja: Caja):
        """Muestra el estado de una caja"""
        tiempo_total = caja.calcular_tiempo_total()
        color = "🟢" if caja.tipo == TipoCaja.EXPRESS else "🔵"
        
        print(f"{color} CAJA {caja.numero} - {caja.tipo.value}")
        print(f"   Velocidad: {caja.tiempo_escaneo}s/artículo")
        if caja.max_articulos:
            print(f"   Límite: {caja.max_articulos} artículos máximo")
        print(f"   Clientes en fila: {len(caja.clientes)}")
        print(f"   Tiempo total estimado: {tiempo_total:.1f} segundos ({tiempo_total/60:.1f} min)")
        
        # Mostrar los clientes en la fila
        if caja.clientes:
            print(f"   Fila: ", end="")
            for i, cliente in enumerate(caja.clientes[:15]):
                print(cliente, end=" ")
            if len(caja.clientes) > 15:
                print(f"... +{len(caja.clientes)-15} más", end="")
            print()
        else:
            print(f"   Fila: (vacía)")
        
        print()
    
    @staticmethod
    def mostrar_estado_tuti(tuti:  Tuti, limpiar=True):
        """Muestra el estado completo del tuti"""
        if limpiar:
            Visualizador.limpiar_pantalla()
        
        Visualizador.mostrar_cabecera()
        
        for caja in tuti.cajas:
            Visualizador.mostrar_caja(caja)
        
        print("=" * 80)
    
    @staticmethod
    def mostrar_atencion(caja: Caja, cliente: Cliente, tiempo: float):
        """Muestra información de una atención en progreso"""
        print(f"Esta es la Caja chevere {caja.numero}: Atendiendo cliente #{cliente.id} "
              f"({cliente.num_articulos} artículos) - {tiempo:.1f}s")
    
    @staticmethod
    def mostrar_recomendacion(caja: Caja, num_articulos: int):
        """Muestra recomendación de caja para un nuevo cliente"""
        tiempo_espera = caja.calcular_tiempo_total()
        print(f"\nRECOMENDACIÓN: Ir a la Caja {caja.numero} ({caja.tipo.value})")
        print(f"   Tiempo de espera estimado: {tiempo_espera:.1f} segundos ({tiempo_espera/60:.1f} minutos)")
