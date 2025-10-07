import pygame
import random
import time
import math
import cv2
import numpy as np
from typing import Dict, List, Tuple
import json

class AerialVideoSimulatorPygame:
    def __init__(self, width: int = 640, height: int = 480,
                 num_obstacles: int = None, num_victims: int = None):
        self.width = width
        self.height = height
        self.frame_count = 0
        
        # Configuración personalizable
        self.num_obstacles = num_obstacles if num_obstacles is not None else random.randint(8, 15)
        self.num_victims = num_victims if num_victims is not None else random.randint(5, 12)
        
        # Configuración de grabación
        self.video_writer = None
        self.output_path = "uav_simulation.mp4"
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("UAV - Vista Aérea Post-Desastre")
        self.clock = pygame.time.Clock()
        
        # Configurar grabación de video
        self._setup_video_recording()
        
        # Colores mejorados para mejor contraste
        self.colors = {
            'terrain': (128, 128, 128),        # Gris (fondo)
            'grid': (160, 160, 160),           # Gris más claro para grid
            'victim_critical': (255, 0, 0),    # Rojo
            'victim_injured': (255, 165, 0),   # Naranja
            'victim_trapped': (128, 0, 128),   # Púrpura
            'victim_safe': (0, 100, 0),        # Verde
            'building': (139, 69, 19),         # Marrón
            'debris': (255, 20, 147),          # Rosa/Magenta (triángulos más distintivos)
            'vehicle': (255, 255, 0),          # Amarillo (vehículos)
            'tree': (0, 100, 200),             # Azul (hexágonos)
            'text': (255, 255, 255),           # Blanco
            'black': (0, 0, 0)                 # Negro
        }
        
        # Fuentes
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # Inicializar zona de desastre
        self.zone_data = self._initialize_disaster_zone()
        self.running = True
        
    def _setup_video_recording(self):
        """Configura la grabación de video"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.output_path, 
            fourcc, 
            30.0, 
            (self.width, self.height)
        )
        print(f"🎥 Grabación de video iniciada: {self.output_path}")
    
    def _initialize_disaster_zone(self) -> Dict:
        """Inicializa la zona de desastre con obstáculos y víctimas"""
        zone = {
            "obstacles": [],
            "victims": [],
            "damage_level": random.choice(["low", "medium", "high"])
        }
        
        print(f"🚧 Generando {self.num_obstacles} obstáculos...")
        
        # Generar obstáculos con mejor distribución
        for i in range(self.num_obstacles):
            obstacle = self._generate_obstacle(zone["obstacles"])
            zone["obstacles"].append(obstacle)
        
        print(f"👥 Generando {self.num_victims} víctimas...")
        
        # Generar víctimas
        for i in range(self.num_victims):
            victim = self._generate_victim(zone["obstacles"], zone["victims"])
            zone["victims"].append(victim)
        
        print(f"✅ Zona de desastre inicializada:")
        print(f"   - Obstáculos: {len(zone['obstacles'])}")
        print(f"   - Víctimas: {len(zone['victims'])}")
        print(f"   - Nivel de daño: {zone['damage_level']}")
        
        return zone
    
    def _generate_obstacle(self, existing_obstacles: List) -> Dict:
        """Genera un obstáculo que no se superponga con otros"""
        max_attempts = 50
        min_distance = 80  # Distancia mínima entre obstáculos
        
        for attempt in range(max_attempts):
            # Posición aleatoria
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            
            # Tamaño variable
            width = random.randint(30, 80)
            height = random.randint(30, 80)
            
            # Verificar colisiones con obstáculos existentes
            collision = False
            for existing in existing_obstacles:
                distance = math.sqrt((x - existing["x"])**2 + (y - existing["y"])**2)
                if distance < min_distance:
                    collision = True
                    break
            
            if not collision:
                obstacle_types = ["building", "debris", "vehicle", "tree"]
                obstacle_type = random.choice(obstacle_types)
                
                return {
                    "id": len(existing_obstacles) + 1,
                    "type": obstacle_type,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "damage_level": random.choice(["intact", "damaged", "destroyed"])
                }
        
        # Si no se puede evitar colisión, generar en posición aleatoria
        x = random.randint(50, self.width - 50)
        y = random.randint(50, self.height - 50)
        width = random.randint(30, 60)
        height = random.randint(30, 60)
        
        return {
            "id": len(existing_obstacles) + 1,
            "type": random.choice(["building", "debris", "vehicle", "tree"]),
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "damage_level": random.choice(["intact", "damaged", "destroyed"])
        }
    
    def _generate_victim(self, obstacles: List, existing_victims: List) -> Dict:
        """Genera una víctima que no se superponga con obstáculos ni otras víctimas"""
        max_attempts = 50
        victim_radius = 15  # Radio de la víctima
        
        for attempt in range(max_attempts):
            # Posición aleatoria
            x = random.randint(20, self.width - 20)
            y = random.randint(20, self.height - 20)
            
            # Verificar colisiones con obstáculos
            collision = False
            for obstacle in obstacles:
                distance = math.sqrt((x - obstacle["x"])**2 + (y - obstacle["y"])**2)
                if distance < 50:  # Distancia mínima de obstáculos
                    collision = True
                    break
            
            # Verificar colisiones con otras víctimas
            if not collision:
                for victim in existing_victims:
                    distance = math.sqrt((x - victim["x"])**2 + (y - victim["y"])**2)
                    if distance < 40:  # Distancia mínima entre víctimas
                        collision = True
                        break
            
            if not collision:
                victim_states = ["critical", "injured", "trapped", "safe"]
                state = random.choice(victim_states)
                
                return {
                    "id": len(existing_victims) + 1,
                    "x": x,
                    "y": y,
                    "state": state,
                    "priority": self._get_priority(state),
                    "radius": victim_radius
                }
        
        # Si no se puede evitar colisión, generar en posición aleatoria
        x = random.randint(20, self.width - 20)
        y = random.randint(20, self.height - 20)
        
        return {
            "id": len(existing_victims) + 1,
            "x": x,
            "y": y,
            "state": random.choice(["critical", "injured", "trapped", "safe"]),
            "priority": random.choice(["critical", "high", "medium", "low"]),
            "radius": victim_radius
        }
    
    def _get_priority(self, state: str) -> str:
        """Obtiene la prioridad basada en el estado de la víctima"""
        priority_map = {
            "critical": "critical",
            "injured": "high",
            "trapped": "high",
            "safe": "low"
        }
        return priority_map.get(state, "medium")
    
    def _draw_terrain(self):
        """Dibuja el terreno de fondo"""
        # Fondo gris
        self.screen.fill(self.colors['terrain'])
        
        # Grid sutil
        grid_size = 50
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.screen, self.colors['grid'], (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_size):
            pygame.draw.line(self.screen, self.colors['grid'], (0, y), (self.width, y), 1)
    
    def _draw_obstacles(self):
        """Dibuja los obstáculos con formas diferentes y contornos negros"""
        for obstacle in self.zone_data["obstacles"]:
            x, y = obstacle["x"], obstacle["y"]
            width, height = obstacle["width"], obstacle["height"]
            
            # Color basado en el tipo
            color = self.colors.get(obstacle["type"], self.colors['debris'])
            
            # Dibujar según el tipo con contorno negro
            if obstacle["type"] == "building":
                # Rectángulo con contorno
                pygame.draw.rect(self.screen, color, (x - width//2, y - height//2, width, height))
                pygame.draw.rect(self.screen, self.colors['black'], (x - width//2, y - height//2, width, height), 2)
            elif obstacle["type"] == "debris":
                # Triángulo con contorno
                points = [
                    (x, y - height//2),
                    (x - width//2, y + height//2),
                    (x + width//2, y + height//2)
                ]
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, self.colors['black'], points, 2)
            elif obstacle["type"] == "vehicle":
                # Rectángulo más pequeño con contorno (ahora amarillo)
                pygame.draw.rect(self.screen, color, (x - width//3, y - height//3, width*2//3, height*2//3))
                pygame.draw.rect(self.screen, self.colors['black'], (x - width//3, y - height//3, width*2//3, height*2//3), 2)
            elif obstacle["type"] == "tree":
                # Hexágono con contorno
                self._draw_hexagon(x, y, min(width, height)//2, color)
    
    def _draw_hexagon(self, center_x: int, center_y: int, radius: int, color: Tuple):
        """Dibuja un hexágono con contorno negro"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, self.colors['black'], points, 2)
    
    def _draw_victims(self):
        """Dibuja las víctimas como círculos de colores SIN cruces"""
        for victim in self.zone_data["victims"]:
            x, y = victim["x"], victim["y"]
            radius = victim["radius"]
            
            # Color basado en el estado
            if victim["state"] == "critical":
                color = self.colors['victim_critical']
            elif victim["state"] == "injured":
                color = self.colors['victim_injured']
            elif victim["state"] == "trapped":
                color = self.colors['victim_trapped']
            else:  # safe
                color = self.colors['victim_safe']
            
            # Dibujar círculo simple (SIN cruces)
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, self.colors['black'], (x, y), radius, 2)
    
    def _update_victims(self):
        """Actualiza la posición de las víctimas (movimiento sutil)"""
        for victim in self.zone_data["victims"]:
            # Movimiento aleatorio sutil
            if random.random() < 0.1:  # 10% de probabilidad de moverse
                victim["x"] += random.randint(-2, 2)
                victim["y"] += random.randint(-2, 2)
                
                # Mantener dentro de los límites
                victim["x"] = max(20, min(self.width - 20, victim["x"]))
                victim["y"] = max(20, min(self.height - 20, victim["y"]))
    
    def _get_frame_data(self) -> Dict:
        """Obtiene los datos del frame actual para procesamiento"""
        frame_data = {
            "frame_number": self.frame_count,
            "timestamp": time.time(),
            "gps_coordinates": {
                "latitude": 40.7128 + random.uniform(-0.01, 0.01),
                "longitude": -74.0060 + random.uniform(-0.01, 0.01),
                "altitude": 100 + random.uniform(-10, 10)
            },
            "detections": {
                "obstacles": len(self.zone_data["obstacles"]),
                "victims": len(self.zone_data["victims"]),
                "victims_by_state": {
                    "critical": len([v for v in self.zone_data["victims"] if v["state"] == "critical"]),
                    "injured": len([v for v in self.zone_data["victims"] if v["state"] == "injured"]),
                    "trapped": len([v for v in self.zone_data["victims"] if v["state"] == "trapped"]),
                    "safe": len([v for v in self.zone_data["victims"] if v["state"] == "safe"])
                }
            },
            "zone_info": {
                "damage_level": self.zone_data["damage_level"],
                "total_obstacles": len(self.zone_data["obstacles"]),
                "total_victims": len(self.zone_data["victims"])
            }
        }
        return frame_data
    
    def _convert_frame_for_video(self):
        """Convierte el frame de Pygame a formato OpenCV para el video"""
        # Convertir superficie de Pygame a imagen
        frame_data = pygame.surfarray.array3d(self.screen)
        frame_data = frame_data.swapaxes(0, 1)  # Corregir orientación
        
        # Convertir a formato OpenCV
        frame_bgr = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)
        
        return frame_bgr
    
    def run_simulation(self, duration_seconds: int = 60):
        """Ejecuta la simulación por el tiempo especificado"""
        start_time = time.time()
        
        print(f"⏱️  Duración: {duration_seconds} segundos")
        
        while self.running and (time.time() - start_time) < duration_seconds:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Actualizar simulación
            self._update_victims()
            
            # Dibujar
            self._draw_terrain()
            self._draw_obstacles()
            self._draw_victims()
            
            # Convertir frame para video (sin guardar imagen individual)
            frame_bgr = self._convert_frame_for_video()
            
            # Escribir frame al video
            if self.video_writer:
                self.video_writer.write(frame_bgr)
            
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
            self.frame_count += 1
        
        # Finalizar grabación
        if self.video_writer:
            self.video_writer.release()
            print(f"✅ Video guardado como: {self.output_path}")
        
        pygame.quit()

def main():
    print("🚁 Iniciando simulación de video aéreo con Pygame...")
    print("🚁 Configuración de Simulación UAV")
    print("=" * 40)
    
    # Configuración interactiva
    try:
        obstacles_input = input("Número de obstáculos (Enter para aleatorio 8-15): ").strip()
        num_obstacles = int(obstacles_input) if obstacles_input else None
    except ValueError:
        num_obstacles = None
    
    try:
        victims_input = input("Número de víctimas (Enter para aleatorio 5-12): ").strip()
        num_victims = int(victims_input) if victims_input else None
    except ValueError:
        num_victims = None
    
    try:
        duration_input = input("Duración en segundos (Enter para 60): ").strip()
        duration = int(duration_input) if duration_input else 60
    except ValueError:
        duration = 60
    
    print("🎮 Controles:")
    print("- ESC: Salir")
    print("- Cerrar ventana: Salir")
    
    # Crear y ejecutar simulación
    simulator = AerialVideoSimulatorPygame(
        width=640, 
        height=480,
        num_obstacles=num_obstacles,
        num_victims=num_victims
    )
    
    simulator.run_simulation(duration)

if __name__ == "__main__":
    main()