import time
from .tuti import Tuti
from .visualizador import Visualizador

class Simulador:
    """Ejecuta la simulación de atención de clientes"""
    
    def __init__(self, tuti: Tuti, visualizador: Visualizador):
        self.tuti = tuti
        self.visualizador = visualizador
        self.contador_iteraciones = 0
    
    def ejecutar(self, velocidad: float = 0.5):
        """Ejecuta la simulación completa"""
        print("\n🚀 Iniciando simulación...\n")
        time.sleep(2)
        
        while self.tuti.tiene_clientes_en_espera():
            self.visualizador.mostrar_estado_tuti(self.tuti)
            
            # Atender clientes
            atenciones = self.tuti.atender_todos()
            for caja, cliente, tiempo in atenciones:
                self.visualizador.mostrar_atencion(caja, cliente, tiempo)
            
            # Mostrar estadísticas cada 3 iteraciones
            self.contador_iteraciones += 1
            if self.contador_iteraciones % 3 == 0:
                print("\n" + "─" * 80)
                self.tuti.estadisticas.mostrar_estadisticas()
                print("─" * 80)
            
            print(f"\n⏳ Procesando... (espera {velocidad}s)")
            time.sleep(velocidad)
        
        # Mostrar estado final
        self.visualizador.mostrar_estado_tuti(self.tuti)
        print("✅ Simulación completada. Todas las cajas están vacías.\n")
        
        # Mostrar estadísticas finales
        print("\n" + "="*80)
        print("ESTADÍSTICAS FINALES DE LA SIMULACIÓN".center(80))
        print("="*80)
        self.tuti.estadisticas.mostrar_estadisticas()
        
        # Preguntar si desea exportar
        exportar = input("\n¿Deseas exportar las estadísticas a un archivo? (s/n): ").lower()
        if exportar == 's':
            nombre_archivo = input("Nombre del archivo (presiona Enter para usar 'resumen_simulacion.txt'): ").strip()
            if not nombre_archivo:
                nombre_archivo = "resumen_simulacion.txt"
            elif not nombre_archivo.endswith('.txt'):
                nombre_archivo += '.txt'
            
            self.tuti.estadisticas.exportar_resumen(nombre_archivo)
            print(f"✅ Estadísticas exportadas a '{nombre_archivo}'")