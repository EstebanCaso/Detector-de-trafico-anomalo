"""
Utilidades para análisis de alertas y estadísticas
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics


class AlertAnalyzer:
    """Análisis de alertas detectadas"""
    
    def __init__(self, anomalies):
        """
        Inicializa el analizador
        
        Args:
            anomalies: Lista de anomalías detectadas
        """
        self.anomalies = anomalies
        
    def get_severity_distribution(self):
        """Obtiene distribución de severidades"""
        distribution = Counter()
        
        for anomaly in self.anomalies:
            severity = anomaly.get('severity', 'UNKNOWN')
            distribution[severity] += 1
            
        return dict(distribution)
        
    def get_anomaly_types(self):
        """Obtiene tipos de anomalías más frecuentes"""
        types = Counter()
        
        for anomaly in self.anomalies:
            atype = anomaly.get('type', 'unknown')
            types[atype] += 1
            
        return types.most_common(10)
        
    def get_timeline(self, bucket_minutes=5):
        """
        Agrupa anomalías en buckets de tiempo
        
        Args:
            bucket_minutes: Minutos por bucket
            
        Returns:
            Diccionario con timeline
        """
        timeline = defaultdict(int)
        
        for anomaly in self.anomalies:
            try:
                timestamp = datetime.fromisoformat(
                    anomaly.get('timestamp', '')
                )
                bucket = timestamp.replace(
                    minute=(timestamp.minute // bucket_minutes) * bucket_minutes
                )
                key = bucket.isoformat()
                timeline[key] += 1
            except:
                pass
                
        return dict(sorted(timeline.items()))
        
    def get_critical_alerts(self):
        """Obtiene solo alertas críticas"""
        return [
            a for a in self.anomalies 
            if a.get('severity') == 'CRITICAL'
        ]
        
    def generate_report(self):
        """Genera reporte de análisis"""
        total = len(self.anomalies)
        critical = len(self.get_critical_alerts())
        
        return {
            'total_anomalies': total,
            'critical_alerts': critical,
            'severity_distribution': self.get_severity_distribution(),
            'top_types': [
                {'type': t, 'count': c} for t, c in self.get_anomaly_types()
            ],
            'critical_percentage': (critical / total * 100) if total > 0 else 0,
            'report_time': datetime.now().isoformat()
        }


class PerformanceMetrics:
    """Métricas de rendimiento del detector"""
    
    def __init__(self):
        self.metrics = {
            'packets_processed': 0,
            'anomalies_detected': 0,
            'processing_time': 0.0,
            'detection_accuracy': 0.0
        }
        
    def calculate_pps(self, packets, elapsed_time):
        """Calcula paquetes por segundo"""
        return packets / elapsed_time if elapsed_time > 0 else 0
        
    def calculate_detection_rate(self, detected, total):
        """Calcula tasa de detección"""
        return (detected / total * 100) if total > 0 else 0
        
    def get_summary(self):
        """Obtiene resumen de métricas"""
        return {
            'packets_processed': self.metrics['packets_processed'],
            'anomalies_detected': self.metrics['anomalies_detected'],
            'detection_rate': self.calculate_detection_rate(
                self.metrics['anomalies_detected'],
                self.metrics['packets_processed']
            ),
            'processing_time_ms': self.metrics['processing_time'] * 1000
        }
