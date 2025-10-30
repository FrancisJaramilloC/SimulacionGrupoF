from .tuti import Tuti
from .modelos import TipoCaja

class Configurador:
    """Maneja la configuración interactiva del Tuti"""
    
    @staticmethod
    def solicitar_entero(mensaje: str, minimo: int = 0, maximo: int = None) -> int:
        """Solicita un número entero con validación"""
        while True:
            try:
                valor = int(input(mensaje))
                if minimo is not None and valor < minimo:
                    print(f"❌ El valor debe ser mayor o igual a {minimo}")
                    continue
                if maximo is not None and valor > maximo:
                    print(f"❌ El valor debe ser menor o igual a {maximo}")
                    continue
                return valor
            except ValueError:
                print("❌ Por favor ingresa un número válido")
    
    @staticmethod
    def solicitar_flotante(mensaje: str, minimo: float = 0) -> float:
        """Solicita un número flotante con validación"""
        while True:
            try:
                valor = float(input(mensaje))
                if valor < minimo:
                    print(f"❌ El valor debe ser mayor o igual a {minimo}")
                    continue
                return valor
            except ValueError:
                print("❌ Por favor ingresa un número válido")
    
    @staticmethod
    def configurar_cajas(tuti: Tuti):
        """Configura todas las cajas del Tuti"""
        print("=" * 80)
        print("CONFIGURACIÓN DEL Tuti".center(80))
        print("=" * 80)
        print()
        
        # Cajas normales
        num_cajas_normales = Configurador.solicitar_entero(
            "¿Cuántas cajas NORMALES deseas? (1-5): ", 1, 5
        )
        
        for i in range(num_cajas_normales):
            print(f"\n--- Configuración Caja Normal #{i+1} ---")
            num_clientes = Configurador.solicitar_entero(
                "  Número de clientes en fila: ", 0
            )
            tiempo_escaneo = Configurador.solicitar_flotante(
                "  Tiempo de escaneo por artículo (segundos): ", 0.1
            )
            tuti.agregar_caja(TipoCaja.NORMAL, tiempo_escaneo, num_clientes)
        
        # Cajas express
        print()
        num_cajas_express = Configurador.solicitar_entero(
            "¿Cuántas cajas EXPRESS deseas? (0-3): ", 0, 3
        )
        
        for i in range(num_cajas_express):
            print(f"\n--- Configuración Caja Express #{i+1} ---")
            num_clientes = Configurador.solicitar_entero(
                "  Número de clientes en fila: ", 0
            )
            tiempo_escaneo = Configurador.solicitar_flotante(
                "  Tiempo de escaneo por artículo (segundos): ", 0.1
            )
            tuti.agregar_caja(TipoCaja.EXPRESS, tiempo_escaneo, num_clientes)
