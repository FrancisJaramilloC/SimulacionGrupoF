# experimentos.py

import heapq
import random
import statistics
from typing import List, Dict, Optional
from dataclasses import dataclass
import pandas as pd

from .tuti import Tuti
from .modelos import TipoCaja, Cliente
from .analizador_costos import ConfiguracionCostos, MetricasSimulacion, AnalizadorCostos

@dataclass
class ConfiguracionExperimento:
    num_replicas: int = 10
    tiempo_simulacion: float = 60.0  # minutos
    lambda_llegadas: float = 1.0  # clientes/minuto (Poisson)
    tiempo_escaneo: float = 0.05  # minutos/artículo
    rango_cajas: List[int] = None

    def __post_init__(self):
        if self.rango_cajas is None:
            self.rango_cajas = [1,2,3,4,5]

class ExperimentoSimulacion:
    """
    Simulación orientada a eventos:
    Eventos: (tiempo, tipo, datos)
      tipo 'arrive' -> datos: Cliente
      tipo 'depart' -> datos: (caja_index, cliente)
    """
    def __init__(self, config_experimento: ConfiguracionExperimento,
                 config_costos: ConfiguracionCostos):
        self.config_exp = config_experimento
        self.config_costos = config_costos
        self.analizador = AnalizadorCostos(config_costos)
        self.resultados = []

    # ---- motor de simulación por réplica ----
    def ejecutar_replica(self, num_cajas: int, semilla: int) -> MetricasSimulacion:
        random.seed(semilla)

        # crear tuti y cajas (express cada 3ra)
        tuti = Tuti()
        for i in range(num_cajas):
            tipo = TipoCaja.EXPRESS if (i % 3 == 0 and i > 0) else TipoCaja.NORMAL
            # Para express, reducimos tiempo_escaneo para que sea realmente express
            escaneo = self.config_exp.tiempo_escaneo * (0.6 if tipo == TipoCaja.EXPRESS else 1.0)
            tuti.agregar_caja(tipo, escaneo, num_clientes=0)

        sim_time = self.config_exp.tiempo_simulacion

        # estadísticas
        tiempos_en_sistema = []
        clientes_totales_llegados = 0
        clientes_atendidos = 0
        clientes_no_atendidos = 0

        # métricas de tiempo-promedio de cola (Lq) por método de área bajo curva
        last_event_time = 0.0
        area_cola = 0.0  # ∫ Lq(t) dt

        # utilización: busy time por caja (se acumula en caja.busy_time)
        for caja in tuti.cajas:
            caja.busy_time = 0.0
            caja.ultimo_inicio_ocupado = None

        # heap de eventos
        # generar primera llegada
        t_arrival = random.expovariate(self.config_exp.lambda_llegadas)
        events = []
        heapq.heappush(events, (t_arrival, 'arrive', None))

        # clientes pendientes en servicio: almacenamos (caja_index, cliente)
        # cuando programamos 'depart' sabemos cuándo termina
        while events:
            time, etype, data = heapq.heappop(events)
            if time > sim_time:
                # si evento fuera del horizonte, nos detenemos (pero contamos Lq hasta sim_time)
                # actualizar area hasta sim_time y romper
                area_cola += self._cola_total(tuti) * (sim_time - last_event_time)
                last_event_time = sim_time
                break

            # actualizar área Lq entre last_event_time y time
            area_cola += self._cola_total(tuti) * (time - last_event_time)
            last_event_time = time

            if etype == 'arrive':
                # llegada de nuevo cliente
                clientes_totales_llegados += 1
                # crear cliente
                cliente = tuti.generador.generar_cliente(max_articulos=20)
                cliente.tiempo_llegada = time

                # elegir mejor caja que permita ese número de artículos
                mejor = tuti.encontrar_mejor_caja(cliente.num_articulos)
                if mejor is None:
                    # no hay caja que pueda aceptar (raro si express limita), consideramos que cliente abandona
                    clientes_no_atendidos += 1
                else:
                    # si caja está vacía (sin cola), inicia servicio inmediatamente
                    if len(mejor.clientes) == 0:
                        # inicia servicio ahora
                        mejor.agregar_cliente(cliente)
                        cliente.tiempo_inicio_servicio = time
                        servicio = mejor.calcular_tiempo_servicio_cliente(cliente)
                        cliente.tiempo_fin_servicio = time + servicio
                        # marcar inicio ocupado
                        mejor.ultimo_inicio_ocupado = time
                        # programar salida
                        heapq.heappush(events, (cliente.tiempo_fin_servicio, 'depart', (mejor, cliente)))
                    else:
                        # agrega a la cola
                        mejor.agregar_cliente(cliente)

                # programar próxima llegada
                t_next = time + random.expovariate(self.config_exp.lambda_llegadas)
                heapq.heappush(events, (t_next, 'arrive', None))

            elif etype == 'depart':
                caja_obj, cliente = data
                # si el cliente no está en la cola del todo (puede porque pop en atender), procesamos
                # retirar cliente de la cabeza si todavía está (debe estarlo)
                # marcamos fin servicio (ya fijado)
                # actualizar métricas
                cliente.tiempo_fin_servicio = time
                tiempo_en_sistema = cliente.tiempo_fin_servicio - cliente.tiempo_llegada
                tiempos_en_sistema.append(tiempo_en_sistema)
                clientes_atendidos += 1

                # actualizar busy_time de la caja
                if caja_obj.ultimo_inicio_ocupado is not None:
                    caja_obj.busy_time += (time - caja_obj.ultimo_inicio_ocupado)
                    caja_obj.ultimo_inicio_ocupado = None

                # remover el cliente atendido (debe ser el primero)
                # lo buscamos en la fila y lo sacamos si sigue ahí
                if caja_obj.clientes and caja_obj.clientes[0] is cliente:
                    caja_obj.pop_cliente()
                else:
                    # si no es el primero, intentamos quitar por identidad
                    try:
                        caja_obj.clientes.remove(cliente)
                    except ValueError:
                        pass

                # si aun hay cola en la caja, iniciar servicio del siguiente
                if caja_obj.clientes:
                    siguiente = caja_obj.clientes[0]
                    siguiente.tiempo_inicio_servicio = time
                    servicio = caja_obj.calcular_tiempo_servicio_cliente(siguiente)
                    siguiente.tiempo_fin_servicio = time + servicio
                    caja_obj.ultimo_inicio_ocupado = time
                    heapq.heappush(events, (siguiente.tiempo_fin_servicio, 'depart', (caja_obj, siguiente)))

        # fin de eventos / horizonte de simulación
        # clientes que no fueron atendidos (quedan en colas) se consideran no cumplidores de SLA
        pendientes = 0
        for caja in tuti.cajas:
            pendientes += len(caja.clientes)
            # si la caja está ocupada al final, contabilizamos busy_time hasta sim_time
            if caja.ultimo_inicio_ocupado is not None:
                caja.busy_time += max(0.0, sim_time - caja.ultimo_inicio_ocupado)
                caja.ultimo_inicio_ocupado = None

        clientes_no_atendidos += pendientes

        # Lq promedio (tiempo-promedio de clientes esperando)
        Lq_promedio = area_cola / sim_time if sim_time > 0 else 0.0

        # utilizaciones por caja
        utilizaciones = []
        for caja in tuti.cajas:
            rho = min(1.0, caja.busy_time / sim_time) if sim_time > 0 else 0.0
            utilizaciones.append(rho)

        # SLA: porcentaje de clientes atendidos que cumplieron SLA
        # Consideramos como incumplidos todos los no atendidos (pendientes/abandonos)
        total_clientes_considerados = clientes_atendidos + clientes_no_atendidos
        if total_clientes_considerados == 0:
            porcentaje_sla = 100.0
        else:
            cumplen = sum(1 for t in tiempos_en_sistema if t <= self.config_costos.sla_tiempo_max)
            # los pendientes no cumplen, así que cumplen/total
            porcentaje_sla = (cumplen / total_clientes_considerados) * 100

        return MetricasSimulacion(
            num_cajas=num_cajas,
            tiempo_simulacion=sim_time,
            tiempos_en_sistema=tiempos_en_sistema,
            longitudes_cola=[Lq_promedio],  # guardamos promedio por réplica
            utilizaciones=utilizaciones,
            clientes_atendidos=clientes_atendidos
        )

    def _cola_total(self, tuti: Tuti) -> int:
        """Devuelve número total de clientes esperando (excluye ninguno en servicio, porque en nuestro modelo
        el cliente en servicio está en la lista, por simplicidad restamos 1 por caja si existe)."""
        total = 0
        for c in tuti.cajas:
            total += max(0, len(c.clientes) - 1)
        return total

    def ejecutar_experimento_completo(self) -> pd.DataFrame:
        print("Iniciando experimento...")
        print(f"Configuraciones: {len(self.config_exp.rango_cajas)}")
        print(f"Réplicas por configuración: {self.config_exp.num_replicas}\n")

        for num_cajas in self.config_exp.rango_cajas:
            print(f"Ejecutando configuración con {num_cajas} caja(s)...")
            resultados_replicas = []
            for replica in range(self.config_exp.num_replicas):
                semilla = num_cajas * 1000 + replica
                metricas = self.ejecutar_replica(num_cajas, semilla)
                costos = self.analizador.calcular_costo_total(metricas)

                resultado = {
                    'num_cajas': num_cajas,
                    'replica': replica + 1,
                    'E[T]': self.analizador.calcular_tiempo_promedio(metricas),
                    'Lq': self.analizador.calcular_longitud_cola_promedio(metricas),
                    'rho': self.analizador.calcular_utilizacion_promedio(metricas),
                    'porcentaje_sla': costos['porcentaje_sla'],
                    'costo_cajas': costos['costo_cajas'],
                    'costo_espera': costos['costo_espera'],
                    'costo_sla': costos['costo_sla'],
                    'costo_total': costos['costo_total'],
                    'clientes_atendidos': metricas.clientes_atendidos
                }
                resultados_replicas.append(resultado)

            self.resultados.extend(resultados_replicas)
            ct_promedio = statistics.mean([r['costo_total'] for r in resultados_replicas])
            print(f"  Costo Total Promedio: ${ct_promedio:.2f}")

        print("\nExperimento completado!\n")
        return pd.DataFrame(self.resultados)

    def generar_resumen(self, df: pd.DataFrame) -> pd.DataFrame:
        resumen = df.groupby('num_cajas').agg({
            'E[T]': ['mean', 'std'],
            'Lq': ['mean', 'std'],
            'rho': ['mean', 'std'],
            'porcentaje_sla': ['mean', 'std'],
            'costo_total': ['mean', 'std']
        }).round(4)
        return resumen
