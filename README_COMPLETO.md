# Detector de Tráfico Anómalo en Red 🚨

Sistema completo de detección de tráfico anómalo en tiempo real con dashboard interactivo.

## 🎯 Características

### Backend (Python)
- ✅ **Captura de Paquetes en Tiempo Real** - Utilizando Scapy
- ✅ **Detección de Anomalías Avanzada**
  - Algoritmos de Machine Learning (Isolation Forest)
  - Detección estadística
  - Análisis de patrones de tráfico
- ✅ **Múltiples Tipos de Alertas**
  - SYN Flood detection
  - ICMP Flood detection
  - Port Scanning detection
  - Anomalías de tamaño de paquete
- ✅ **API REST Completa** - Flask con WebSocket
- ✅ **Persistencia de Datos** - PostgreSQL/MongoDB
- ✅ **Análisis de Flujos de Red** - Estadísticas en tiempo real

### Frontend (React)
- 🎨 **Dashboard Interactivo Moderno**
- 📊 **Gráficos en Tiempo Real**
  - Líneas de tráfico
  - Distribución de protocolos
  - Estado de anomalías
  - Top de puertos
- 📋 **Paneles de Información**
  - Anomalías detectadas
  - Paquetes capturados
  - Flujos de red activos
- 🔌 **Actualizaciones en Vivo** - WebSocket
- 📱 **Responsive Design** - Funciona en móviles

## 🛠️ Requisitos Previos

### Windows
- Python 3.8+
- Node.js 14+
- Npcap (para captura de paquetes)

### Linux
- Python 3.8+
- Node.js 14+
- libpcap-dev
- Permisos de root/sudo

### macOS
- Python 3.8+
- Node.js 14+
- Xcode Command Line Tools

## 📦 Instalación

### Opción 1: Instalador Automático

**Windows (ejecutar como Administrador):**
```bash
.\install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

### Opción 2: Instalación Manual

1. **Clonar/Descargar el proyecto**
```bash
cd "Detector de tráfico anomalo"
```

2. **Configurar Backend**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate.bat
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

3. **Configurar Frontend**
```bash
cd frontend
npm install
cd ..
```

## 🚀 Uso

### 1. Iniciar Backend (requiere permisos administrativos)

**Windows (Como Administrador):**
```bash
venv\Scripts\activate.bat
python backend/app.py
```

**Linux/macOS:**
```bash
source venv/bin/activate
sudo python backend/app.py
```

El backend estará disponible en `http://localhost:5000`

### 2. Iniciar Frontend (en otra terminal)

```bash
cd frontend
npm start
```

El dashboard estará disponible en `http://localhost:3000`

## 📊 Cómo Usar el Dashboard

### Panel Principal
1. **Estadísticas en Vivo**: Visualiza el tráfico actual
2. **Botones de Control**:
   - **Iniciar Captura**: Comienza la captura de paquetes
   - **Detener Captura**: Detiene la captura

### Pestañas de Información

#### 📈 Resumen
- Gráficos de tráfico en tiempo real
- Distribución de protocolos
- Estado de anomalías
- Top de puertos usados

#### ⚠️ Anomalías
- Lista de anomalías detectadas
- Severidad (CRITICAL, HIGH, MEDIUM, LOW)
- Score de anomalía
- Recomendaciones de acción

#### 📦 Paquetes
- Tabla de paquetes capturados
- Información de IP, puertos, protocolo
- Tamaño de paquete
- Timestamps precisos

#### 🔗 Flujos
- Flujos de red activos
- Estadísticas por flujo
- Protocolos y puertos utilizados
- Visualización de actividad

## 🔧 Configuración Avanzada

Editar `.env` para personalizar:

```env
# Interfaz de red a monitorear
CAPTURE_INTERFACE=eth0

# Umbral de detección (0-1)
ANOMALY_THRESHOLD=0.7

# Base de datos
DB_TYPE=postgresql
DB_HOST=localhost
DB_NAME=detector_trafico

# Nivel de logging
LOG_LEVEL=INFO
```

## 📚 Estructura del Proyecto

```
Detector de tráfico anomalo/
├── backend/
│   ├── app.py                 # API Flask y WebSocket
│   ├── packet_capture.py      # Captura de paquetes
│   ├── anomaly_detector.py    # Detección de anomalías
│   ├── database_manager.py    # Gestión de BD
│   └── example_capture.py     # Ejemplo de uso
├── frontend/
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── App.js             # Aplicación principal
│   │   └── index.js           # Punto de entrada
│   └── package.json
├── requirements.txt           # Dependencias Python
├── .env                       # Configuración
├── install.sh                 # Instalador Linux/macOS
└── install.bat                # Instalador Windows
```

## 🔍 Algoritmos de Detección

### 1. Aislamiento (Isolation Forest)
- Detección de anomalías no supervisada
- Identifica patrones inusuales en características de paquetes
- Modelo de machine learning entrenado

### 2. Análisis Estadístico
- Desviaciones estándar de tamaños de paquete
- Detección de patrones anormales de tráfico
- Análisis de puerto y protocolo

### 3. Detección de Ataques Específicos
- **SYN Flood**: Detecta un número anormalmente alto de paquetes SYN
- **ICMP Flood**: Identifica paquetes ICMP excesivos
- **Port Scanning**: Reconoce intentos de escaneo de puertos
- **DNS Queries Anómalas**: Flagea consultas DNS inusuales

## 📊 Métricas Capturadas

### Por Paquete
- IP Origen/Destino
- Puertos Origen/Destino
- Protocolo (TCP, UDP, ICMP, IPv6)
- Tamaño del paquete
- Flags TCP (SYN, FIN, RST, etc.)
- TTL (Time To Live)
- Consultas DNS

### Por Flujo
- Cantidad de paquetes
- Bytes totales
- Protocolos utilizados
- Puertos involucrados
- Duración del flujo

## 🔐 Seguridad

- ⚠️ **Importante**: El backend requiere permisos de administrador/root
- API con autenticación básica (configurable)
- WebSocket con validación de conexión
- Base de datos con credenciales separadas

## 🐛 Troubleshooting

### Error: "Permission denied"
- **Windows**: Ejecutar como Administrador
- **Linux/macOS**: Usar `sudo` al ejecutar

### Error: "No interface found"
- Verificar interfaz de red: `ipconfig` (Windows) o `ifconfig` (Linux)
- Cambiar `CAPTURE_INTERFACE` en `.env`

### Puerto 5000/3000 ocupado
```bash
# Cambiar puerto en backend
python backend/app.py --port 5001

# Cambiar puerto en frontend
PORT=3001 npm start
```

### Error de conexión a base de datos
- Verificar que PostgreSQL/MongoDB está ejecutándose
- Verificar credenciales en `.env`
- Crear base de datos manualmente si es necesario

## 📖 Documentación API

### Endpoints principales

#### GET `/api/health`
Estado del servidor

#### POST `/api/capture/start`
Inicia la captura de paquetes

#### POST `/api/capture/stop`
Detiene la captura

#### GET `/api/statistics`
Estadísticas actuales

#### GET `/api/anomalies?limit=100`
Anomalías detectadas

#### GET `/api/flows`
Flujos de red activos

#### GET `/api/packets?limit=50`
Paquetes capturados recientes

### WebSocket Events

- `connect`: Cliente conectado
- `subscribe_stats`: Suscribirse a actualizaciones de estadísticas
- `stats_update`: Actualización de estadísticas
- `anomaly_detected`: Nueva anomalía detectada

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo licencia MIT

## 🆘 Soporte

Para reportar bugs o solicitar features, crea un issue en el repositorio.

## 📞 Contacto

Para preguntas o soporte técnico, contacta al desarrollador.

---

⭐ Si te fue útil, considera dar una estrella al proyecto!
