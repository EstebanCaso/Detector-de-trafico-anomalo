"""
Detector de anomalías en tráfico de red
Utiliza múltiples algoritmos de detección
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import EllipticEnvelope
from collections import deque
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detector de anomalías en patrones de tráfico de red"""
    
    def __init__(self, window_size=100, contamination=0.1):
        """
        Inicializa el detector de anomalías
        
        Args:
            window_size: Número de observaciones para análisis
            contamination: Proporción esperada de anomalías (0-1)
        """
        self.window_size = window_size
        self.contamination = contamination
        
        # Isolation Forest para detección de anomalías
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        # Eliptic Envelope para detección de outliers
        self.elliptic_envelope = EllipticEnvelope(contamination=contamination)
        
        self.scaler = StandardScaler()
        self.feature_history = deque(maxlen=window_size)
        self.anomalies = []
        self.predictions = []
        
    def extract_features(self, packet_batch):
        """
        Extrae características de un lote de paquetes
        
        Args:
            packet_batch: Lista de diccionarios de paquetes
            
        Returns:
            numpy array con features normalizadas
        """
        if not packet_batch:
            return None
            
        features = []
        
        for packet in packet_batch:
            # Características numéricas
            size = packet.get('size', 0)
            src_port = packet.get('src_port', 0) or 0
            dst_port = packet.get('dst_port', 0) or 0
            ttl = packet.get('ttl', 64) or 64
            
            # Indicadores de protocolo
            is_tcp = 1 if packet.get('protocol') == 'TCP' else 0
            is_udp = 1 if packet.get('protocol') == 'UDP' else 0
            is_icmp = 1 if packet.get('protocol') == 'ICMP' else 0
            
            # Indicadores de flags TCP (posible actividad maliciosa)
            has_syn = 1 if packet.get('flags') and 'S' in str(packet.get('flags', '')) else 0
            has_fin = 1 if packet.get('flags') and 'F' in str(packet.get('flags', '')) else 0
            has_rst = 1 if packet.get('flags') and 'R' in str(packet.get('flags', '')) else 0
            
            # DNS query (posible anomalía)
            has_dns = 1 if packet.get('dns_query') else 0
            
            feature_vector = [
                size,
                src_port,
                dst_port,
                ttl,
                is_tcp,
                is_udp,
                is_icmp,
                has_syn,
                has_fin,
                has_rst,
                has_dns
            ]
            
            features.append(feature_vector)
            
        return np.array(features)
        
    def detect_statistical_anomalies(self, packet_batch):
        """
        Detecta anomalías basadas en estadísticas
        
        Args:
            packet_batch: Lista de paquetes
            
        Returns:
            Lista de índices de anomalías detectadas
        """
        if len(packet_batch) < 5:
            return []
            
        # Analizar tamaños de paquete
        sizes = [p.get('size', 0) for p in packet_batch]
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        
        # Analizar puertos destino
        dst_ports = [p.get('dst_port', 0) for p in packet_batch if p.get('dst_port')]
        
        anomalies = []
        threshold = mean_size + (3 * std_size)  # 3 desviaciones estándar
        
        for idx, packet in enumerate(packet_batch):
            size = packet.get('size', 0)
            
            # Anomalía por tamaño
            if size > threshold:
                anomalies.append({
                    'index': idx,
                    'type': 'size_anomaly',
                    'reason': f'Tamaño anormal: {size} bytes'
                })
                
            # Anomalía por puerto (escaneo de puertos)
            if len(set(dst_ports)) > len(dst_ports) * 0.8:
                anomalies.append({
                    'index': idx,
                    'type': 'port_scan',
                    'reason': 'Posible escaneo de puertos'
                })
                break
                
            # Anomalía por ICMP excesivo
            if packet.get('protocol') == 'ICMP':
                icmp_count = sum(1 for p in packet_batch if p.get('protocol') == 'ICMP')
                if icmp_count > len(packet_batch) * 0.3:
                    anomalies.append({
                        'index': idx,
                        'type': 'icmp_flood',
                        'reason': f'Posible flood de ICMP ({icmp_count} paquetes)'
                    })
                    break
                    
            # Anomalía por TCP SYN (posible SYN flood)
            if packet.get('flags') and 'S' in str(packet.get('flags', '')):
                syn_count = sum(1 for p in packet_batch if p.get('flags') and 'S' in str(p.get('flags', '')))
                if syn_count > len(packet_batch) * 0.5:
                    anomalies.append({
                        'index': idx,
                        'type': 'syn_flood',
                        'reason': f'Posible SYN flood ({syn_count} paquetes)'
                    })
                    break
                    
        return anomalies
        
    def detect_machine_learning_anomalies(self, packet_batch):
        """
        Detecta anomalías usando Isolation Forest
        
        Args:
            packet_batch: Lista de paquetes
            
        Returns:
            Array de predicciones (-1 para anomalías, 1 para normal)
        """
        features = self.extract_features(packet_batch)
        
        if features is None or len(features) < self.contamination * 100:
            return np.ones(len(packet_batch))
            
        try:
            # Normalizar features
            features_scaled = self.scaler.fit_transform(features)
            
            # Predecir anomalías
            predictions = self.isolation_forest.fit_predict(features_scaled)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error en detección ML: {e}")
            return np.ones(len(packet_batch))
            
    def analyze_packet_batch(self, packet_batch):
        """
        Análisis completo de un lote de paquetes
        
        Args:
            packet_batch: Lista de paquetes a analizar
            
        Returns:
            Diccionario con resultados del análisis
        """
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'total_packets': len(packet_batch),
            'statistical_anomalies': [],
            'ml_anomalies': [],
            'anomaly_score': 0.0,
            'severity': 'LOW',
            'recommendations': []
        }
        
        if not packet_batch:
            return analysis_result
            
        # Detección estadística
        stat_anomalies = self.detect_statistical_anomalies(packet_batch)
        analysis_result['statistical_anomalies'] = stat_anomalies
        
        # Detección ML
        ml_predictions = self.detect_machine_learning_anomalies(packet_batch)
        anomaly_indices = np.where(ml_predictions == -1)[0]
        analysis_result['ml_anomalies'] = anomaly_indices.tolist()
        
        # Calcular score de anomalía
        total_anomalies = len(stat_anomalies) + len(anomaly_indices)
        analysis_result['anomaly_score'] = total_anomalies / len(packet_batch) if packet_batch else 0
        
        # Determinar severidad
        if analysis_result['anomaly_score'] > 0.5:
            analysis_result['severity'] = 'CRITICAL'
            analysis_result['recommendations'] = [
                'Investigar inmediatamente',
                'Revisar logs de red',
                'Considerar aislamiento de hosts'
            ]
        elif analysis_result['anomaly_score'] > 0.3:
            analysis_result['severity'] = 'HIGH'
            analysis_result['recommendations'] = [
                'Monitorear de cerca',
                'Revisar patrones de tráfico'
            ]
        elif analysis_result['anomaly_score'] > 0.1:
            analysis_result['severity'] = 'MEDIUM'
            analysis_result['recommendations'] = [
                'Mantener vigilancia'
            ]
        else:
            analysis_result['severity'] = 'LOW'
            
        return analysis_result
        
    def update_history(self, packet):
        """Actualiza el historial de características"""
        features = self.extract_features([packet])
        if features is not None and len(features) > 0:
            self.feature_history.append(features[0])


class TrafficPattern:
    """Analiza patrones de tráfico de red"""
    
    def __init__(self, window_minutes=5):
        """
        Inicializa el analizador de patrones
        
        Args:
            window_minutes: Ventana de tiempo para análisis en minutos
        """
        self.window_minutes = window_minutes
        self.traffic_history = deque()
        self.flow_stats = {}
        
    def add_packet(self, packet):
        """Añade un paquete al historial"""
        packet['timestamp'] = datetime.now()
        self.traffic_history.append(packet)
        
        # Limpiar paquetes antiguos
        cutoff_time = datetime.now() - timedelta(minutes=self.window_minutes)
        while self.traffic_history and self.traffic_history[0]['timestamp'] < cutoff_time:
            self.traffic_history.popleft()
            
    def get_flow_statistics(self):
        """
        Obtiene estadísticas de flujos de red
        
        Returns:
            Diccionario con estadísticas de flujos
        """
        flows = {}
        
        for packet in self.traffic_history:
            if packet.get('src_ip') and packet.get('dst_ip'):
                flow_key = f"{packet['src_ip']}->{packet['dst_ip']}"
                
                if flow_key not in flows:
                    flows[flow_key] = {
                        'src_ip': packet['src_ip'],
                        'dst_ip': packet['dst_ip'],
                        'packets': 0,
                        'bytes': 0,
                        'protocols': set(),
                        'ports': set(),
                        'start_time': packet['timestamp']
                    }
                    
                flows[flow_key]['packets'] += 1
                flows[flow_key]['bytes'] += packet.get('size', 0)
                if packet.get('protocol'):
                    flows[flow_key]['protocols'].add(packet['protocol'])
                if packet.get('dst_port'):
                    flows[flow_key]['ports'].add(packet['dst_port'])
                    
        # Convertir sets a listas para serialización
        for flow in flows.values():
            flow['protocols'] = list(flow['protocols'])
            flow['ports'] = list(flow['ports'])
            
        return flows
