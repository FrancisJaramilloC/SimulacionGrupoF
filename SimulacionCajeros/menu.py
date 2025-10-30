from .modelos import TipoCaja
from .configurador import Configurador
from .visualizador import Visualizador
from .simulador import Simulador
from .tuti import Tuti
import time

class Menu:
    """Maneja el menú principal del programa"""
    
    @staticmethod
    def modo_personalizado():
        """Ejecuta el modo de configuración personalizada"""
        tuti = Tuti()
        visualizador = Visualizador()
        
        # Configurar cajas
        Configurador.configurar_cajas(tuti)
        
        # Mostrar estado inicial
        print("\n📊 Estado inicial del Tuti:")
        visualizador.mostrar_estado_tuti(tuti, limpiar=False)

        # Simular nuevo cliente
        print("\n👤 NUEVO CLIENTE")
        num_articulos_nuevo = Configurador.solicitar_entero(
            "¿Cuántos artículos tiene el nuevo cliente?: ", 1
        )
        
        mejor_caja = tuti.encontrar_mejor_caja(num_articulos_nuevo)
        
        if mejor_caja:
            visualizador.mostrar_recomendacion(mejor_caja, num_articulos_nuevo)
        else:
            print(f"\n❌ No hay cajas disponibles para {num_articulos_nuevo} artículos")
        
        # Opción de simular
        print()
        simular = input("¿Deseas simular la atención de clientes? (s/n): ").lower()
        if simular == 's':
            velocidad = Configurador.solicitar_flotante(
                "Velocidad de simulación en segundos (recomendado 0.5-2): ", 0.1
            )
            simulador = Simulador(tuti, visualizador)
            simulador.ejecutar(velocidad)
        else:
            print("\n👋 ¡Gracias por usar el simulador!")
    
    @staticmethod
    def modo_ejemplo():
        """Ejecuta un ejemplo rápido predefinido"""
        print("Ejecutando ejemplo rápido...\n")
        time.sleep(1)
        
        tuti = Tuti()
        visualizador = Visualizador()
        
        # Crear configuración predefinida
        tuti.agregar_caja(TipoCaja.NORMAL, 5, 3)
        tuti.agregar_caja(TipoCaja.NORMAL, 7, 2)
        tuti.agregar_caja(TipoCaja.EXPRESS, 4, 5)
        
        visualizador.mostrar_estado_tuti(tuti)
        
        # Simular nuevo cliente
        import random
        num_articulos = random.randint(1, 50)
        print(f"\n👤 Nuevo cliente con {num_articulos} artículos")

        mejor_caja = tuti.encontrar_mejor_caja(num_articulos)
        if mejor_caja:
            visualizador.mostrar_recomendacion(mejor_caja, num_articulos)
        
        print()
        simular = input("¿Simular atención? (s/n): ").lower()
        if simular == 's':
            simulador = Simulador(tuti, visualizador)
            simulador.ejecutar(0.8)
    
    @staticmethod
    def ejecutar():
        """Ejecuta el menú principal"""
        print("\n" + "="*80)
        print("SIMULADOR DE CAJAS DE TUTI".center(80))
        print("="*80)
        print("\nOpciones:")
        print("1. Configuración personalizada")
        print("2. Ejemplo rápido")
        print()
        
        opcion = input("Selecciona una opción (1-2): ")
        print()
        
        if opcion == "1":
            Menu.modo_personalizado()
        elif opcion == "2":
            Menu.modo_ejemplo()
        else:
            print("Opción no válida. Ejecutando ejemplo rápido...")
            Menu.modo_ejemplo()
