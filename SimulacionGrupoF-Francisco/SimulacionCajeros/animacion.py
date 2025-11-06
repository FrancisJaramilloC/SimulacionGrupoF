import pygame
import time
from SimulacionCajeros.simulador import Simulador
from SimulacionCajeros.modelos import TipoCaja

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
CAJA_COLOR = (70, 130, 180)
EXPRESS_COLOR = (50, 205, 50)
CLIENTE_COLOR = (255, 215, 0)
CAJA_WIDTH, CAJA_HEIGHT = 150, 50
CLIENTE_RADIUS = 10
MARGEN_Y = 50

class Animacion:
    def __init__(self, tuti, velocidad=0.5):
        self.tuti = tuti
        self.velocidad = velocidad
        self.simulador = Simulador(tuti, None)  # No necesitamos visualizador aquí
        pygame.init()
        self.pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simulación Supermercado")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    def dibujar(self):
        self.pantalla.fill(BG_COLOR)
        num_cajas = len(self.tuti.cajas)
        # Calcular espacio vertical dinámico
        if num_cajas > 1:
            ESPACIO_Y = max(100, (HEIGHT - 2*MARGEN_Y - CAJA_HEIGHT) // (num_cajas - 1))
        else:
            ESPACIO_Y = 100

        for i, caja in enumerate(self.tuti.cajas):
            x = 100
            y = MARGEN_Y + i * ESPACIO_Y
            color = EXPRESS_COLOR if caja.tipo == TipoCaja.EXPRESS else CAJA_COLOR
            pygame.draw.rect(self.pantalla, color, (x, y, CAJA_WIDTH, CAJA_HEIGHT))

            # Etiqueta de la caja
            tipo_texto = f"{caja.tipo.value} #{caja.numero}"
            etiqueta = self.font.render(tipo_texto, True, (255, 255, 255))
            self.pantalla.blit(etiqueta, (x + 10, y + 10))

            # Dibujar clientes
            for j, cliente in enumerate(caja.clientes):
                cx = x + 30 + j*25
                cy = y + CAJA_HEIGHT + 20
                pygame.draw.circle(self.pantalla, CLIENTE_COLOR, (cx, cy), CLIENTE_RADIUS)

        pygame.display.flip()

    def ejecutar(self):
        running = True
        while running and self.simulador.tuti.tiene_clientes_en_espera():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Atender un cliente por caja
            self.simulador.tuti.atender_todos()

            self.dibujar()
            self.clock.tick(30)
            time.sleep(self.velocidad)

        pygame.quit()
