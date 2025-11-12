"""
API REST con Flask y WebSocket para comunicación en tiempo real
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv
from functools import wraps
from threading import Thread, Event
import json
from collections import deque

from packet_capture import NetworkPacketCapture
from anomaly_detector import AnomalyDetector, TrafficPattern
from database_manager import DatabaseFactory

# Cargar configuración
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
CORS(app)

# Inicializar SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado global
class AppState:
    def __init__(self):
        self.capture_thread = None
        self.is_capturing = False
        self.packet_buffer = deque(maxlen=1000)
        self.anomaly_detector = AnomalyDetector(
            window_size=100,
            contamination=float(os.getenv('ANOMALY_THRESHOLD', 0.1))
        )
        self.traffic_pattern = TrafficPattern(window_minutes=5)
        self.db_manager = None
        self.stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'anomalies_detected': 0,
            'start_time': datetime.now()
        }
        self.stop_event = Event()
        
app_state = AppState()


# Decorador para requerir autenticación (básica)
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != os.getenv('API_PASSWORD', 'admin'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ========================
# Rutas API REST
# ========================

@app.route('/api/health', methods=['GET'])
def health():
    """Verifica el estado de la API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'capturing': app_state.is_capturing
    })


@app.route('/api/capture/start', methods=['POST'])
@require_auth
def start_capture():
    """Inicia la captura de paquetes"""
    if app_state.is_capturing:
        return jsonify({'error': 'Capture already running'}), 400
        
    try:
        interface = request.json.get('interface') if request.is_json else None
        interface = interface or os.getenv('CAPTURE_INTERFACE')
        
        # Iniciar captura en thread separado
        app_state.is_capturing = True
        app_state.stop_event.clear()
        app_state.capture_thread = Thread(
            target=capture_worker,
            args=(interface,),
            daemon=True
        )
        app_state.capture_thread.start()
        
        logger.info(f"Captura iniciada en interfaz: {interface}")
        
        return jsonify({
            'status': 'started',
            'interface': interface,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error iniciando captura: {e}")
        app_state.is_capturing = False
        return jsonify({'error': str(e)}), 500


@app.route('/api/capture/stop', methods=['POST'])
@require_auth
def stop_capture():
    """Detiene la captura de paquetes"""
    if not app_state.is_capturing:
        return jsonify({'error': 'No capture running'}), 400
        
    app_state.is_capturing = False
    app_state.stop_event.set()
    
    logger.info("Captura detenida")
    
    return jsonify({
        'status': 'stopped',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Obtiene estadísticas actuales"""
    elapsed_time = (datetime.now() - app_state.stats['start_time']).total_seconds()
    
    return jsonify({
        'total_packets': app_state.stats['total_packets'],
        'total_bytes': app_state.stats['total_bytes'],
        'packets_per_second': app_state.stats['total_packets'] / elapsed_time if elapsed_time > 0 else 0,
        'anomalies_detected': app_state.stats['anomalies_detected'],
        'elapsed_seconds': elapsed_time,
        'buffer_size': len(app_state.packet_buffer)
    })


@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    """Obtiene anomalías recientes"""
    limit = request.args.get('limit', 100, type=int)
    
    try:
        if app_state.db_manager:
            anomalies = app_state.db_manager.get_recent_anomalies(limit)
            return jsonify(anomalies)
        else:
            return jsonify({'error': 'Database not connected'}), 503
    except Exception as e:
        logger.error(f"Error obteniendo anomalías: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/flows', methods=['GET'])
def get_flows():
    """Obtiene estadísticas de flujos de red"""
    try:
        flows = app_state.traffic_pattern.get_flow_statistics()
        
        # Ordenar por cantidad de paquetes
        sorted_flows = sorted(
            flows.items(),
            key=lambda x: x[1]['packets'],
            reverse=True
        )[:50]  # Top 50 flows
        
        return jsonify(dict(sorted_flows))
    except Exception as e:
        logger.error(f"Error obteniendo flujos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets', methods=['GET'])
def get_recent_packets():
    """Obtiene paquetes recientes"""
    limit = request.args.get('limit', 50, type=int)
    
    packets = list(app_state.packet_buffer)[-limit:]
    return jsonify(packets)


@app.route('/api/export/anomalies', methods=['GET'])
def export_anomalies():
    """Exporta anomalías en formato JSON"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        if app_state.db_manager:
            anomalies = app_state.db_manager.get_recent_anomalies(limit=10000)
            
            # Filtrar por fecha
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered = [
                a for a in anomalies 
                if datetime.fromisoformat(str(a['timestamp'])) > cutoff_time
            ]
            
            response = app.make_response(jsonify(filtered))
            response.headers['Content-Disposition'] = 'attachment; filename=anomalies.json'
            return response
        else:
            return jsonify({'error': 'Database not connected'}), 503
    except Exception as e:
        logger.error(f"Error exportando anomalías: {e}")
        return jsonify({'error': str(e)}), 500


# ========================
# WebSocket Events
# ========================

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    logger.info(f"Cliente conectado: {request.sid}")
    emit('connection_response', {
        'data': 'Conectado al servidor de detección de tráfico',
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info(f"Cliente desconectado: {request.sid}")


@socketio.on('subscribe_stats')
def handle_subscribe_stats():
    """Cliente se suscribe a estadísticas en tiempo real"""
    join_room('stats_room')
    emit('subscribed', {'room': 'stats_room'})


@socketio.on('subscribe_anomalies')
def handle_subscribe_anomalies():
    """Cliente se suscribe a anomalías en tiempo real"""
    join_room('anomalies_room')
    emit('subscribed', {'room': 'anomalies_room'})


def broadcast_stats():
    """Envía estadísticas a todos los clientes"""
    if len(app_state.packet_buffer) > 0:
        elapsed_time = (datetime.now() - app_state.stats['start_time']).total_seconds()
        stats = {
            'total_packets': app_state.stats['total_packets'],
            'total_bytes': app_state.stats['total_bytes'],
            'packets_per_second': app_state.stats['total_packets'] / elapsed_time if elapsed_time > 0 else 0,
            'anomalies_detected': app_state.stats['anomalies_detected'],
            'buffer_size': len(app_state.packet_buffer),
            'timestamp': datetime.now().isoformat()
        }
        socketio.emit('stats_update', stats, room='stats_room')


def broadcast_anomaly(anomaly_data):
    """Envía una anomalía a todos los clientes"""
    socketio.emit('anomaly_detected', anomaly_data, room='anomalies_room')


# ========================
# Funciones Worker
# ========================

def capture_worker(interface):
    """Worker para capturar paquetes en segundo plano"""
    try:
        capturer = NetworkPacketCapture(interface=interface, timeout=60)
        
        def packet_handler(packet_info):
            """Maneja cada paquete capturado"""
            app_state.packet_buffer.append(packet_info)
            app_state.stats['total_packets'] += 1
            app_state.stats['total_bytes'] += packet_info.get('size', 0)
            
            # Agregar a patrón de tráfico
            app_state.traffic_pattern.add_packet(packet_info)
            
            # Guardar en BD si está disponible
            if app_state.db_manager and app_state.stats['total_packets'] % 100 == 0:
                app_state.db_manager.save_packet(packet_info)
        
        capturer.add_callback(packet_handler)
        
        # Analizar en lotes
        batch_size = 50
        last_analysis = datetime.now()
        
        while not app_state.stop_event.is_set():
            # Análisis periódico
            if len(app_state.packet_buffer) >= batch_size:
                batch = list(app_state.packet_buffer)[-batch_size:]
                
                analysis = app_state.anomaly_detector.analyze_packet_batch(batch)
                
                if analysis['anomaly_score'] > 0.1:  # Threshold mínimo
                    app_state.stats['anomalies_detected'] += 1
                    
                    # Guardar anomalía
                    anomaly_data = {
                        'type': 'traffic_anomaly',
                        'severity': analysis['severity'],
                        'score': analysis['anomaly_score'],
                        'timestamp': datetime.now().isoformat(),
                        'details': analysis
                    }
                    
                    if app_state.db_manager:
                        app_state.db_manager.save_anomaly(anomaly_data)
                    
                    # Broadcast a clientes
                    broadcast_anomaly(anomaly_data)
                
                # Broadcast de estadísticas
                if (datetime.now() - last_analysis).total_seconds() > 5:
                    broadcast_stats()
                    last_analysis = datetime.now()
            
            # Iniciar captura
            if not app_state.is_capturing:
                logger.info("Iniciando captura de paquetes...")
                app_state.is_capturing = True
                
                try:
                    capturer.start_capture(packet_count=0)
                except KeyboardInterrupt:
                    app_state.is_capturing = False
                    break
                    
    except Exception as e:
        logger.error(f"Error en capture worker: {e}")
        app_state.is_capturing = False


# ========================
# Inicialización
# ========================

def init_database():
    """Inicializa la conexión a la base de datos"""
    try:
        db_type = os.getenv('DB_TYPE', 'postgresql')
        
        if db_type.lower() == 'postgresql':
            app_state.db_manager = DatabaseFactory.create_manager(
                'postgresql',
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
        elif db_type.lower() == 'mongodb':
            app_state.db_manager = DatabaseFactory.create_manager(
                'mongodb',
                uri=os.getenv('DB_URI', 'mongodb://localhost:27017/'),
                database=os.getenv('DB_NAME')
            )
        
        if app_state.db_manager:
            app_state.db_manager.connect()
            logger.info(f"Base de datos {db_type} inicializada")
            
    except Exception as e:
        logger.warning(f"No se pudo inicializar la base de datos: {e}")
        logger.info("Continuando sin persistencia de datos")


if __name__ == '__main__':
    logger.info("Iniciando Detector de Tráfico Anómalo...")
    
    # Inicializar BD
    init_database()
    
    # Iniciar servidor
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', False),
        allow_unsafe_werkzeug=True
    )
