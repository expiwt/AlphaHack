import React from 'react';
import RiskBadge from './RiskBadge';

export default function CreditDecisionBox({ client }) {
  if (!client) return null;

  const isApproved = client.recommendation === 'APPROVE';
  const recommendation = client.recommendation || 'REVIEW';
  const riskLevel = client.risk_level || 'MEDIUM';
  const reasoning = client.reasoning || 'Решение основано на анализе финансовых показателей клиента';

  const getDecisionStyle = () => {
    if (isApproved) {
      return {
        backgroundColor: '#22C55E',
        color: '#FFFFFF',
        borderColor: '#16A34A'
      };
    } else {
      return {
        backgroundColor: '#EF4444',
        color: '#FFFFFF',
        borderColor: '#DC2626'
      };
    }
  };

  return (
    <div className="credit-decision-box" style={getDecisionStyle()}>
      <div className="decision-header">
        <h3>Решение по кредиту</h3>
        <div className="decision-status">
          {isApproved ? (
            <span className="decision-approve">ОДОБРЕНО</span>
          ) : (
            <span className="decision-reject">ОТКЛОНЕНО</span>
          )}
        </div>
      </div>
      
      <div className="decision-details">
        <div className="decision-item">
          <span className="decision-label">Рекомендация:</span>
          <span className="decision-value">{recommendation}</span>
        </div>
        
        <div className="decision-item">
          <span className="decision-label">Уровень риска:</span>
          <RiskBadge riskLevel={riskLevel} />
        </div>
        
        {client.incomeValue && client.ovrd_sum !== null && client.ovrd_sum !== undefined && (
          <div className="decision-item">
            <span className="decision-label">Долговая нагрузка:</span>
            <span className="decision-value">{((client.ovrd_sum / client.incomeValue) * 100).toFixed(1)}%</span>
          </div>
        )}
        
        {client.ovrd_sum !== null && client.ovrd_sum !== undefined && (
          <div className="decision-item">
            <span className="decision-label">Сумма просрочки:</span>
            <span className="decision-value">{client.ovrd_sum.toLocaleString()} ₽</span>
          </div>
        )}
        
        {client.loan_cur_amt !== null && client.loan_cur_amt !== undefined && (
          <div className="decision-item">
            <span className="decision-label">Запрашиваемая сумма:</span>
            <span className="decision-value">{client.loan_cur_amt.toLocaleString()} ₽</span>
          </div>
        )}
      </div>
      
      <div className="decision-reasoning">
        <p>{reasoning}</p>
      </div>
    </div>
  );
}

