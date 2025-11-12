import React from 'react';
import { Package, GitBranch, Wifi } from 'lucide-react';
import './PacketsPanel.css';

function PacketsPanel({ packets }) {
  const getProtocolColor = (protocol) => {
    const colors = {
      'TCP': '#3b82f6',
      'UDP': '#16c784',
      'ICMP': '#fbbf24',
      'IPv6': '#a78bfa',
      'DNS': '#f472b6'
    };
    return colors[protocol] || '#64748b';
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="packets-panel">
      {packets.length === 0 ? (
        <div className="empty-state">
          <Package size={48} />
          <h3>No hay paquetes capturados</h3>
          <p>Inicia la captura para ver paquetes en tiempo real</p>
        </div>
      ) : (
        <div className="packets-table">
          <div className="table-header">
            <div className="col col-time">Timestamp</div>
            <div className="col col-protocol">Protocolo</div>
            <div className="col col-src">IP Origen</div>
            <div className="col col-dst">IP Destino</div>
            <div className="col col-ports">Puertos</div>
            <div className="col col-size">Tamaño</div>
          </div>

          <div className="table-body">
            {packets.map((packet, index) => (
              <div key={index} className="table-row">
                <div className="col col-time">
                  <span className="timestamp">
                    {new Date(packet.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="col col-protocol">
                  <span 
                    className="protocol-badge"
                    style={{ borderColor: getProtocolColor(packet.protocol) }}
                  >
                    {packet.protocol || 'N/A'}
                  </span>
                </div>

                <div className="col col-src">
                  <code>{packet.src_ip || '-'}</code>
                </div>

                <div className="col col-dst">
                  <code>{packet.dst_ip || '-'}</code>
                </div>

                <div className="col col-ports">
                  <span className="port">
                    {packet.src_port || '-'}
                  </span>
                  <span className="arrow">→</span>
                  <span className="port">
                    {packet.dst_port || '-'}
                  </span>
                </div>

                <div className="col col-size">
                  {formatBytes(packet.size)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default PacketsPanel;
