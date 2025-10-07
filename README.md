# Sistema Multi-Agente UAV-UGV para Operaciones de Rescate

Este proyecto implementa un sistema multi-agente utilizando LangGraph para operaciones de rescate coordinadas entre un UAV (vehículo aéreo no tripulado) y un UGV (vehículo terrestre no tripulado).

## 🚁 Componentes del Sistema

### UAV Agent (`UAV_agent.py`)
- **Análisis de video**: Procesa secuencias de video para identificar víctimas y obstáculos
- **Identificación de víctimas**: Utiliza GPT-4o para detectar y clasificar víctimas por estado de salud
- **Identificación de obstáculos**: Detecta edificios, vehículos, escombros y otros obstáculos
- **Planificación de rutas**: Genera rutas optimizadas que visitan todas las víctimas
- **Compilación de misiones**: Crea briefings estructurados para el UGV

### UGV Agent (`UGV_Agent.py`)
- **Recepción de misiones**: Lee y procesa briefings del UAV
- **Detección de colisiones**: Sistema de sensor de proximidad para evitar obstáculos
- **Corrección de trayectoria**: Replanificación automática cuando detecta amenazas
- **Ejecución terrestre**: Navegación paso a paso con rescate de víctimas

## 🔧 Características Técnicas

### Tecnologías Utilizadas
- **LangGraph**: Framework para aplicaciones multi-agente con estado
- **OpenAI GPT-4o/GPT-5-mini**: Análisis de imágenes y planificación inteligente
- **OpenCV**: Procesamiento de video e imágenes
- **Python**: Lenguaje principal del proyecto

### Capacidades del Sistema
- ✅ **Análisis en tiempo real** de video de UAV
- ✅ **Identificación precisa** de víctimas y obstáculos
- ✅ **Planificación optimizada** de rutas de rescate
- ✅ **Detección de colisiones** con sensor de proximidad
- ✅ **Replanificación automática** ante cambios en el entorno
- ✅ **Comunicación inter-agente** mediante archivos JSON
- ✅ **Registro detallado** de operaciones y correcciones

## 📁 Estructura del Proyecto

```
Practicas langgrahp/
├── UAV_agent.py              # Agente aéreo principal
├── UGV_Agent.py              # Agente terrestre con detección de colisiones
├── multi_agent_system.py     # Sistema coordinado UAV-UGV
├── video_sim.py              # Simulador de video
├── uav_to_ugv_message.json   # Archivo de comunicación entre agentes
├── uav_simulation.mp4        # Video de simulación
├── frame_analysis_*.png      # Análisis de frames del video
├── venv/                     # Entorno virtual Python
├── .langgraph_api/           # Configuración de LangGraph API
├── langgraph.json            # Configuración del proyecto
└── README.md                 # Este archivo
```

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- OpenAI API Key

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd Practicas-langgrahp
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install langgraph langchain-openai opencv-python python-dotenv
   ```

4. **Configurar variables de entorno**:
   ```bash
   # Crear archivo .env
   echo "OPENAI_API_KEY=tu_api_key_aqui" > .env
   ```

## 🎯 Uso del Sistema

### Ejecutar UAV Agent
```bash
python UAV_agent.py
```

### Ejecutar UGV Agent
```bash
python UGV_Agent.py
```

### Ejecutar Sistema Multi-Agente
```bash
python multi_agent_system.py
```

## 🔄 Flujo de Trabajo

1. **UAV** analiza video y identifica víctimas/obstáculos
2. **UAV** planifica rutas optimizadas
3. **UAV** compila briefing de misión
4. **UGV** recibe y procesa briefing
5. **UGV** ejecuta rescate con detección de colisiones
6. **UGV** replanifica automáticamente ante obstáculos

## 🛡️ Sistema de Detección de Colisiones

El UGV incluye un sistema avanzado de detección de colisiones:

- **Sensor de proximidad**: Detecta obstáculos en un rango configurable
- **Detección en tiempo real**: Escanea el entorno continuamente
- **Obstáculos dinámicos**: Detecta cambios en el entorno
- **Replanificación inteligente**: Usa GPT para generar rutas alternativas
- **Margen de seguridad**: Mantiene distancia segura de obstáculos

## 📊 Monitoreo y Logging

El sistema registra:
- Víctimas identificadas y rescatadas
- Obstáculos detectados y evitados
- Correcciones de ruta realizadas
- Tiempos de ejecución y eficiencia

## 🤝 Contribuciones

Este proyecto forma parte de un PFG (Proyecto Final de Grado) enfocado en sistemas multi-agente para operaciones de rescate.

## 📝 Licencia

Proyecto académico - Uso educativo y de investigación.

## 🔗 Referencias

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenCV Documentation](https://docs.opencv.org/)
