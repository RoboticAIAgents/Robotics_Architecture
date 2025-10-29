# Sistema Multi-Agente UAV-UGV para Operaciones de Rescate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.0+-green.svg)](https://python.langchain.com/docs/langgraph)

Este proyecto implementa un sistema multi-agente utilizando LangGraph para operaciones de rescate coordinadas entre un UAV (vehículo aéreo no tripulado) y un UGV (vehículo terrestre no tripulado). Desarrollado como parte de la [Arquitectura Robótica](https://github.com/RoboticAIAgents/Robotics_Architecture) de RoboticAIAgents.

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
MultiAgent/
├── UAV_agent.py              # Agente aéreo principal
├── UGV_Agent.py              # Agente terrestre con detección de colisiones
├── video_sim.py              # Simulador de video
├── uav_to_ugv_message.json   # Archivo de comunicación entre agentes
├── uav_simulation.mp4        # Video de simulación
├── frame_analysis_*.png      # Análisis de frames del video
├── venv/                     # Entorno virtual Python
├── .langgraph_api/           # Configuración de LangGraph API
├── langgraph.json            # Configuración del proyecto
├── requirements.txt          # Dependencias del proyecto
├── setup.py                  # Script de configuración automática
├── config.example            # Archivo de configuración de ejemplo
├── .gitignore               # Archivos ignorados por Git
├── LICENSE                  # Licencia MIT
└── README.md                # Este archivo
```

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- OpenAI API Key

### Instalación Automática (Recomendada)

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/RoboticAIAgents/Robotics_Architecture.git
   cd Robotics_Architecture/MultiAgent
   ```

2. **Ejecutar script de configuración**:
   ```bash
   python setup.py
   ```

3. **Configurar API Key**:
   - Editar el archivo `.env` generado
   - Reemplazar `your_openai_api_key_here` con tu API key real

### Instalación Manual

1. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   ```bash
   # Copiar archivo de ejemplo
   cp config.example .env
   # Editar .env con tu API key
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

Este proyecto forma parte de la [Arquitectura Robótica](https://github.com/RoboticAIAgents/Robotics_Architecture) de RoboticAIAgents y está abierto a contribuciones de la comunidad. 

### Cómo Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Reportar Issues

Si encuentras algún problema o tienes una sugerencia, por favor abre un [issue](https://github.com/RoboticAIAgents/Robotics_Architecture/issues) en el repositorio.

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Referencias

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenCV Documentation](https://docs.opencv.org/)
