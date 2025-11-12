import React from 'react';
import { AlertTriangle, Clock, Globe, Zap } from 'lucide-react';
import './AnomaliesPanel.css';

function AnomaliesPanel({ anomalies }) {
  const getSeverityColor = (severity) => {
    const colors = {
      'CRITICAL': '#ef4444',
      'HIGH': '#f97316',
      'MEDIUM': '#fbbf24',
      'LOW': '#16c784'
    };
    return colors[severity] || '#64748b';
  };

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'CRITICAL': return '🔴';
      case 'HIGH': return '🟠';
      case 'MEDIUM': return '🟡';
      case 'LOW': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div className="anomalies-panel">
      {anomalies.length === 0 ? (
        <div className="empty-state">
          <AlertTriangle size={48} />
          <h3>No hay anomalías detectadas</h3>
          <p>El tráfico parece normal en este momento</p>
        </div>
      ) : (
        <div className="anomalies-list">
          {anomalies.map((anomaly, index) => (
            <div key={index} className="anomaly-item" style={{
              borderLeftColor: getSeverityColor(anomaly.severity)
            }}>
              <div className="anomaly-header">
                <div className="anomaly-title">
                  <span className="severity-icon">{getSeverityIcon(anomaly.severity)}</span>
                  <h4>{anomaly.type || 'Anomalía detectada'}</h4>
                  <span className="severity-badge" style={{
                    backgroundColor: getSeverityColor(anomaly.severity) + '20',
                    color: getSeverityColor(anomaly.severity),
                    borderColor: getSeverityColor(anomaly.severity)
                  }}>
                    {anomaly.severity}
                  </span>
                </div>
                <span className="anomaly-score">
                  Score: {(anomaly.anomaly_score * 100).toFixed(1)}%
                </span>
              </div>

              <div className="anomaly-details">
                {anomaly.details && anomaly.details.recommendations && (
                  <div className="recommendations">
                    <strong>Recomendaciones:</strong>
                    <ul>
                      {anomaly.details.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="anomaly-meta">
                  <div className="meta-item">
                    <Clock size={16} />
                    <span>{new Date(anomaly.timestamp).toLocaleString()}</span>
                  </div>
                  {anomaly.src_ip && (
                    <div className="meta-item">
                      <Globe size={16} />
                      <span>{anomaly.src_ip} → {anomaly.dst_ip || 'N/A'}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AnomaliesPanel;
