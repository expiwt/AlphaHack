import React, { useState, useEffect } from 'react';
import axios from 'axios';

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
          placeholder="Введите ID клиента (например: cli_test_001)"
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
        <div className="client-card-detailed">
          <h3>Информация о клиенте</h3>
          
          <div className="client-details">
            <div className="detail-row">
              <span className="detail-label">ID:</span>
              <span className="detail-value">{client.client_id}</span>
            </div>
            
            <div className="detail-row">
              <span className="detail-label">Возраст:</span>
              <span className="detail-value">{client.age} лет</span>
            </div>
            
            <div className="detail-row">
              <span className="detail-label">Пол:</span>
              <span className="detail-value">{client.gender === 'M' ? 'Мужской' : 'Женский'}</span>
            </div>
            
            <div className="detail-row">
              <span className="detail-label">Город:</span>
              <span className="detail-value">{client.city}</span>
            </div>
            
            <div className="detail-row">
              <span className="detail-label">Регион:</span>
              <span className="detail-value">{client.region}</span>
            </div>
            
            {client.income_real && (
              <div className="detail-row highlight">
                <span className="detail-label">Реальный доход:</span>
                <span className="detail-value">{client.income_real.toLocaleString()} ₽</span>
              </div>
            )}
            
            {client.income_predicted && (
              <div className="detail-row highlight">
                <span className="detail-label">Прогноз дохода:</span>
                <span className="detail-value">{client.income_predicted.toLocaleString()} ₽</span>
              </div>
            )}
            
            {client.confidence && (
              <div className="detail-row">
                <span className="detail-label">Уверенность:</span>
                <span className="detail-value">{(client.confidence * 100).toFixed(1)}%</span>
              </div>
            )}
            
            {client.income_category && (
              <div className="detail-row">
                <span className="detail-label">Категория:</span>
                <span className="detail-value">{client.income_category}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
