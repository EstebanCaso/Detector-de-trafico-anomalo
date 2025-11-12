import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [stats, setStats] = useState({
    total_packets: 0,
    total_bytes: 0,
    packets_per_second: 0,
    anomalies_detected: 0,
    buffer_size: 0
  });
  const [anomalies, setAnomalies] = useState([]);
  const [recentPackets, setRecentPackets] = useState([]);
  const [flows, setFlows] = useState({});

  useEffect(() => {
    // Conectar WebSocket
    const newSocket = io(API_BASE_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    newSocket.on('connect', () => {
      console.log('Conectado al servidor');
      setIsConnected(true);
      newSocket.emit('subscribe_stats');
      newSocket.emit('subscribe_anomalies');
    });

    newSocket.on('disconnect', () => {
      console.log('Desconectado del servidor');
      setIsConnected(false);
    });

    newSocket.on('stats_update', (data) => {
      setStats(data);
    });

    newSocket.on('anomaly_detected', (data) => {
      setAnomalies(prev => [data, ...prev].slice(0, 100));
    });

    newSocket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, []);

  // Obtener datos iniciales
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Obtener paquetes recientes
      const packetsRes = await axios.get(`${API_BASE_URL}/api/packets?limit=50`);
      setRecentPackets(packetsRes.data);

      // Obtener flujos
      const flowsRes = await axios.get(`${API_BASE_URL}/api/flows`);
      setFlows(flowsRes.data);

      // Obtener anomalías
      const anomaliesRes = await axios.get(`${API_BASE_URL}/api/anomalies?limit=100`);
      if (anomaliesRes.data.length > anomalies.length) {
        setAnomalies(anomaliesRes.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const startCapture = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/capture/start`, {
        interface: 'eth0'
      }, {
        auth: {
          username: 'admin',
          password: 'admin'
        }
      });
      setIsCapturing(true);
    } catch (error) {
      console.error('Error starting capture:', error);
      alert('Error iniciando captura: ' + error.message);
    }
  };

  const stopCapture = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/capture/stop`, {}, {
        auth: {
          username: 'admin',
          password: 'admin'
        }
      });
      setIsCapturing(false);
    } catch (error) {
      console.error('Error stopping capture:', error);
      alert('Error deteniendo captura: ' + error.message);
    }
  };

  return (
    <div className="App">
      <Header 
        isConnected={isConnected}
        isCapturing={isCapturing}
        onStartCapture={startCapture}
        onStopCapture={stopCapture}
      />
      <Dashboard 
        stats={stats}
        anomalies={anomalies}
        recentPackets={recentPackets}
        flows={flows}
      />
    </div>
  );
}

export default App;
