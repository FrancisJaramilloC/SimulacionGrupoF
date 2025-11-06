import time
from collections import defaultdict

class EstadisticasSupermercado:
    def __init__(self):
        self.clientes_atendidos = 0
        self.clientes_en_espera = 0
        self.tiempo_total_espera = 0
        self.tiempo_inicio = time.time()
        
        # Estadísticas por caja
        self.cajas_stats = defaultdict(lambda: {
            'clientes_atendidos': 0,
            'tiempo_total_atencion': 0,
            'tiempo_inactivo': 0
        })
        
        # Historial de tiempos de espera
        self.tiempos_espera = []
        self.tiempos_atencion = []
    
    def registrar_cliente_en_cola(self):
        """Registra cuando un cliente entra a la cola"""
        self.clientes_en_espera += 1
    
    def registrar_inicio_atencion(self, id_caja, tiempo_espera):
        """Registra cuando un cliente empieza a ser atendido"""
        self.clientes_en_espera -= 1
        self.tiempo_total_espera += tiempo_espera
        self.tiempos_espera.append(tiempo_espera)
    
    def registrar_fin_atencion(self, id_caja, tiempo_atencion):
        """Registra cuando un cliente termina de ser atendido"""
        self.clientes_atendidos += 1
        self.cajas_stats[id_caja]['clientes_atendidos'] += 1
        self.cajas_stats[id_caja]['tiempo_total_atencion'] += tiempo_atencion
        self.tiempos_atencion.append(tiempo_atencion)
    
    def registrar_tiempo_inactivo(self, id_caja, tiempo_inactivo):
        """Registra tiempo que una caja estuvo sin atender clientes"""
        self.cajas_stats[id_caja]['tiempo_inactivo'] += tiempo_inactivo
    
    def get_tiempo_promedio_espera(self):
        """Retorna el tiempo promedio de espera en segundos"""
        if self.clientes_atendidos == 0:
            return 0
        return self.tiempo_total_espera / self.clientes_atendidos
    
    def get_tiempo_promedio_atencion(self):
        """Retorna el tiempo promedio de atención en segundos"""
        if not self.tiempos_atencion:
            return 0
        return sum(self.tiempos_atencion) / len(self.tiempos_atencion)
    
    def get_eficiencia_caja(self, id_caja):
        """Calcula el porcentaje de eficiencia de una caja"""
        stats = self.cajas_stats[id_caja]
        tiempo_total = stats['tiempo_total_atencion'] + stats['tiempo_inactivo']
        if tiempo_total == 0:
            return 0
        return (stats['tiempo_total_atencion'] / tiempo_total) * 100
    
    def get_clientes_por_minuto(self):
        """Calcula la tasa de clientes atendidos por minuto"""
        tiempo_transcurrido = (time.time() - self.tiempo_inicio) / 60  # en minutos
        if tiempo_transcurrido == 0:
            return 0
        return self.clientes_atendidos / tiempo_transcurrido
    
    def mostrar_estadisticas(self):
        """Muestra un resumen de las estadísticas en tiempo real"""
        print("\n" + "="*50)
        print("ESTADÍSTICAS EN TIEMPO REAL")
        print("="*50)
        print(f"Clientes atendidos: {self.clientes_atendidos}")
        print(f"Clientes en espera: {self.clientes_en_espera}")
        print(f"Tiempo promedio de espera: {self.get_tiempo_promedio_espera():.2f} seg")
        print(f"Tiempo promedio de atención: {self.get_tiempo_promedio_atencion():.2f} seg")
        print(f"Clientes por minuto: {self.get_clientes_por_minuto():.2f}")
        
        print("\n--- Estadísticas por Caja ---")
        for id_caja, stats in sorted(self.cajas_stats.items()):
            eficiencia = self.get_eficiencia_caja(id_caja)
            print(f"\nCaja {id_caja}:")
            print(f"  Clientes atendidos: {stats['clientes_atendidos']}")
            print(f"  Eficiencia: {eficiencia:.1f}%")
            print(f"  Tiempo inactivo: {stats['tiempo_inactivo']:.2f} seg")
        print("="*50 + "\n")
    
    def exportar_resumen(self, archivo="resumen_simulacion.txt"):
        """Exporta las estadísticas a un archivo de texto"""
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("RESUMEN DE SIMULACIÓN - SUPERMERCADO\n")
            f.write("="*50 + "\n\n")
            f.write(f"Clientes atendidos: {self.clientes_atendidos}\n")
            f.write(f"Tiempo promedio de espera: {self.get_tiempo_promedio_espera():.2f} seg\n")
            f.write(f"Tiempo promedio de atención: {self.get_tiempo_promedio_atencion():.2f} seg\n")
            f.write(f"Clientes por minuto: {self.get_clientes_por_minuto():.2f}\n\n")
            
            f.write("Estadísticas por Caja:\n")
            for id_caja, stats in sorted(self.cajas_stats.items()):
                f.write(f"\nCaja {id_caja}:\n")
                f.write(f"  Clientes: {stats['clientes_atendidos']}\n")
                f.write(f"  Eficiencia: {self.get_eficiencia_caja(id_caja):.1f}%\n")