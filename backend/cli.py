"""
CLI para ejecutar el detector desde la línea de comandos
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from packet_capture import NetworkPacketCapture
from anomaly_detector import AnomalyDetector, TrafficPattern
from logging_config import setup_logging

# Cargar configuración
load_dotenv()

# Setup logging
logger = setup_logging(
    __name__,
    log_file=os.path.join('logs', 'detector.log'),
    level='INFO'
)

def main():
    """Función principal"""
    
    parser = argparse.ArgumentParser(
        description='Detector de Tráfico Anómalo en Red',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  python cli.py --capture --interface eth0
  python cli.py --analyze --output results.json
  python cli.py --server
        '''
    )
    
    parser.add_argument(
        '--capture',
        action='store_true',
        help='Inicia captura de paquetes'
    )
    
    parser.add_argument(
        '--interface',
        default=os.getenv('CAPTURE_INTERFACE', 'eth0'),
        help='Interfaz de red a monitorear (default: eth0)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Tiempo máximo de captura en segundos (default: 60)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=0,
        help='Número de paquetes a capturar (0=infinito, default: 0)'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Modo análisis con anomalías'
    )
    
    parser.add_argument(
        '--server',
        action='store_true',
        help='Inicia el servidor API'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Modo verbose'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel('DEBUG')
    
    try:
        if args.server:
            logger.info("Iniciando servidor API...")
            # Importar aquí para evitar depencias circulares
            from app import app, socketio
            socketio.run(app, host='0.0.0.0', port=5000, debug=args.verbose)
            
        elif args.capture:
            logger.info(f"Iniciando captura en {args.interface}...")
            logger.info(f"Timeout: {args.timeout}s, Paquetes: {args.count if args.count > 0 else 'infinito'}")
            
            capturer = NetworkPacketCapture(
                interface=args.interface,
                timeout=args.timeout
            )
            
            packet_count = 0
            anomaly_detector = AnomalyDetector() if args.analyze else None
            traffic_pattern = TrafficPattern() if args.analyze else None
            
            def on_packet(packet_info):
                nonlocal packet_count
                packet_count += 1
                
                if args.verbose:
                    logger.debug(f"[Paquete {packet_count}] {packet_info['protocol']} "
                               f"{packet_info['src_ip']}:{packet_info['src_port']} -> "
                               f"{packet_info['dst_ip']}:{packet_info['dst_port']}")
                
                if args.analyze:
                    traffic_pattern.add_packet(packet_info)
                    anomaly_detector.update_history(packet_info)
            
            capturer.add_callback(on_packet)
            
            try:
                capturer.start_capture(packet_count=args.count)
            except KeyboardInterrupt:
                logger.info("\nCaptura interrumpida por usuario")
            
            # Mostrar estadísticas
            logger.info(f"\nTotal de paquetes capturados: {packet_count}")
            stats = capturer.get_statistics()
            
            logger.info(f"Paquetes por segundo: {stats['packets_per_second']:.2f}")
            logger.info(f"Protocolos: {stats['protocol_distribution']}")
            
            if args.analyze:
                flows = traffic_pattern.get_flow_statistics()
                logger.info(f"Flujos de red únicos: {len(flows)}")
                logger.info(f"Top 5 flujos:")
                sorted_flows = sorted(flows.items(), key=lambda x: x[1]['packets'], reverse=True)[:5]
                for i, (flow_key, flow_data) in enumerate(sorted_flows, 1):
                    logger.info(f"  {i}. {flow_key}: {flow_data['packets']} paquetes, "
                              f"{flow_data['bytes']} bytes")
        else:
            parser.print_help()
            
    except PermissionError:
        logger.error("Error: Se requieren permisos de administrador")
        logger.error("En Windows: Ejecuta como Administrador")
        logger.error("En Linux/macOS: Usa 'sudo'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        sys.exit(1)

if __name__ == '__main__':
    main()
