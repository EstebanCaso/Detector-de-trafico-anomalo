import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import './Charts.css';

function Charts({ stats }) {
  // Datos simulados para gráficos (en producción vendrían del backend)
  const packetData = [
    { time: 'T-5m', packets: 4000, bytes: 2400 },
    { time: 'T-4m', packets: 3000, bytes: 1398 },
    { time: 'T-3m', packets: 2000, bytes: 9800 },
    { time: 'T-2m', packets: 2780, bytes: 3908 },
    { time: 'T-1m', packets: 1890, bytes: 4800 },
    { time: 'Now', packets: stats.total_packets % 10000, bytes: (stats.total_bytes / 1024) % 10000 }
  ];

  const protocolData = [
    { name: 'TCP', value: 45, color: '#3b82f6' },
    { name: 'UDP', value: 30, color: '#16c784' },
    { name: 'ICMP', value: 15, color: '#fbbf24' },
    { name: 'Otros', value: 10, color: '#64748b' }
  ];

  const anomalyData = [
    { name: 'Normal', value: 85, color: '#16c784' },
    { name: 'Sospechoso', value: 10, color: '#fbbf24' },
    { name: 'Anómalo', value: 5, color: '#ef4444' }
  ];

  return (
    <div className="charts-container">
      <div className="chart-card">
        <h3>Tráfico en Tiempo Real</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={packetData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.3)" />
            <XAxis dataKey="time" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #16c784',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="packets"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6' }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="bytes"
              stroke="#16c784"
              strokeWidth={2}
              dot={{ fill: '#16c784' }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>Distribución de Protocolos</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={protocolData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {protocolData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #16c784',
                borderRadius: '8px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>Estado de Anomalías</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={anomalyData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {anomalyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #16c784',
                borderRadius: '8px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>Top 5 Puertos más Usados</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={[
              { port: '80', packets: 4000 },
              { port: '443', packets: 3000 },
              { port: '22', packets: 2000 },
              { port: '53', packets: 2780 },
              { port: '3306', packets: 1890 }
            ]}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.3)" />
            <XAxis dataKey="port" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #16c784',
                borderRadius: '8px'
              }}
            />
            <Bar dataKey="packets" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Charts;
