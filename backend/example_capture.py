"""
Script de ejemplo para captura manual de paquetes
"""

import logging
from packet_capture import NetworkPacketCapture

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        # En Windows, Scapy necesita Npcap instalado
        # En Linux, necesita permisos de root
        
        logger.info("Iniciando captura de paquetes...")
        logger.info("Este script requiere permisos de administrador/root")
        logger.info("")
        logger.info("Para Windows: Ejecuta como Administrador")
        logger.info("Para Linux: Usa 'sudo python example_capture.py'")
        logger.info("")
        
        # Crear capturador
        capturer = NetworkPacketCapture(interface=None, timeout=30)
        
        packet_count = 0
        
        def on_packet(packet_info):
            global packet_count
            packet_count += 1
            print(f"\n[Paquete {packet_count}]")
            print(f"  Timestamp: {packet_info['timestamp']}")
            print(f"  Protocolo: {packet_info['protocol']}")
            print(f"  {packet_info['src_ip']}:{packet_info['src_port']} -> {packet_info['dst_ip']}:{packet_info['dst_port']}")
            print(f"  Tamaño: {packet_info['size']} bytes")
        
        capturer.add_callback(on_packet)
        
        print("Capturando paquetes durante 30 segundos...")
        print("(Presiona Ctrl+C para detener)\n")
        
        try:
            capturer.start_capture(packet_count=0)
        except KeyboardInterrupt:
            print("\n\nCaptura detenida por usuario")
        
        logger.info(f"\nTotal de paquetes capturados: {packet_count}")
        
        # Mostrar estadísticas
        stats = capturer.get_statistics()
        logger.info(f"Estadísticas:")
        logger.info(f"  Paquetes por segundo: {stats['packets_per_second']:.2f}")
        logger.info(f"  Distribución de protocolos: {stats['protocol_distribution']}")
        
    except PermissionError:
        logger.error("Este script requiere permisos de administrador/root")
        logger.error("En Windows: Ejecuta como Administrador")
        logger.error("En Linux: Usa 'sudo python example_capture.py'")
    except Exception as e:
        logger.error(f"Error: {e}")
