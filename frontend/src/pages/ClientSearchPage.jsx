import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CreditDecisionBox from '../components/CreditDecisionBox';
import RiskBadge from '../components/RiskBadge';

export default function ClientSearchPage() {
  const [clientId, setClientId] = useState('');
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!clientId.trim()) return;

    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/clients/${clientId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setClient(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Клиент не найден');
      setClient(null);
    }
    
    setLoading(false);
  };

  return (
    <div className="search-page">
      <h2>Поиск клиента по ID</h2>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Введите ID клиента (например: 1)"
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Поиск...' : 'Поиск'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {client && (
        <>
          <div className="client-card-detailed">
            <h3>Информация о клиенте</h3>
            
            <div className="client-details">
              <div className="detail-row">
                <span className="detail-label">ID:</span>
                <span className="detail-value">{client.id}</span>
              </div>
              
              {client.target !== null && client.target !== undefined && (
                <div className="detail-row">
                  <span className="detail-label">Target:</span>
                  <span className="detail-value">{client.target.toLocaleString()} ₽</span>
                </div>
              )}
              
              {client.incomeValue !== null && client.incomeValue !== undefined && (
                <div className="detail-row highlight">
                  <span className="detail-label">Доход:</span>
                  <span className="detail-value">{client.incomeValue.toLocaleString()} ₽</span>
                </div>
              )}
              
              {client.avg_cur_cr_turn !== null && client.avg_cur_cr_turn !== undefined && (
                <div className="detail-row">
                  <span className="detail-label">Средний кредитовый оборот:</span>
                  <span className="detail-value">{client.avg_cur_cr_turn.toLocaleString()} ₽</span>
                </div>
              )}
              
              {client.ovrd_sum !== null && client.ovrd_sum !== undefined && (
                <div className="detail-row">
                  <span className="detail-label">Сумма просрочки:</span>
                  <span className="detail-value">{client.ovrd_sum.toLocaleString()} ₽</span>
                </div>
              )}
              
              {client.loan_cur_amt !== null && client.loan_cur_amt !== undefined && (
                <div className="detail-row highlight">
                  <span className="detail-label">Запрашиваемая сумма кредита:</span>
                  <span className="detail-value">{client.loan_cur_amt.toLocaleString()} ₽</span>
                </div>
              )}
              
              {client.hdb_income_ratio !== null && client.hdb_income_ratio !== undefined && (
                <div className="detail-row">
                  <span className="detail-label">HDB Income Ratio:</span>
                  <span className="detail-value">{client.hdb_income_ratio.toFixed(4)}</span>
                </div>
              )}
              
              {client.risk_level && (
                <div className="detail-row">
                  <span className="detail-label">Уровень риска:</span>
                  <span className="detail-value">
                    <RiskBadge riskLevel={client.risk_level} />
                  </span>
                </div>
              )}
            </div>
          </div>
          
          <CreditDecisionBox client={client} />
        </>
      )}
    </div>
  );
}
