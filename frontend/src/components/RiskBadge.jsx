import React from 'react';

export default function RiskBadge({ riskLevel }) {
  const getRiskStyle = (level) => {
    switch (level) {
      case 'LOW':
        return {
          backgroundColor: '#22C55E',
          color: '#FFFFFF'
        };
      case 'MEDIUM':
        return {
          backgroundColor: '#F59E0B',
          color: '#FFFFFF'
        };
      case 'HIGH':
        return {
          backgroundColor: '#EF4444',
          color: '#FFFFFF'
        };
      default:
        return {
          backgroundColor: '#666666',
          color: '#FFFFFF'
        };
    }
  };

  const getRiskLabel = (level) => {
    switch (level) {
      case 'LOW':
        return 'НИЗКИЙ';
      case 'MEDIUM':
        return 'СРЕДНИЙ';
      case 'HIGH':
        return 'ВЫСОКИЙ';
      default:
        return level || 'НЕИЗВЕСТНО';
    }
  };

  if (!riskLevel) return null;

  return (
    <span 
      className="risk-badge"
      style={getRiskStyle(riskLevel)}
    >
      {getRiskLabel(riskLevel)}
    </span>
  );
}

