import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class VisualizadorResultados:
    """Genera gráficos para análisis de resultados"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def grafico_costo_vs_cajas(self, save_path: str = None):
        """Gráfico CT vs s"""
        fig, ax = plt.subplots()
        
        # Calcular promedios
        ct_promedio = self.df.groupby('num_cajas')['costo_total'].mean()
        ct_std = self.df.groupby('num_cajas')['costo_total'].std()
        
        ax.plot(ct_promedio.index, ct_promedio.values, 
                marker='o', linewidth=2, markersize=8, label='Costo Total Promedio')
        ax.fill_between(ct_promedio.index, 
                        ct_promedio - ct_std, 
                        ct_promedio + ct_std, 
                        alpha=0.3)
        
        ax.set_xlabel('Número de Cajas (s)', fontsize=12)
        ax.set_ylabel('Costo Total (USD)', fontsize=12)
        ax.set_title('Costo Total vs Número de Cajas', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def grafico_sla_vs_cajas(self, objetivo_sla: float = 80.0, save_path: str = None):
        """Gráfico %SLA vs s"""
        fig, ax = plt.subplots()
        
        sla_promedio = self.df.groupby('num_cajas')['porcentaje_sla'].mean()
        sla_std = self.df.groupby('num_cajas')['porcentaje_sla'].std()
        
        ax.plot(sla_promedio.index, sla_promedio.values, 
                marker='s', linewidth=2, markersize=8, 
                label='% Cumplimiento SLA', color='green')
        ax.fill_between(sla_promedio.index, 
                        sla_promedio - sla_std, 
                        sla_promedio + sla_std, 
                        alpha=0.3, color='green')
        
        # Línea objetivo
        ax.axhline(y=objetivo_sla, color='red', linestyle='--', 
                   linewidth=2, label=f'Objetivo SLA ({objetivo_sla}%)')
        
        ax.set_xlabel('Número de Cajas (s)', fontsize=12)
        ax.set_ylabel('Cumplimiento SLA (%)', fontsize=12)
        ax.set_title('Nivel de Servicio vs Número de Cajas', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def grafico_utilizacion_vs_cajas(self, save_path: str = None):
        """Gráfico ρ vs s"""
        fig, ax = plt.subplots()
        
        rho_promedio = self.df.groupby('num_cajas')['rho'].mean()
        rho_std = self.df.groupby('num_cajas')['rho'].std()
        
        ax.plot(rho_promedio.index, rho_promedio.values, 
                marker='^', linewidth=2, markersize=8, 
                label='Utilización Promedio (ρ)', color='orange')
        ax.fill_between(rho_promedio.index, 
                        rho_promedio - rho_std, 
                        rho_promedio + rho_std, 
                        alpha=0.3, color='orange')
        
        # Línea de estabilidad
        ax.axhline(y=1.0, color='red', linestyle='--', 
                   linewidth=2, label='Límite de Estabilidad (ρ=1)')
        ax.axhline(y=0.85, color='blue', linestyle=':', 
                   linewidth=2, label='Umbral Recomendado (ρ=0.85)')
        
        ax.set_xlabel('Número de Cajas (s)', fontsize=12)
        ax.set_ylabel('Utilización (ρ)', fontsize=12)
        ax.set_title('Utilización del Sistema vs Número de Cajas', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.1])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def grafico_descomposicion_costos(self, save_path: str = None):
        """Gráfico de barras apiladas con componentes de costo"""
        costos_promedio = self.df.groupby('num_cajas')[
            ['costo_cajas', 'costo_espera', 'costo_sla']
        ].mean()
        
        fig, ax = plt.subplots()
        costos_promedio.plot(kind='bar', stacked=True, ax=ax, 
                            color=['#3498db', '#e74c3c', '#f39c12'])
        
        ax.set_xlabel('Número de Cajas (s)', fontsize=12)
        ax.set_ylabel('Costo (USD)', fontsize=12)
        ax.set_title('Descomposición de Costos por Configuración', 
                    fontsize=14, fontweight='bold')
        ax.legend(['Costo Cajas', 'Costo Espera', 'Penalización SLA'])
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=0)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generar_todos_los_graficos(self, objetivo_sla: float = 80.0, directorio: str = "./"):
        """Genera todos los gráficos requeridos"""
        print("Generando gráficos...")
        
        self.grafico_costo_vs_cajas(save_path=f"{directorio}costo_vs_cajas.png")
        self.grafico_sla_vs_cajas(objetivo_sla, save_path=f"{directorio}sla_vs_cajas.png")
        self.grafico_utilizacion_vs_cajas(save_path=f"{directorio}utilizacion_vs_cajas.png")
        self.grafico_descomposicion_costos(save_path=f"{directorio}descomposicion_costos.png")
        
        print(f"Gráficos guardados en {directorio}")