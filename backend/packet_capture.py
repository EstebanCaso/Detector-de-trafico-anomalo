"""
Capturador de paquetes de red en tiempo real
Utiliza Scapy para capturar paquetes de la interfaz de red
"""

from scapy.all import sniff, IP, TCP, UDP, ICMP, DNS, DNSQR
from scapy.layers.inet6 import IPv6
import time
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class NetworkPacketCapture:
    """Capturador de paquetes de red"""
    
    def __init__(self, interface=None, timeout=60):
        """
        Inicializa el capturador de paquetes
        
        Args:
            interface: Interfaz de red a monitorear (si es None, usa la predeterminada)
            timeout: Tiempo máximo de captura en segundos
        """
        self.interface = interface
        self.timeout = timeout
        self.packets = []
        self.packet_count = 0
        self.start_time = None
        self.callbacks = []
        
    def add_callback(self, callback):
        """Añade una función callback para cada paquete capturado"""
        self.callbacks.append(callback)
        
    def packet_callback(self, packet):
        """Procesa cada paquete capturado"""
        self.packet_count += 1
        
        packet_info = self._extract_packet_info(packet)
        self.packets.append(packet_info)
        
        # Ejecutar callbacks
        for callback in self.callbacks:
            try:
                callback(packet_info)
            except Exception as e:
                logger.error(f"Error en callback: {e}")
                
    def _extract_packet_info(self, packet):
        """Extrae información relevante del paquete"""
        packet_data = {
            'timestamp': datetime.now().isoformat(),
            'size': len(packet),
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dst_port': None,
            'protocol': None,
            'flags': None,
            'ttl': None,
            'dns_query': None,
        }
        
        # IPv4
        if IP in packet:
            ip_layer = packet[IP]
            packet_data['src_ip'] = ip_layer.src
            packet_data['dst_ip'] = ip_layer.dst
            packet_data['ttl'] = ip_layer.ttl
            packet_data['protocol'] = ip_layer.proto
            
            # TCP
            if TCP in packet:
                tcp_layer = packet[TCP]
                packet_data['src_port'] = tcp_layer.sport
                packet_data['dst_port'] = tcp_layer.dport
                packet_data['protocol'] = 'TCP'
                packet_data['flags'] = str(tcp_layer.flags)
                
            # UDP
            elif UDP in packet:
                udp_layer = packet[UDP]
                packet_data['src_port'] = udp_layer.sport
                packet_data['dst_port'] = udp_layer.dport
                packet_data['protocol'] = 'UDP'
                
                # DNS Query
                if DNSQR in packet:
                    dns_layer = packet[DNSQR]
                    packet_data['dns_query'] = dns_layer.qname.decode('utf-8', errors='ignore')
                    
            # ICMP
            elif ICMP in packet:
                packet_data['protocol'] = 'ICMP'
                
        # IPv6
        elif IPv6 in packet:
            ipv6_layer = packet[IPv6]
            packet_data['src_ip'] = ipv6_layer.src
            packet_data['dst_ip'] = ipv6_layer.dst
            packet_data['protocol'] = 'IPv6'
            
        return packet_data
        
    def start_capture(self, packet_count=0):
        """
        Inicia la captura de paquetes
        
        Args:
            packet_count: Número de paquetes a capturar (0 = infinito)
        """
        self.start_time = time.time()
        self.packets = []
        self.packet_count = 0
        
        logger.info(f"Iniciando captura en interfaz: {self.interface}")
        
        try:
            sniff(
                iface=self.interface,
                prn=self.packet_callback,
                count=packet_count if packet_count > 0 else 0,
                timeout=self.timeout,
                store=False
            )
        except PermissionError:
            logger.error("Se requieren permisos de administrador para capturar paquetes")
            raise
        except Exception as e:
            logger.error(f"Error durante la captura: {e}")
            raise
            
    def stop_capture(self):
        """Detiene la captura de paquetes"""
        logger.info(f"Captura detenida. Paquetes capturados: {self.packet_count}")
        
    def get_statistics(self):
        """Retorna estadísticas de la captura"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        protocol_count = defaultdict(int)
        port_distribution = defaultdict(int)
        top_ips = defaultdict(int)
        
        for packet in self.packets:
            if packet['protocol']:
                protocol_count[packet['protocol']] += 1
            if packet['dst_port']:
                port_distribution[packet['dst_port']] += 1
            if packet['src_ip']:
                top_ips[packet['src_ip']] += 1
                
        return {
            'total_packets': self.packet_count,
            'elapsed_time': elapsed_time,
            'packets_per_second': self.packet_count / elapsed_time if elapsed_time > 0 else 0,
            'protocol_distribution': dict(protocol_count),
            'port_distribution': dict(sorted(port_distribution.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_ips': dict(sorted(top_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
