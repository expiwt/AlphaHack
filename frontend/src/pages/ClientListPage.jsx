import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ClientListPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('income_predicted');
  const [order, setOrder] = useState('desc');

  useEffect(() => {
    fetchClients();
  }, [sortBy, order]);

  const fetchClients = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/clients?sort=${sortBy}&order=${order}&limit=50`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setClients(response.data.items);
    } catch (error) {
      alert('Ошибка загрузки клиентов');
    }
    setLoading(false);
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="clients-list-page">
      <h2>Список клиентов</h2>
      
      <div className="sort-controls">
        <label>
          Сортировать по:
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="income_predicted">Прогнозу дохода</option>
            <option value="income_real">Реальному доходу</option>
            <option value="age">Возрасту</option>
          </select>
        </label>
        
        <label>
          Порядок:
          <select value={order} onChange={(e) => setOrder(e.target.value)}>
            <option value="desc">↓ Убывающий</option>
            <option value="asc">↑ Возрастающий</option>
          </select>
        </label>
      </div>

      <table className="clients-table">
        <thead>
          <tr>
            <th>ID клиента</th>
            <th>Возраст</th>
            <th>Город</th>
            <th>Реальный доход</th>
            <th>Прогноз дохода</th>
            <th>Уверенность</th>
            <th>Категория</th>
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => (
            <tr key={client.client_id} className="client-row">
              <td className="client-id">{client.client_id}</td>
              <td>{client.age}</td>
              <td>{client.city}</td>
              <td className="income">
                {client.income_real ? client.income_real.toLocaleString() : '-'} ₽
              </td>
              <td className="income highlight">
                {client.income_predicted ? client.income_predicted.toLocaleString() : '-'} ₽
              </td>
              <td className="confidence">
                {client.confidence ? (client.confidence * 100).toFixed(1) : '-'}%
              </td>
              <td className="category">
                <span className={`badge badge-${client.income_category?.toLowerCase()}`}>
                  {client.income_category || '-'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {clients.length === 0 && (
        <div className="empty-state">
          <p>Нет данных о клиентах</p>
          <p>Сначала создайте тестовые данные через POST /api/v1/clients/seed/data</p>
        </div>
      )}
    </div>
  );
}
