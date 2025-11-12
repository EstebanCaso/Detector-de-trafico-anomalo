import React from 'react';
import { GitBranch, Wifi } from 'lucide-react';
import './FlowsPanel.css';

function FlowsPanel({ flows }) {
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const sortedFlows = Object.entries(flows)
    .sort((a, b) => b[1].packets - a[1].packets)
    .slice(0, 50);

  return (
    <div className="flows-panel">
      {sortedFlows.length === 0 ? (
        <div className="empty-state">
          <GitBranch size={48} />
          <h3>No hay flujos de red</h3>
          <p>Los flujos de red aparecerán aquí cuando se capturen paquetes</p>
        </div>
      ) : (
        <div className="flows-container">
          <div className="flows-stats">
            <div className="stat">
              <span className="label">Total de Flujos</span>
              <span className="value">{sortedFlows.length}</span>
            </div>
            <div className="stat">
              <span className="label">Flujos Activos</span>
              <span className="value">{sortedFlows.filter(f => f[1].packets > 10).length}</span>
            </div>
          </div>

          <div className="flows-list">
            {sortedFlows.map(([flowKey, flow], index) => (
              <div key={index} className="flow-card">
                <div className="flow-header">
                  <div className="flow-source">
                    <code className="ip">{flow.src_ip}</code>
                    <span className="arrow">→</span>
                    <code className="ip">{flow.dst_ip}</code>
                  </div>
                  <div className="flow-stats">
                    <span className="stat-badge">
                      <Wifi size={14} />
                      {flow.packets} pkts
                    </span>
                    <span className="stat-badge">
                      {formatBytes(flow.bytes)}
                    </span>
                  </div>
                </div>

                <div className="flow-details">
                  <div className="detail-item">
                    <span className="label">Protocolos:</span>
                    <div className="protocols">
                      {flow.protocols && flow.protocols.map((proto, idx) => (
                        <span key={idx} className="protocol">{proto}</span>
                      ))}
                    </div>
                  </div>

                  <div className="detail-item">
                    <span className="label">Puertos:</span>
                    <div className="ports">
                      {flow.ports && flow.ports.slice(0, 5).map((port, idx) => (
                        <span key={idx} className="port">{port}</span>
                      ))}
                      {flow.ports && flow.ports.length > 5 && (
                        <span className="port-more">+{flow.ports.length - 5}</span>
                      )}
                    </div>
                  </div>

                  <div className="detail-item">
                    <span className="label">Inicio:</span>
                    <span className="time">
                      {new Date(flow.start_time).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                <div className="flow-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{
                        width: Math.min((flow.packets / 1000) * 100, 100) + '%'
                      }}
                    ></div>
                  </div>
                  <span className="progress-text">
                    {((flow.packets / 1000) * 100).toFixed(1)}% de actividad
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FlowsPanel;
