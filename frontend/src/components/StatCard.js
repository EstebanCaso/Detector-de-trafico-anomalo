import React from 'react';
import './StatCard.css';

function StatCard({ title, value, unit, icon, trend, color }) {
  return (
    <div className={`stat-card stat-card-${color}`}>
      <div className="stat-header">
        <h3>{title}</h3>
        <span className="stat-icon">{icon}</span>
      </div>
      <div className="stat-value">
        <span className="value">{typeof value === 'number' ? value.toLocaleString() : value}</span>
        <span className="unit">{unit}</span>
      </div>
      <div className="stat-footer">
        <span className="trend">{trend}</span>
      </div>
    </div>
  );
}

export default StatCard;
