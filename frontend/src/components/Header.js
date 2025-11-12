import React from 'react';
import { Activity, Wifi, AlertTriangle, Zap } from 'lucide-react';
import './Header.css';

function Header({ isConnected, isCapturing, onStartCapture, onStopCapture }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <Activity size={32} />
            <h1>Traffic Anomaly Detector</h1>
          </div>
          <p className="subtitle">Monitoreo de tráfico anómalo en tiempo real</p>
        </div>

        <div className="header-right">
          <div className="status-indicators">
            <div className={`status-item ${isConnected ? 'connected' : 'disconnected'}`}>
              <div className="status-dot"></div>
              <span>{isConnected ? 'Conectado' : 'Desconectado'}</span>
            </div>

            <div className={`status-item ${isCapturing ? 'capturing' : ''}`}>
              <Wifi size={18} />
              <span>{isCapturing ? 'Capturando' : 'No capturando'}</span>
            </div>
          </div>

          <div className="control-buttons">
            {!isCapturing ? (
              <button 
                className="btn btn-start"
                onClick={onStartCapture}
              >
                <Zap size={18} />
                Iniciar Captura
              </button>
            ) : (
              <button 
                className="btn btn-stop"
                onClick={onStopCapture}
              >
                <AlertTriangle size={18} />
                Detener Captura
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
