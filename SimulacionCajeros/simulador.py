import time
from .tuti import Tuti
from .visualizador_pygame import PygameVisualizador

class Simulador:
    """Ejecuta la simulación de atención de clientes"""
    
    def __init__(self, tuti: Tuti, visualizador: PygameVisualizador):
        self.tuti = tuti
        self.visualizador = visualizador
    
    def ejecutar(self, velocidad: float = 0.5):
        """Ejecuta la simulación completa"""
        print("\nIniciando simulación...\n")
        time.sleep(2)
        
        while self.tuti.tiene_clientes_en_espera():
            self.visualizador.mostrar_estado_tuti(self.tuti)
            
            # Atender clientes
            atenciones = self.tuti.atender_todos()
            for caja, cliente, tiempo in atenciones:
                self.visualizador.mostrar_atencion(caja, cliente, tiempo)
            
            print(f"\n⏳ Procesando... (espera {velocidad}s)")
            time.sleep(velocidad)
        
        self.visualizador.mostrar_estado_tuti(self.tuti)
        print("Simulación completada. Todas las cajas están vacías.\n")
