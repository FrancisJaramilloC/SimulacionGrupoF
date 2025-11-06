import pygame
import sys
import time
from typing import List, Optional, Tuple

from .tuti import Tuti
from .modelos import Cliente, Caja, TipoCaja

# --- Colores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOX_COLOR = (60, 110, 170)
CLIENT_COLOR = (50, 180, 50)
NEW_CLIENT_COLOR = (220, 20, 60) # Color para el cliente recién llegado
SERVICE_COLOR = (200, 150, 50)

class PygameVisualizador:
    """Visualizador simplificado para la simulación de cajeros."""

    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Simulación de Cajeros")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    def draw_state(self, tuti: Tuti, clientes_atendidos: List[Optional[Cliente]], new_client_info: Optional[Tuple[int, int]] = None):
        """Dibuja el estado actual de todas las cajas y clientes."""
        self.screen.fill(WHITE)
        padding = 40
        caja_w = (self.width - padding * 2) / len(tuti.cajas)
        caja_h = 150
        cliente_radius = 15
        cliente_gap = 5

        for i, caja in enumerate(tuti.cajas):
            x = padding + i * caja_w
            y = 50
            
            rect = pygame.Rect(x, y, caja_w - 10, caja_h)
            pygame.draw.rect(self.screen, BOX_COLOR, rect, border_radius=8)
            
            tipo_str = "EXP" if caja.tipo == TipoCaja.EXPRESS else "N"
            caja_text = self.font.render(f"Caja {caja.numero} [{tipo_str}]", True, WHITE)
            self.screen.blit(caja_text, (x + 15, y + 15))

            cliente_en_servicio = clientes_atendidos[i]
            
            # 1. Dibuja al cliente en atención (si hay uno)
            if cliente_en_servicio:
                cx = x + 30
                cy = y + 70
                pygame.draw.circle(self.screen, SERVICE_COLOR, (cx, cy), cliente_radius)
                id_text = self.font.render(str(cliente_en_servicio.id), True, BLACK)
                self.screen.blit(id_text, (cx - id_text.get_width() / 2, cy - id_text.get_height() / 2))

                serving_text = pygame.font.SysFont(None, 20).render(f"Atendiendo: {cliente_en_servicio.num_articulos} art.", True, BLACK)
                self.screen.blit(serving_text, (x + 15, y + caja_h + 10))

            # 2. Dibuja la cola de espera, sin salirse del rectángulo
            start_queue_x = x + 30 + (cliente_radius * 2 + cliente_gap)
            max_visible = int((caja_w - 40 - (cliente_radius * 2 + cliente_gap)) / (cliente_radius * 2 + cliente_gap))
            
            clientes_en_cola = caja.clientes
            for j, cliente in enumerate(clientes_en_cola):
                if j >= max_visible:
                    # Si hay más clientes, dibuja un indicador "+N"
                    plus_text = self.font.render(f"+{len(clientes_en_cola) - j}", True, WHITE)
                    self.screen.blit(plus_text, (cx + 20, cy - plus_text.get_height() / 2))
                    break

                cx = start_queue_x + j * (cliente_radius * 2 + cliente_gap)
                cy = y + 70
                
                color = CLIENT_COLOR
                if new_client_info and new_client_info[0] == cliente.id and new_client_info[1] == i:
                    color = NEW_CLIENT_COLOR

                pygame.draw.circle(self.screen, color, (cx, cy), cliente_radius)
                id_text = self.font.render(str(cliente.id), True, WHITE)
                self.screen.blit(id_text, (cx - id_text.get_width() / 2, cy - id_text.get_height() / 2))

        pygame.display.flip()

    def run_simulation(self, tuti: Tuti):
        """Ejecuta el bucle principal de la simulación y visualización."""
        num_cajas = len(tuti.cajas)
        clientes_en_atencion = [None] * num_cajas
        tiempos_finalizacion = [0] * num_cajas
        
        # --- Lógica para un solo cliente nuevo ---
        un_cliente_generado = False
        tiempo_para_nuevo_cliente = time.time() + 5 # El cliente nuevo llegará en 5 segundos

        new_client_info = None
        new_client_timer = 0

        # Genera 5 clientes iniciales
        num_clientes_iniciales = 5
        print(f"--- Cargando {num_clientes_iniciales} clientes iniciales... ---")
        for _ in range(num_clientes_iniciales):
            cliente = tuti.generador.generar_cliente()
            caja = tuti.encontrar_mejor_caja(cliente.num_articulos) or tuti.cajas[0]
            caja.agregar_cliente(cliente)
        print("--- Simulación iniciada ---")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            current_time = time.time()

            # Gestionar la llegada del único cliente nuevo
            if not un_cliente_generado and current_time >= tiempo_para_nuevo_cliente:
                nuevo_cliente = tuti.generador.generar_cliente()
                mejor_caja = tuti.encontrar_mejor_caja(nuevo_cliente.num_articulos) or tuti.cajas[0]
                mejor_caja.agregar_cliente(nuevo_cliente)
                
                print("\n" + "="*40)
                print(f"¡Nuevo cliente #{nuevo_cliente.id} ha llegado con {nuevo_cliente.num_articulos} artículos!")
                print(f"Caja recomendada: Caja {mejor_caja.numero} (Tiempo estimado: {mejor_caja.calcular_tiempo_total():.1f}s)")
                print("="*40 + "\n")

                new_client_info = (nuevo_cliente.id, tuti.cajas.index(mejor_caja))
                new_client_timer = current_time + 1.5
                un_cliente_generado = True

            # Limpiar el resaltado del nuevo cliente después de un tiempo
            if new_client_info and current_time > new_client_timer:
                new_client_info = None

            # Revisa cada caja para procesar clientes
            for i in range(num_cajas):
                if clientes_en_atencion[i] and current_time >= tiempos_finalizacion[i]:
                    clientes_en_atencion[i] = None

                if not clientes_en_atencion[i] and tuti.cajas[i].clientes:
                    cliente_actual = tuti.cajas[i].atender_cliente()
                    clientes_en_atencion[i] = cliente_actual
                    
                    tiempo_servicio = (cliente_actual.num_articulos * tuti.cajas[i].tiempo_escaneo) + cliente_actual.tiempo_cobro
                    tiempos_finalizacion[i] = current_time + tiempo_servicio / 10

            self.draw_state(tuti, clientes_en_atencion, new_client_info)
            self.clock.tick(30)

            # Condición de parada: se generó el cliente y ya no hay nadie en el sistema
            if un_cliente_generado and not any(clientes_en_atencion) and not tuti.tiene_clientes_en_espera():
                running = False
        
        time.sleep(2)
        pygame.quit()
        sys.exit()

    def run_demo(self):
        """Prepara y ejecuta una demo de la simulación."""
        tuti = Tuti()
        tuti.agregar_caja(TipoCaja.NORMAL, 5, 3)
        tuti.agregar_caja(TipoCaja.NORMAL, 7, 2)
        tuti.agregar_caja(TipoCaja.EXPRESS, 4, 5)

        self.run_simulation(tuti)

if __name__ == "__main__":
    vis = PygameVisualizador()
    vis.run_demo()
