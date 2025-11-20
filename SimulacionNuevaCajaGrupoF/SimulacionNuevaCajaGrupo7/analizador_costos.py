# analizador_costos.py
from dataclasses import dataclass
from typing import List, Dict
import statistics

@dataclass
class ConfiguracionCostos:
    c_caja: float
    c_espera: float
    c_SLA: float
    sla_tiempo_max: float
    sla_porcentaje_objetivo: float

@dataclass
class MetricasSimulacion:
    num_cajas: int
    tiempo_simulacion: float
    tiempos_en_sistema: List[float]
    longitudes_cola: List[float]
    utilizaciones: List[float]
    clientes_atendidos: int

class AnalizadorCostos:
    def __init__(self, config: ConfiguracionCostos):
        self.config = config

    def calcular_tiempo_promedio(self, metricas: MetricasSimulacion) -> float:
        if not metricas.tiempos_en_sistema:
            return 0.0
        return statistics.mean(metricas.tiempos_en_sistema)

    def calcular_porcentaje_sla(self, metricas: MetricasSimulacion) -> float:
        if not metricas.tiempos_en_sistema:
            # si no hay atendidos, y existieron llegadas, se considera 0% cumplidos
            return 0.0
        cumplen = sum(1 for t in metricas.tiempos_en_sistema if t <= self.config.sla_tiempo_max)
        # nota: en el experimento ya se contaron pendientes como incumplidos al calcular porcentaje global
        return (cumplen / len(metricas.tiempos_en_sistema)) * 100

    def calcular_costo_total(self, metricas: MetricasSimulacion) -> Dict[str, float]:
        costo_cajas = (self.config.c_caja * metricas.num_cajas * metricas.tiempo_simulacion)
        tiempo_total_espera = sum(metricas.tiempos_en_sistema)
        costo_espera = self.config.c_espera * tiempo_total_espera

        porcentaje_sla = self.calcular_porcentaje_sla(metricas)
        # incumplimiento relativo a objetivo: si porcentaje_sla ya está calculado solo para atendidos,
        # el experimento principal ajusta considerando pendientes. Aquí mantenemos la fórmula simple:
        incumplimiento = max(0, self.config.sla_porcentaje_objetivo * 100 - porcentaje_sla)
        costo_sla = self.config.c_SLA * incumplimiento

        costo_total = costo_cajas + costo_espera + costo_sla
        return {
            'costo_cajas': costo_cajas,
            'costo_espera': costo_espera,
            'costo_sla': costo_sla,
            'costo_total': costo_total,
            'porcentaje_sla': porcentaje_sla
        }

    def calcular_utilizacion_promedio(self, metricas: MetricasSimulacion) -> float:
        if not metricas.utilizaciones:
            return 0.0
        return statistics.mean(metricas.utilizaciones)

    def calcular_longitud_cola_promedio(self, metricas: MetricasSimulacion) -> float:
        if not metricas.longitudes_cola:
            return 0.0
        # en nuestra implementación, longitudes_cola es una lista con el Lq_promedio de la réplica
        return statistics.mean(metricas.longitudes_cola)
