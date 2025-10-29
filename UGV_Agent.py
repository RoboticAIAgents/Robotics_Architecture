import os
import json
import time
import socket
import threading
import math
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# Configurar LLM
llm = ChatOpenAI(model="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"))

class UGVState(dict):
    mission_received: bool
    mission_data: dict
    current_position: tuple
    target_victims: list
    obstacles_avoided: list
    mission_status: str
    communication_log: list
    message_file: str  # Archivo del mensaje del UAV
    # Nuevos campos para el controlador de movimiento
    target_point: tuple  # Punto objetivo actual
    route_index: int  # Índice del punto actual en la ruta
    arrival_confirmed: bool  # Confirmación de llegada al punto
    movement_speed: float  # Velocidad de movimiento (píxeles por comando)
    # Campos de atención de víctimas
    current_victim_info: dict  # Información de la víctima actual
    attention_in_progress: bool  # Indica si hay atención en curso
    attention_complete: bool  # Indica si la atención fue completada
    victims_rescued: list  # Lista de víctimas rescatadas

def receptorMensaje(state: UGVState) -> UGVState:
    """Lee el mensaje del UAV desde el archivo uav_to_ugv_message.json"""
    print("📡 UGV: Leyendo mensaje del UAV...")
    
    if not state.get("mission_received", False):
        message_file = "uav_to_ugv_message.json"
        
        try:
            # Verificar si el archivo existe
            if os.path.exists(message_file):
                print(f"📄 UGV: Archivo encontrado: {message_file}")
                
                # Leer el archivo JSON
                with open(message_file, "r", encoding="utf-8") as f:
                    message_data = json.load(f)
                
                # Verificar que el mensaje es del UAV
                if message_data.get("from") == "UAV" and message_data.get("to") == "UGV":
                    print(f"✅ UGV: Mensaje del UAV recibido")
                    print(f"📋 UGV: Tipo de mensaje: {message_data.get('message_type', 'N/A')}")
                    print(f"🆔 UGV: ID del mensaje: {message_data.get('message_id', 'N/A')}")
                    
                    # Procesar el mission brief
                    mission_brief = message_data.get("mission_brief", "")
                    if mission_brief:
                        print(f"📋 UGV: Mission brief recibido ({len(mission_brief)} caracteres)")
                        
                        # Extraer información del mission brief
                        mission_data = _parse_simplified_mission_brief(mission_brief)
                        
                        state["mission_received"] = True
                        state["mission_data"] = mission_data
                        state["target_victims"] = mission_data.get("victims", [])
                        state["mission_status"] = "MISSION_RECEIVED"
                        state["message_file"] = message_file
                        
                        print(f"👥 UGV: {len(mission_data.get('victims', []))} víctimas identificadas")
                        print(f"🚧 UGV: {len(mission_data.get('obstacles', []))} obstáculos identificados")
                        print(f"🗺️ UGV: Ruta optimizada disponible")
                        
                        # Log de comunicación
                        state["communication_log"] = state.get("communication_log", [])
                        state["communication_log"].append({
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "type": "MESSAGE_RECEIVED",
                            "from": "UAV",
                            "file": message_file,
                            "status": "SUCCESS"
                        })
                    else:
                        print(f"⚠️ UGV: Mission brief vacío")
                else:
                    print(f"⚠️ UGV: Mensaje no es del UAV o formato incorrecto")
            else:
                print(f"⏳ UGV: Archivo {message_file} no encontrado, esperando...")
                
        except Exception as e:
            print(f"❌ UGV: Error al leer mensaje: {e}")
            
            # Log de error
            state["communication_log"] = state.get("communication_log", [])
            state["communication_log"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "MESSAGE_RECEIVED",
                "from": "UAV",
                "file": message_file,
                "status": "ERROR",
                "error": str(e)
            })
    
    return state

def _parse_simplified_mission_brief(mission_brief):
    """Parsea el mission brief simplificado para extraer información estructurada"""
    print("🔍 UGV: Parseando mission brief simplificado...")
    
    # Crear estructura de datos básica
    mission_data = {
        "mission_id": "UNKNOWN",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "victims": [],
        "obstacles": [],
        "route": {},
        "zone_info": {}
    }
    
    try:
        # Dividir el texto en líneas
        lines = mission_brief.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Extraer ID de misión
            if "ID:" in line:
                mission_data["mission_id"] = line.split("ID:")[1].strip()
            
            # Extraer información de la zona
            elif "Map Resolution:" in line:
                mission_data["zone_info"]["resolution"] = line.split("Map Resolution:")[1].strip()
            elif "Victims:" in line:
                mission_data["zone_info"]["victims_count"] = line.split("Victims:")[1].strip()
            elif "Obstacles:" in line:
                mission_data["zone_info"]["obstacles_count"] = line.split("Obstacles:")[1].strip()
            
            # Extraer víctimas
            elif "Victim" in line and "Position=" in line:
                victim_data = _extract_simplified_victim_data(line)
                if victim_data:
                    mission_data["victims"].append(victim_data)
            
            # Extraer obstáculos
            elif "Obstacle" in line and "Position=" in line:
                obstacle_data = _extract_simplified_obstacle_data(line)
                if obstacle_data:
                    mission_data["obstacles"].append(obstacle_data)
            
            # Extraer información de ruta
            elif "Distance:" in line:
                mission_data["route"]["distance"] = line.split("Distance:")[1].strip()
            elif "Time:" in line:
                mission_data["route"]["time"] = line.split("Time:")[1].strip()
            elif "Victims to visit:" in line:
                mission_data["route"]["victims_to_visit"] = line.split("Victims to visit:")[1].strip()
            elif "Visit order:" in line:
                order_str = line.split("Visit order:")[1].strip()
                # Convertir string de lista a lista real
                try:
                    order_str = order_str.replace("[", "").replace("]", "")
                    order_list = [int(x.strip()) for x in order_str.split(",")]
                    mission_data["route"]["visit_order"] = order_list
                except:
                    mission_data["route"]["visit_order"] = []
            
            # Extraer puntos de ruta
            elif "Puntos de ruta:" in line:
                # Buscar puntos de ruta en las siguientes líneas
                route_points = []
                for j in range(i + 1, min(i + 20, len(lines))):
                    route_line = lines[j].strip()
                    if route_line and not route_line.startswith("MISSION"):
                        route_point = _extract_route_point(route_line)
                        if route_point:
                            route_points.append(route_point)
                        else:
                            break
                mission_data["route"]["points"] = route_points
        
        print(f"✅ UGV: Mission brief parseado exitosamente")
        print(f"   - Víctimas: {len(mission_data['victims'])}")
        print(f"   - Obstáculos: {len(mission_data['obstacles'])}")
        print(f"   - Puntos de ruta: {len(mission_data['route'].get('points', []))}")
        
    except Exception as e:
        print(f"⚠️ UGV: Error al parsear mission brief: {e}")
    
    return mission_data

def _extract_simplified_victim_data(line):
    """Extrae datos de una víctima del formato simplificado"""
    try:
        # Formato: "Victim 1: Position=(120, 50), State=herido, Priority=media"
        parts = line.split(":")
        victim_id = parts[0].split("Victim")[1].strip()
        
        # Extraer posición
        pos_start = line.find("Position=(") + 10
        pos_end = line.find(")", pos_start)
        pos_str = line[pos_start:pos_end]
        x, y = pos_str.split(",")
        
        # Extraer estado
        state_start = line.find("State=") + 6
        state_end = line.find(",", state_start)
        if state_end == -1:
            state_end = len(line)
        state = line[state_start:state_end]
        
        # Extraer prioridad
        priority_start = line.find("Priority=") + 9
        priority = line[priority_start:].strip()
        
        return {
            "id": int(victim_id),
            "coordenadas": {"x": int(x.strip()), "y": int(y.strip())},
            "estado": state.strip(),
            "prioridad": priority
        }
        
    except Exception as e:
        print(f"⚠️ UGV: Error al extraer datos de víctima: {e}")
        return None

def _extract_simplified_obstacle_data(line):
    """Extrae datos de un obstáculo del formato simplificado"""
    try:
        # Formato: "Obstacle 1: Position=(170, 120), Type=escombro, Risk=ALTO"
        parts = line.split(":")
        obstacle_id = parts[0].split("Obstacle")[1].strip()
        
        # Extraer posición
        pos_start = line.find("Position=(") + 10
        pos_end = line.find(")", pos_start)
        pos_str = line[pos_start:pos_end]
        x, y = pos_str.split(",")
        
        # Extraer tipo
        type_start = line.find("Type=") + 5
        type_end = line.find(",", type_start)
        if type_end == -1:
            type_end = len(line)
        obstacle_type = line[type_start:type_end]
        
        # Extraer riesgo
        risk_start = line.find("Risk=") + 5
        risk = line[risk_start:].strip()
        
        return {
            "id": int(obstacle_id),
            "coordenadas": {"x": int(x.strip()), "y": int(y.strip())},
            "tipo": obstacle_type.strip(),
            "nivel_riesgo": risk
        }
        
    except Exception as e:
        print(f"⚠️ UGV: Error al extraer datos de obstáculo: {e}")
        return None

def _extract_route_point(line):
    """Extrae un punto de ruta del formato simplificado"""
    try:
        # Formato: "  1. (10, 10) - inicio" o "  3. (230, 210) - victima (ID: 2)"
        if not line.strip() or not line.strip()[0].isdigit():
            return None
            
        # Extraer número de punto
        point_num = line.split(".")[0].strip()
        
        # Extraer coordenadas
        pos_start = line.find("(") + 1
        pos_end = line.find(")", pos_start)
        pos_str = line[pos_start:pos_end]
        x, y = pos_str.split(",")
        
        # Extraer tipo
        type_start = line.find("-") + 2
        type_end = line.find("(", type_start)
        if type_end == -1:
            type_end = len(line)
        point_type = line[type_start:type_end].strip()
        
        # Extraer ID de víctima si existe
        victim_id = ""
        if "(ID:" in line:
            id_start = line.find("(ID:") + 4
            id_end = line.find(")", id_start)
            victim_id = line[id_start:id_end]
        
        return {
            "numero": int(point_num),
            "coordenadas": {"x": int(x.strip()), "y": int(y.strip())},
            "tipo": point_type,
            "victima_id": victim_id.strip() if victim_id else ""
        }
        
    except Exception as e:
        print(f"⚠️ UGV: Error al extraer punto de ruta: {e}")
        return None

def planificadorMision(state: UGVState) -> UGVState:
    """Planifica la ejecución de la misión terrestre"""
    if not state.get("mission_received", False):
        return state
    
    print("🗺️ UGV: Planificando ejecución terrestre...")
    
    mission_data = state["mission_data"]
    victims = mission_data.get("victims", [])
    obstacles = mission_data.get("obstacles", [])
    route = mission_data.get("route", {})
    
    # Crear plan de ejecución
    execution_plan = {
        "plan_id": f"UGV_PLAN_{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "victims_to_rescue": len(victims),
        "obstacles_to_avoid": len(obstacles),
        "route_available": bool(route),
        "status": "PLANNING_COMPLETE"
    }
    
    state["mission_status"] = "PLANNING_COMPLETE"
    print(f"🗺️ UGV: Plan de ejecución creado - {len(victims)} víctimas a rescatar")
    
    # Mostrar información de la ruta
    if route.get("points"):
        print(f"🗺️ UGV: Ruta con {len(route['points'])} puntos")
        print(f"   - Distancia: {route.get('distance', 'N/A')}")
        print(f"   - Tiempo: {route.get('time', 'N/A')}")
        print(f"   - Orden de visita: {route.get('visit_order', [])}")
    
    return state

def ejecutorMision(state: UGVState) -> UGVState:
    """Coordina la ejecución de la misión enviando puntos objetivo al controlador"""
    # Inicializar variables si es la primera vez
    if state.get("mission_status") == "PLANNING_COMPLETE":
        print("🚀 UGV: Iniciando ejecución de misión con controlador de movimiento...")
        state["route_index"] = 0
        state["arrival_confirmed"] = False
        state["movement_speed"] = 2.0  # píxeles por comando
        state["mission_status"] = "READY_FOR_POINT"
    
    # Solo procesar si estamos listos para enviar un punto
    if state.get("mission_status") != "READY_FOR_POINT":
        return state
    
    # Obtener información de la ruta
    mission_data = state["mission_data"]
    route = mission_data.get("route", {})
    route_points = route.get("points", [])
    
    if not route_points:
        print("⚠️ UGV: No hay puntos en la ruta")
        state["mission_status"] = "MISSION_COMPLETE"
        return state
    
    route_index = state.get("route_index", 0)
    
    # Verificar si hemos completado todos los puntos
    if route_index >= len(route_points):
        print(f"✅ UGV: Todos los puntos de la ruta completados")
        state["mission_status"] = "MISSION_COMPLETE"
        return state
    
    # Enviar siguiente punto objetivo
    point = route_points[route_index]
    coords = point.get("coordenadas", {})
    target_x = coords.get("x", 0)
    target_y = coords.get("y", 0)
    tipo = point.get("tipo", "desconocido")
    victima_id = point.get("victima_id", "")
    
    state["target_point"] = (target_x, target_y)
    state["mission_status"] = "MOVING"
    state["arrival_confirmed"] = False
    
    print(f"🎯 UGV Executor: Enviando punto {route_index + 1}/{len(route_points)}")
    print(f"   └─ Objetivo: ({target_x}, {target_y}) - {tipo}")
    if victima_id:
        print(f"   └─ Víctima ID: {victima_id}")
    
    return state


def controladorMovimiento(state: UGVState) -> UGVState:
    """Controlador de movimiento que genera comandos (x,y) hacia el punto objetivo"""
    if state.get("mission_status") != "MOVING":
        return state
    
    current_pos = state.get("current_position", (10, 10))
    target_point = state.get("target_point")
    movement_speed = state.get("movement_speed", 2.0)
    
    if not target_point:
        return state
    
    current_x, current_y = current_pos
    target_x, target_y = target_point
    
    # Calcular distancia al objetivo
    dx = target_x - current_x
    dy = target_y - current_y
    distance = math.sqrt(dx**2 + dy**2)
    
    # Verificar si hemos llegado al objetivo
    if distance <= movement_speed:
        # Llegamos al objetivo
        state["current_position"] = target_point
        state["arrival_confirmed"] = True
        
        print(f"✅ UGV Controller: Llegada confirmada a ({target_x}, {target_y})")
        print(f"   └─ Distancia recorrida desde inicio: {distance:.1f} px")
        
        # Obtener información del punto alcanzado
        route_index = state.get("route_index", 0)
        mission_data = state["mission_data"]
        route_points = mission_data.get("route", {}).get("points", [])
        
        if route_index < len(route_points):
            point = route_points[route_index]
            tipo = point.get("tipo", "desconocido")
            victima_id = point.get("victima_id", "")
            
            # Si es una víctima, activar protocolo de atención
            if tipo == "victima" and victima_id:
                coords = point.get("coordenadas", {})
                state["current_victim_info"] = {
                    "id": victima_id,
                    "coordinates": coords,
                    "tipo": tipo
                }
                state["mission_status"] = "VICTIM_ATTENTION"
                state["attention_in_progress"] = True
                state["attention_complete"] = False
                print(f"🚑 UGV: Víctima detectada - Activando protocolo de atención")
            else:
                # Para otros puntos, continuar directamente
                if tipo == "inicio":
                    print(f"🏁 UGV: Punto de inicio alcanzado")
                else:
                    print(f"📍 UGV: Punto intermedio alcanzado")
                
                time.sleep(0.5)  # Pausa breve
                
                # Avanzar al siguiente punto
                state["route_index"] = route_index + 1
                state["mission_status"] = "READY_FOR_POINT"
                state["target_point"] = None
        else:
            # Sin más puntos
            state["route_index"] = route_index + 1
            state["mission_status"] = "READY_FOR_POINT"
            state["target_point"] = None
        
    else:
        # Calcular siguiente posición (movimiento en línea recta)
        # Normalizar vector de dirección
        direction_x = dx / distance
        direction_y = dy / distance
        
        # Calcular nueva posición
        new_x = current_x + direction_x * movement_speed
        new_y = current_y + direction_y * movement_speed
        
        # Actualizar posición
        state["current_position"] = (int(new_x), int(new_y))
        
        # Mostrar comando de movimiento
        print(f"🚗 UGV Controller: Moviendo a ({int(new_x)}, {int(new_y)}) | Distancia restante: {distance:.1f} px")
        
        time.sleep(0.1)  # Pequeña pausa para visualizar el movimiento
    
    return state


def atencionVictimas(state: UGVState) -> UGVState:
    """Protocolo de atención de víctimas - Ejecuta procedimientos de rescate"""
    if state.get("mission_status") != "VICTIM_ATTENTION":
        return state
    
    victim_info = state.get("current_victim_info", {})
    victim_id = victim_info.get("id", "unknown")
    coordinates = victim_info.get("coordinates", {})
    x = coordinates.get("x", 0)
    y = coordinates.get("y", 0)
    
    print(f"🚑 UGV: Iniciando protocolo de atención para víctima {victim_id}")
    print(f"   └─ Ubicación: ({x}, {y})")
    print(f"   └─ Evaluando estado de la víctima...")
    time.sleep(1)
    
    # Simulación del protocolo de atención
    print(f"   └─ Fase 1: Evaluación inicial completada")
    time.sleep(0.5)
    
    print(f"   └─ Fase 2: Estabilización en proceso...")
    time.sleep(1)
    
    print(f"   └─ Fase 3: Preparación para evacuación...")
    time.sleep(1)
    
    print(f"   └─ Fase 4: Víctima asegurada")
    time.sleep(0.5)
    
    # Registrar víctima rescatada
    victims_rescued = state.get("victims_rescued", [])
    victims_rescued.append({
        "id": victim_id,
        "coordinates": coordinates,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "RESCUED"
    })
    state["victims_rescued"] = victims_rescued
    
    # Actualizar log de comunicación
    communication_log = state.get("communication_log", [])
    communication_log.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": "VICTIM_RESCUED",
        "victim_id": victim_id,
        "coordinates": coordinates,
        "status": "SUCCESS"
    })
    state["communication_log"] = communication_log
    
    # Marcar atención como completada
    state["attention_complete"] = True
    state["attention_in_progress"] = False
    
    print(f"✅ UGV: Protocolo de atención completado para víctima {victim_id}")
    print(f"   └─ Total de víctimas rescatadas: {len(victims_rescued)}")
    print(f"   └─ Enviando confirmación para continuar ruta...")
    
    # Avanzar al siguiente punto
    state["route_index"] = state.get("route_index", 0) + 1
    state["mission_status"] = "READY_FOR_POINT"
    state["target_point"] = None
    state["current_victim_info"] = {}
    
    time.sleep(0.5)  # Pausa antes de continuar
    
    return state


def continuarEjecutor(state: UGVState) -> str:
    """Controla si el ejecutor debe enviar más puntos o pasar al controlador"""
    status = state.get("mission_status", "")
    
    if status == "MISSION_COMPLETE":
        return "finalizar"
    elif status == "MOVING":
        return "mover"
    elif status == "READY_FOR_POINT":
        return "ejecutar"
    else:
        return "ejecutar"

def continuarControlador(state: UGVState) -> str:
    """Controla si el controlador debe seguir moviéndose, atender víctima o volver al ejecutor"""
    status = state.get("mission_status", "")
    
    if status == "VICTIM_ATTENTION":
        return "atender"
    elif status == "READY_FOR_POINT":
        return "ejecutar"
    elif status == "MOVING":
        return "mover"
    else:
        return "ejecutar"

def create_ugv_graph():
    """Crea y compila el grafo de trabajo del UGV"""
    # Crear grafo UGV con controlador de movimiento y atención de víctimas
    ugv_workflow = StateGraph(UGVState)
    ugv_workflow.add_node("receptorMensaje", receptorMensaje)
    ugv_workflow.add_node("planificadorMision", planificadorMision)
    ugv_workflow.add_node("ejecutorMision", ejecutorMision)
    ugv_workflow.add_node("controladorMovimiento", controladorMovimiento)
    ugv_workflow.add_node("atencionVictimas", atencionVictimas)
    
    # Definir el flujo
    ugv_workflow.set_entry_point("receptorMensaje")
    ugv_workflow.add_edge("receptorMensaje", "planificadorMision")
    ugv_workflow.add_edge("planificadorMision", "ejecutorMision")
    
    # Flujo entre ejecutor y controlador
    ugv_workflow.add_conditional_edges(
        "ejecutorMision",
        continuarEjecutor,
        {
            "ejecutar": "ejecutorMision",       # Preparar siguiente punto
            "mover": "controladorMovimiento",   # Pasar al controlador
            "finalizar": END                     # Misión completada
        }
    )
    
    # Flujo del controlador: seguir moviéndose, atender víctima o volver al ejecutor
    ugv_workflow.add_conditional_edges(
        "controladorMovimiento",
        continuarControlador,
        {
            "mover": "controladorMovimiento",  # Seguir moviéndose
            "atender": "atencionVictimas",      # Atender víctima detectada
            "ejecutar": "ejecutorMision"        # Punto alcanzado, volver al ejecutor
        }
    )
    
    # Flujo de atención de víctimas: después de atender, volver al ejecutor
    ugv_workflow.add_edge("atencionVictimas", "ejecutorMision")
    
    # Compilar y retornar
    return ugv_workflow.compile()

# Variable global para el grafo compilado (para langgraph.json)
g = create_ugv_graph()

def main():
    print("🚗 SISTEMA UGV - CON CONTROLADOR DE MOVIMIENTO Y ATENCIÓN DE VÍCTIMAS")
    print("=" * 60)
    
    # Estado inicial
    initial_state = {
        "mission_received": False,
        "mission_data": {},
        "current_position": (10, 10),
        "target_victims": [],
        "obstacles_avoided": [],
        "mission_status": "WAITING",
        "communication_log": [],
        "message_file": "uav_to_ugv_message.json",
        # Campos del controlador
        "target_point": None,
        "route_index": 0,
        "arrival_confirmed": False,
        "movement_speed": 2.0,
        # Campos de atención de víctimas
        "current_victim_info": {},
        "attention_in_progress": False,
        "attention_complete": False,
        "victims_rescued": []
    }
    
    # Usar el grafo global compilado
    ugv_app = g
    
    try:
        print("🎯 Flujo de trabajo:")
        print("   messageReceiver → missionPlanner → missionExecutor ⇄ movementController")
        print("=" * 60)
        ugv_app.invoke(initial_state, config={"recursion_limit": 10000})
    except Exception as e:
        print(f"❌ Error en UGV: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔚 UGV Agent terminado")

if __name__ == "__main__":
    main()
