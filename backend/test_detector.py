"""
Pruebas unitarias para los módulos principales
"""

import unittest
from datetime import datetime
from anomaly_detector import AnomalyDetector, TrafficPattern
import numpy as np


class TestAnomalyDetector(unittest.TestCase):
    """Pruebas para el detector de anomalías"""
    
    def setUp(self):
        """Configuración previa a cada prueba"""
        self.detector = AnomalyDetector()
        
    def test_extract_features(self):
        """Prueba extracción de características"""
        packets = [
            {
                'size': 100,
                'src_port': 1234,
                'dst_port': 443,
                'ttl': 64,
                'protocol': 'TCP',
                'flags': 'S',
                'dns_query': None
            }
        ]
        
        features = self.detector.extract_features(packets)
        
        self.assertIsNotNone(features)
        self.assertEqual(len(features), 1)
        self.assertEqual(len(features[0]), 11)  # 11 features
        
    def test_statistical_anomalies(self):
        """Prueba detección estadística de anomalías"""
        # Crear lote con un paquete anormal
        packets = [
            {'size': 100, 'protocol': 'TCP', 'dst_port': 80, 'flags': '', 'ttl': 64}
            for _ in range(10)
        ]
        packets.append({
            'size': 10000,  # Anormalmente grande
            'protocol': 'TCP',
            'dst_port': 80,
            'flags': '',
            'ttl': 64
        })
        
        anomalies = self.detector.detect_statistical_anomalies(packets)
        
        self.assertGreater(len(anomalies), 0)
        
    def test_ml_anomalies(self):
        """Prueba detección ML de anomalías"""
        packets = [
            {
                'size': 100,
                'src_port': 1234 + i,
                'dst_port': 80,
                'protocol': 'TCP',
                'flags': '',
                'ttl': 64,
                'dns_query': None
            }
            for i in range(50)
        ]
        
        predictions = self.detector.detect_machine_learning_anomalies(packets)
        
        self.assertEqual(len(predictions), 50)
        self.assertTrue(all(p in [-1, 1] for p in predictions))
        
    def test_batch_analysis(self):
        """Prueba análisis de lote completo"""
        packets = [
            {
                'size': 100 + i,
                'src_port': 1234,
                'dst_port': 80,
                'src_ip': '192.168.1.100',
                'dst_ip': '8.8.8.8',
                'protocol': 'TCP',
                'flags': '',
                'ttl': 64,
                'dns_query': None
            }
            for i in range(30)
        ]
        
        result = self.detector.analyze_packet_batch(packets)
        
        self.assertIn('timestamp', result)
        self.assertIn('total_packets', result)
        self.assertIn('anomaly_score', result)
        self.assertIn('severity', result)
        self.assertEqual(result['total_packets'], 30)
        

class TestTrafficPattern(unittest.TestCase):
    """Pruebas para análisis de patrones de tráfico"""
    
    def setUp(self):
        """Configuración previa a cada prueba"""
        self.pattern = TrafficPattern(window_minutes=5)
        
    def test_add_packet(self):
        """Prueba agregar paquetes"""
        packet = {
            'src_ip': '192.168.1.100',
            'dst_ip': '8.8.8.8',
            'protocol': 'TCP',
            'dst_port': 443,
            'size': 100
        }
        
        self.pattern.add_packet(packet)
        
        self.assertEqual(len(self.pattern.traffic_history), 1)
        
    def test_flow_statistics(self):
        """Prueba estadísticas de flujos"""
        packets = [
            {
                'src_ip': '192.168.1.100',
                'dst_ip': '8.8.8.8',
                'protocol': 'TCP',
                'dst_port': 443,
                'size': 100
            },
            {
                'src_ip': '192.168.1.100',
                'dst_ip': '8.8.8.8',
                'protocol': 'TCP',
                'dst_port': 443,
                'size': 100
            }
        ]
        
        for packet in packets:
            self.pattern.add_packet(packet)
            
        flows = self.pattern.get_flow_statistics()
        
        self.assertGreater(len(flows), 0)
        
        flow_key = '192.168.1.100->8.8.8.8'
        self.assertIn(flow_key, flows)
        self.assertEqual(flows[flow_key]['packets'], 2)
        self.assertEqual(flows[flow_key]['bytes'], 200)


class TestEdgeCases(unittest.TestCase):
    """Pruebas de casos edge"""
    
    def setUp(self):
        self.detector = AnomalyDetector()
        
    def test_empty_batch(self):
        """Prueba lote vacío"""
        result = self.detector.analyze_packet_batch([])
        
        self.assertEqual(result['total_packets'], 0)
        self.assertEqual(result['anomaly_score'], 0.0)
        
    def test_single_packet(self):
        """Prueba único paquete"""
        packets = [{
            'size': 100,
            'src_port': 1234,
            'dst_port': 443,
            'protocol': 'TCP',
            'flags': '',
            'ttl': 64,
            'dns_query': None
        }]
        
        result = self.detector.analyze_packet_batch(packets)
        
        self.assertEqual(result['total_packets'], 1)
        
    def test_missing_fields(self):
        """Prueba paquetes con campos faltantes"""
        packets = [
            {'size': 100},  # Solo tamaño
            {'protocol': 'TCP'},  # Solo protocolo
            {}  # Vacío
        ]
        
        # No debe lanzar excepción
        result = self.detector.analyze_packet_batch(packets)
        
        self.assertEqual(result['total_packets'], 3)


def run_tests():
    """Ejecuta todas las pruebas"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
