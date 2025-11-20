# main.py
"""
TALLER 4 - ¿CUÁNDO ABRIR UNA NUEVA CAJA?
Modo teclado + ejemplo predeterminado
Con validaciones estrictas
"""

from .analizador_costos import ConfiguracionCostos
from .experimentos import ConfiguracionExperimento, ExperimentoSimulacion
from .visualizador_resultados import VisualizadorResultados
import pandas as pd

def leer_float(msg, defecto, min_val=None, max_val=None):
    while True:
        txt = input(f"{msg} [{defecto}]: ").strip()
        if txt == "":
            valor = defecto
        else:
            try:
                valor = float(txt)
            except ValueError:
                print("❌ Error: Debe ingresar un número válido.")
                continue
        if min_val is not None and valor < min_val:
            print(f"❌ El valor mínimo permitido es {min_val}")
            continue
        if max_val is not None and valor > max_val:
            print(f"❌ El valor máximo permitido es {max_val}")
            continue
        return valor

def leer_int(msg, defecto, min_val=None, max_val=None):
    while True:
        txt = input(f"{msg} [{defecto}]: ").strip()
        if txt == "":
            valor = defecto
        else:
            try:
                valor = int(txt)
            except ValueError:
                print("❌ Error: Debe ingresar un entero válido.")
                continue
        if min_val is not None and valor < min_val:
            print(f"❌ El valor mínimo permitido es {min_val}")
            continue
        if max_val is not None and valor > max_val:
            print(f"❌ El valor máximo permitido es {max_val}")
            continue
        return valor

def leer_rango(msg, defecto):
    while True:
        txt = input(f"{msg} [{defecto[0]}-{defecto[-1]}]: ").strip()
        if txt == "":
            return defecto
        try:
            inicio, fin = map(int, txt.split("-"))
        except:
            print("❌ Formato inválido. Debe ser por ejemplo 1-5")
            continue
        if inicio <= 0 or fin <= 0 or inicio >= fin:
            print("❌ Rangos inválidos.")
            continue
        return list(range(inicio, fin+1))

def seleccionar_modo():
    print("="*80)
    print(" MODOS DE EJECUCIÓN ".center(80))
    print("="*80)
    print("1) Ingresar parámetros por TECLADO")
    print("2) Usar EJEMPLO PREDETERMINADO")
    print()
    while True:
        op = input("Seleccione modo (1 o 2): ").strip()
        if op in ["1","2"]:
            return op
        print("❌ Opción inválida. Intente nuevamente.")

def main():
    modo = seleccionar_modo()
    if modo == "1":
        print("\n✔ MODO: ingreso por teclado")
        c_caja = leer_float("Costo por caja activa (USD/min)", 0.50, 0.1, 2.0)
        c_espera = leer_float("Costo por cliente esperando (USD/min)", 0.10, 0.01, 1.0)
        c_SLA = leer_float("Penalización SLA (USD por punto %)", 5.0, 0.5, 50.0)
        sla_tiempo_max = leer_float("Tiempo máximo del SLA (min)", 8.0, 1, 20)
        sla_obj = leer_float("SLA objetivo (%)", 80.0, 50, 99) / 100.0

        num_replicas = leer_int("Número de réplicas (mínimo 10)", 10, 10, 100)
        tiempo_sim = leer_float("Tiempo de simulación (min)", 60.0, 10, 600)
        tasa_lambda = leer_float("Tasa de llegadas λ (clientes/min)", 2.0, 0.1, 10)
        tiempo_escaneo = leer_float("Tiempo por artículo (min)", 0.05, 0.01, 0.2)
        rango_cajas = leer_rango("Rango de cajas (ej:1-5)", [1,2,3,4,5])
    else:
        print("\n✔ MODO: ejemplo predefinido")
        c_caja = 0.50
        c_espera = 0.10
        c_SLA = 5.0
        sla_tiempo_max = 8.0
        sla_obj = 0.80
        num_replicas = 10
        tiempo_sim = 60.0
        tasa_lambda = 2.0
        tiempo_escaneo = 0.05
        rango_cajas = [1,2,3,4,5]

    config_costos = ConfiguracionCostos(
        c_caja=c_caja, c_espera=c_espera, c_SLA=c_SLA,
        sla_tiempo_max=sla_tiempo_max, sla_porcentaje_objetivo=sla_obj
    )

    config_exp = ConfiguracionExperimento(
        num_replicas=num_replicas, tiempo_simulacion=tiempo_sim,
        lambda_llegadas=tasa_lambda, tiempo_escaneo=tiempo_escaneo,
        rango_cajas=rango_cajas
    )

    print("\n🔬 Ejecutando experimento...")
    experimento = ExperimentoSimulacion(config_exp, config_costos)
    df_resultados = experimento.ejecutar_experimento_completo()

    print("\n📊 Resumen estadístico")
    resumen = experimento.generar_resumen(df_resultados)
    print(resumen)

    costos_prom = df_resultados.groupby("num_cajas")["costo_total"].mean()
    optimo = costos_prom.idxmin()
    sla_opt = df_resultados[df_resultados["num_cajas"] == optimo]["porcentaje_sla"].mean()
    rho_opt = df_resultados[df_resultados["num_cajas"] == optimo]["rho"].mean()

    print(f"\n💡 Configuración óptima: {optimo} cajas")
    print(f"   Costo Total Promedio: ${costos_prom.min():.2f}")
    print(f"   SLA Promedio: {sla_opt:.1f}%")
    print(f"   Utilización ρ: {rho_opt:.3f}")

    Lq_opt = df_resultados[df_resultados["num_cajas"] == optimo]["Lq"].mean()
    print("\n📐 Regla de apertura propuesta")
    print(f"Abrir nueva caja cuando Lq > {Lq_opt:.1f} o ρ > 0.85 durante 5 minutos\n")

    print("📈 Generando gráficos...")
    visualizador = VisualizadorResultados(df_resultados)
    visualizador.generar_todos_los_graficos(objetivo_sla=config_costos.sla_porcentaje_objetivo * 100, directorio="./")

    df_resultados.to_csv("matriz_corridas.csv", index=False)
    resumen.to_csv("resumen_estadistico.csv")
    print("\n✓ Archivos generados: matriz_corridas.csv, resumen_estadistico.csv")

if __name__ == "__main__":
    main()
