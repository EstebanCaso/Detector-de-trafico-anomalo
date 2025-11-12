"""
Gestor de base de datos para almacenar eventos y análisis
"""

import logging
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)


class DatabaseManager(ABC):
    """Clase base para gestión de base de datos"""
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def save_packet(self, packet_data):
        pass
    
    @abstractmethod
    def save_anomaly(self, anomaly_data):
        pass
    
    @abstractmethod
    def get_recent_anomalies(self, limit=100):
        pass
    
    @abstractmethod
    def get_statistics(self, hours=24):
        pass


class PostgreSQLManager(DatabaseManager):
    """Gestor de PostgreSQL para persistencia de datos"""
    
    def __init__(self, host, port, user, password, database):
        """Inicializa la conexión a PostgreSQL"""
        try:
            import psycopg2
            self.psycopg2 = psycopg2
        except ImportError:
            logger.error("psycopg2 no está instalado")
            raise
            
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Conecta a la base de datos PostgreSQL"""
        try:
            self.connection = self.psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            logger.info("Conectado a PostgreSQL")
            self._create_tables()
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise
            
    def disconnect(self):
        """Desconecta de la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Desconectado de PostgreSQL")
            
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS packets (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    src_ip VARCHAR(45),
                    dst_ip VARCHAR(45),
                    src_port INTEGER,
                    dst_port INTEGER,
                    protocol VARCHAR(10),
                    size INTEGER,
                    flags VARCHAR(20),
                    ttl INTEGER,
                    dns_query TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_timestamp ON packets(timestamp);
                CREATE INDEX IF NOT EXISTS idx_src_ip ON packets(src_ip);
                CREATE INDEX IF NOT EXISTS idx_dst_ip ON packets(dst_ip);
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    anomaly_type VARCHAR(50),
                    severity VARCHAR(20),
                    src_ip VARCHAR(45),
                    dst_ip VARCHAR(45),
                    anomaly_score FLOAT,
                    details TEXT,
                    status VARCHAR(20) DEFAULT 'NEW'
                );
                
                CREATE INDEX IF NOT EXISTS idx_anomaly_timestamp ON anomalies(timestamp);
                CREATE INDEX IF NOT EXISTS idx_anomaly_severity ON anomalies(severity);
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS traffic_summary (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    total_packets BIGINT,
                    total_bytes BIGINT,
                    protocol_stats TEXT,
                    top_ips TEXT,
                    alerts_count INTEGER
                );
                
                CREATE INDEX IF NOT EXISTS idx_summary_timestamp ON traffic_summary(timestamp);
            """)
            
            self.connection.commit()
            logger.info("Tablas creadas/verificadas")
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            
    def save_packet(self, packet_data):
        """Guarda un paquete en la base de datos"""
        try:
            self.cursor.execute("""
                INSERT INTO packets 
                (timestamp, src_ip, dst_ip, src_port, dst_port, protocol, size, flags, ttl, dns_query)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datetime.fromisoformat(packet_data['timestamp']),
                packet_data.get('src_ip'),
                packet_data.get('dst_ip'),
                packet_data.get('src_port'),
                packet_data.get('dst_port'),
                packet_data.get('protocol'),
                packet_data.get('size'),
                packet_data.get('flags'),
                packet_data.get('ttl'),
                packet_data.get('dns_query')
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error guardando paquete: {e}")
            
    def save_anomaly(self, anomaly_data):
        """Guarda una anomalía detectada"""
        try:
            self.cursor.execute("""
                INSERT INTO anomalies 
                (timestamp, anomaly_type, severity, src_ip, dst_ip, anomaly_score, details)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                anomaly_data.get('type', 'unknown'),
                anomaly_data.get('severity', 'LOW'),
                anomaly_data.get('src_ip'),
                anomaly_data.get('dst_ip'),
                anomaly_data.get('score', 0),
                json.dumps(anomaly_data)
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error guardando anomalía: {e}")
            
    def get_recent_anomalies(self, limit=100):
        """Obtiene anomalías recientes"""
        try:
            self.cursor.execute("""
                SELECT timestamp, anomaly_type, severity, src_ip, dst_ip, anomaly_score, details
                FROM anomalies
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            
            columns = [desc[0] for desc in self.cursor.description]
            anomalies = []
            
            for row in self.cursor.fetchall():
                anomalies.append(dict(zip(columns, row)))
                
            return anomalies
        except Exception as e:
            logger.error(f"Error obteniendo anomalías: {e}")
            return []
            
    def get_statistics(self, hours=24):
        """Obtiene estadísticas de tráfico de las últimas horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_packets,
                    SUM(size) as total_bytes,
                    protocol,
                    COUNT(DISTINCT src_ip) as unique_sources
                FROM packets
                WHERE timestamp > %s
                GROUP BY protocol
                ORDER BY total_packets DESC
            """, (cutoff_time,))
            
            columns = [desc[0] for desc in self.cursor.description]
            stats = []
            
            for row in self.cursor.fetchall():
                stats.append(dict(zip(columns, row)))
                
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return []


class MongoDBManager(DatabaseManager):
    """Gestor de MongoDB para almacenamiento flexible"""
    
    def __init__(self, uri, database):
        """Inicializa la conexión a MongoDB"""
        try:
            from pymongo import MongoClient
            self.MongoClient = MongoClient
        except ImportError:
            logger.error("pymongo no está instalado")
            raise
            
        self.uri = uri
        self.database_name = database
        self.client = None
        self.db = None
        
    def connect(self):
        """Conecta a MongoDB"""
        try:
            self.client = self.MongoClient(self.uri)
            self.db = self.client[self.database_name]
            
            # Crear índices
            self.db['packets'].create_index('timestamp')
            self.db['anomalies'].create_index('timestamp')
            self.db['anomalies'].create_index('severity')
            
            logger.info("Conectado a MongoDB")
        except Exception as e:
            logger.error(f"Error conectando a MongoDB: {e}")
            raise
            
    def disconnect(self):
        """Desconecta de MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Desconectado de MongoDB")
            
    def save_packet(self, packet_data):
        """Guarda un paquete en MongoDB"""
        try:
            packet_data['timestamp'] = datetime.fromisoformat(packet_data['timestamp'])
            self.db['packets'].insert_one(packet_data)
        except Exception as e:
            logger.error(f"Error guardando paquete en MongoDB: {e}")
            
    def save_anomaly(self, anomaly_data):
        """Guarda una anomalía en MongoDB"""
        try:
            anomaly_data['timestamp'] = datetime.now()
            self.db['anomalies'].insert_one(anomaly_data)
        except Exception as e:
            logger.error(f"Error guardando anomalía en MongoDB: {e}")
            
    def get_recent_anomalies(self, limit=100):
        """Obtiene anomalías recientes de MongoDB"""
        try:
            anomalies = list(self.db['anomalies'].find({}).sort('timestamp', -1).limit(limit))
            # Convertir ObjectId a string para serialización JSON
            for anomaly in anomalies:
                anomaly['_id'] = str(anomaly['_id'])
            return anomalies
        except Exception as e:
            logger.error(f"Error obteniendo anomalías de MongoDB: {e}")
            return []
            
    def get_statistics(self, hours=24):
        """Obtiene estadísticas de MongoDB"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            pipeline = [
                {'$match': {'timestamp': {'$gt': cutoff_time}}},
                {'$group': {
                    '_id': '$protocol',
                    'total_packets': {'$sum': 1},
                    'total_bytes': {'$sum': '$size'},
                    'unique_sources': {'$addToSet': '$src_ip'}
                }},
                {'$sort': {'total_packets': -1}}
            ]
            
            stats = list(self.db['packets'].aggregate(pipeline))
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de MongoDB: {e}")
            return []


class DatabaseFactory:
    """Factory para crear instancias de gestores de base de datos"""
    
    @staticmethod
    def create_manager(db_type, **kwargs):
        """
        Crea un gestor de base de datos
        
        Args:
            db_type: Tipo de base de datos ('postgresql' o 'mongodb')
            **kwargs: Parámetros específicos de la base de datos
            
        Returns:
            Instancia del gestor de base de datos
        """
        if db_type.lower() == 'postgresql':
            return PostgreSQLManager(
                host=kwargs.get('host', 'localhost'),
                port=kwargs.get('port', 5432),
                user=kwargs.get('user'),
                password=kwargs.get('password'),
                database=kwargs.get('database')
            )
        elif db_type.lower() == 'mongodb':
            return MongoDBManager(
                uri=kwargs.get('uri', 'mongodb://localhost:27017/'),
                database=kwargs.get('database')
            )
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {db_type}")
