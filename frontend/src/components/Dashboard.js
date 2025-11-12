import React, { useState } from 'react';
import StatCard from './StatCard';
import AnomaliesPanel from './AnomaliesPanel';
import PacketsPanel from './PacketsPanel';
import FlowsPanel from './FlowsPanel';
import Charts from './Charts';
import './Dashboard.css';

function Dashboard({ stats, anomalies, recentPackets, flows }) {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="dashboard">
      <div className="dashboard-container">
        {/* Estadísticas principales */}
        <div className="stats-grid">
          <StatCard
            title="Total de Paquetes"
            value={stats.total_packets}
            unit="pkts"
            icon="📦"
            trend="+5.2%"
            color="blue"
          />
          <StatCard
            title="Tráfico"
            value={(stats.total_bytes / (1024 * 1024)).toFixed(2)}
            unit="MB"
            icon="📊"
            trend="+3.1%"
            color="green"
          />
          <StatCard
            title="Velocidad"
            value={stats.packets_per_second.toFixed(2)}
            unit="pps"
            icon="⚡"
            trend="En tiempo real"
            color="yellow"
          />
          <StatCard
            title="Anomalías Detectadas"
            value={stats.anomalies_detected}
            unit="alertas"
            icon="⚠️"
            trend={stats.anomalies_detected > 0 ? '⚠️ Crítico' : 'Normal'}
            color={stats.anomalies_detected > 0 ? "red" : "green"}
          />
        </div>

        {/* Navegación de pestañas */}
        <div className="tabs-navigation">
          <button
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📈 Resumen
          </button>
          <button
            className={`tab-btn ${activeTab === 'anomalies' ? 'active' : ''}`}
            onClick={() => setActiveTab('anomalies')}
          >
            ⚠️ Anomalías ({anomalies.length})
          </button>
          <button
            className={`tab-btn ${activeTab === 'packets' ? 'active' : ''}`}
            onClick={() => setActiveTab('packets')}
          >
            📦 Paquetes
          </button>
          <button
            className={`tab-btn ${activeTab === 'flows' ? 'active' : ''}`}
            onClick={() => setActiveTab('flows')}
          >
            🔗 Flujos
          </button>
        </div>

        {/* Contenido dinámico */}
        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-section">
              <Charts stats={stats} />
            </div>
          )}

          {activeTab === 'anomalies' && (
            <AnomaliesPanel anomalies={anomalies} />
          )}

          {activeTab === 'packets' && (
            <PacketsPanel packets={recentPackets} />
          )}

          {activeTab === 'flows' && (
            <FlowsPanel flows={flows} />
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
