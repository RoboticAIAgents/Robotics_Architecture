# Sistema de Detección de Colisiones UGV

## 📋 Descripción General

El sistema de detección de colisiones del UGV permite al robot terrestre adaptarse dinámicamente a cambios en el entorno, evitando obstáculos y replanificando rutas en tiempo real.

## 🔧 Componentes Principales

### 1. ProximitySensor Class

**Ubicación**: `UGV_Agent.py` (líneas 17-105)

**Funcionalidades**:
- Detección de obstáculos en rango configurable (25 píxeles por defecto)
- Verificación de amenazas en el camino hacia objetivos
- Simulación de obstáculos dinámicos (cambios en el entorno)
- Cálculo de distancia perpendicular para determinar colisiones

**Métodos principales**:
- `check_collision_risk()`: Función principal de detección
- `_is_in_path()`: Verifica si un obstáculo está en el camino
- `_create_dynamic_obstacle()`: Simula obstáculos dinámicos

### 2. Estados del UGV

**Campos agregados al UGVState**:
```python
proximity_sensor: ProximitySensor    # Sensor de proximidad
current_route_index: int            # Índice del punto actual
collision_threats: list             # Amenazas detectadas
path_corrections: list              # Historial de correcciones
```

## 🔄 Flujo de Detección

### 1. Escaneo Continuo
- El sensor escanea el entorno cada vez que se ejecuta
- Verifica obstáculos conocidos en el rango de detección
- Simula obstáculos dinámicos con probabilidad del 20%

### 2. Análisis de Amenazas
- Calcula distancia a cada obstáculo
- Determina si el obstáculo está en el camino hacia el objetivo
- Evalúa nivel de riesgo (ALTO, MEDIO, BAJO)

### 3. Replanificación
- Si se detectan amenazas, activa replanificación con GPT
- Genera nueva ruta que evita obstáculos detectados
- Registra corrección en el historial

## 🧮 Algoritmos Utilizados

### Detección de Obstáculos en Camino

```python
def _is_in_path(self, start, end, obstacle, margin=10):
    # Calcular vector de movimiento
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    # Normalizar vector
    dx_norm = dx / distance
    dy_norm = dy / distance
    
    # Calcular proyección del obstáculo
    A = obstacle[0] - start[0]
    B = obstacle[1] - start[1]
    projection = A * dx_norm + B * dy_norm
    
    # Verificar si está en el rango del camino
    if projection < 0 or projection > distance:
        return False
    
    # Calcular distancia perpendicular
    perp_distance = abs(A * dy_norm - B * dx_norm)
    return perp_distance <= margin
```

## 📊 Configuración de Parámetros

### Parámetros del Sensor
- **detection_range**: 25 píxeles (rango de detección)
- **margin**: 10 píxeles (margen de seguridad)
- **dynamic_probability**: 20% (probabilidad de obstáculo dinámico)

### Parámetros de Replanificación
- **safety_margin**: 20 píxeles (margen para GPT)
- **scan_frequency**: Cada ejecución del nodo
- **threat_threshold**: Cualquier amenaza activa replanificación

## 🎯 Casos de Uso

### 1. Obstáculo Estático
- **Situación**: Edificio o vehículo estacionario en el camino
- **Acción**: Replanificar ruta para evitar el obstáculo
- **Resultado**: Nueva ruta que mantiene distancia segura

### 2. Obstáculo Dinámico
- **Situación**: Persona o vehículo que aparece inesperadamente
- **Acción**: Detectar y replanificar inmediatamente
- **Resultado**: Adaptación rápida al cambio

### 3. Múltiples Amenazas
- **Situación**: Varios obstáculos en diferentes posiciones
- **Acción**: Evaluar todas las amenazas y replanificar
- **Resultado**: Ruta optimizada que evita todos los obstáculos

## 📈 Métricas y Monitoreo

### Registro de Eventos
- **Timestamp**: Momento de detección
- **Position**: Posición del robot
- **Threats_count**: Número de amenazas detectadas
- **Reason**: Razón de la corrección (collision_avoidance)
- **Route_changes**: Cambios en la ruta original

### Estadísticas de Misión
- Víctimas rescatadas
- Correcciones de ruta realizadas
- Obstáculos evitados
- Tiempo total de ejecución

## 🔧 Configuración Avanzada

### Ajustar Sensibilidad
```python
# Aumentar rango de detección
sensor = ProximitySensor(detection_range=40)

# Aumentar margen de seguridad
def _is_in_path(self, start, end, obstacle, margin=20):
```

### Modificar Probabilidad de Obstáculos Dinámicos
```python
# Reducir probabilidad de obstáculos dinámicos
if random.random() < 0.1:  # 10% en lugar de 20%
```

## 🐛 Solución de Problemas

### Problema: Falsos Positivos
- **Causa**: Margen de seguridad muy amplio
- **Solución**: Reducir el parámetro `margin`

### Problema: No Detecta Amenazas
- **Causa**: Rango de detección muy pequeño
- **Solución**: Aumentar `detection_range`

### Problema: Replanificación Excesiva
- **Causa**: Probabilidad de obstáculos dinámicos muy alta
- **Solución**: Reducir la probabilidad en `_create_dynamic_obstacle()`

## 🚀 Próximas Mejoras

1. **Aprendizaje Adaptativo**: Ajustar parámetros según experiencia
2. **Predicción de Movimiento**: Anticipar movimiento de obstáculos
3. **Optimización Multi-Objetivo**: Balancear tiempo vs. seguridad
4. **Integración con Sensores Reales**: Conectar con hardware físico
