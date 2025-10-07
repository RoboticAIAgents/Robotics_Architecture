import os
import json
import time
import socket
import threading
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

def messageReceiver(state: UGVState) -> UGVState:
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

def missionPlanner(state: UGVState) -> UGVState:
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

def missionExecutor(state: UGVState) -> UGVState:
    """Ejecuta la misión terrestre"""
    if state.get("mission_status") != "PLANNING_COMPLETE":
        return state
    
    print("🚀 UGV: Ejecutando misión terrestre...")
    
    # Obtener información de la ruta
    mission_data = state["mission_data"]
    route = mission_data.get("route", {})
    route_points = route.get("points", [])
    
    if route_points:
        print(f"🗺️ UGV: Siguiendo ruta optimizada...")
        
        # Simular seguimiento de ruta
        for point in route_points:
            coords = point.get("coordenadas", {})
            x = coords.get("x", 0)
            y = coords.get("y", 0)
            tipo = point.get("tipo", "desconocido")
            victima_id = point.get("victima_id", "")
            
            if tipo == "victima" and victima_id:
                print(f"🎯 UGV: Rescatando víctima {victima_id} en ({x}, {y})")
                time.sleep(1)  # Simular tiempo de rescate
            else:
                print(f"📍 UGV: Pasando por punto ({x}, {y}) - {tipo}")
                time.sleep(0.5)  # Simular tiempo de navegación
    else:
        # Fallback: rescatar víctimas directamente
        victims = state["target_victims"]
        for i, victim in enumerate(victims, 1):
            coords = victim.get("coordenadas", {})
            x = coords.get("x", 0)
            y = coords.get("y", 0)
            estado = victim.get("estado", "desconocido")
            
            print(f"🎯 UGV: Rescatando víctima {i} en ({x}, {y}) - Estado: {estado}")
            time.sleep(1)  # Simular tiempo de rescate
    
    state["mission_status"] = "MISSION_COMPLETE"
    print(f"✅ UGV: Misión completada")
    
    return state

def should_continue(state: UGVState) -> str:
    """Controla el flujo del UGV"""
    if state.get("mission_status") == "MISSION_COMPLETE":
        return "end"
    else:
        return "continue"

def main():
    print("🚗 SISTEMA UGV - LECTURA DE MENSAJES SIMPLIFICADOS DEL UAV")
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
        "message_file": "uav_to_ugv_message.json"
    }
    
    # Crear grafo UGV
    ugv_workflow = StateGraph(UGVState)
    ugv_workflow.add_node("messageReceiver", messageReceiver)
    ugv_workflow.add_node("missionPlanner", missionPlanner)
    ugv_workflow.add_node("missionExecutor", missionExecutor)
    
    ugv_workflow.set_entry_point("messageReceiver")
    ugv_workflow.add_edge("messageReceiver", "missionPlanner")
    ugv_workflow.add_edge("missionPlanner", "missionExecutor")
    ugv_workflow.add_conditional_edges(
        "missionExecutor",
        should_continue,
        {
            "continue": "messageReceiver",
            "end": END
        }
    )
    
    # Compilar y ejecutar UGV
    ugv_app = ugv_workflow.compile()
    
    try:
        ugv_app.invoke(initial_state, config={"recursion_limit": 20})
    except Exception as e:
        print(f"❌ Error en UGV: {e}")
    finally:
        print("🔚 UGV Agent terminado")

if __name__ == "__main__":
    main()
