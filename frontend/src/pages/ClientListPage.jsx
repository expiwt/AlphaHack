import React, { useState, useEffect } from 'react';
import axios from 'axios';
import RiskBadge from '../components/RiskBadge';

export default function ClientListPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('incomeValue');
  const [order, setOrder] = useState('desc');
  const [riskFilter, setRiskFilter] = useState('');

  useEffect(() => {
    fetchClients();
  }, [sortBy, order, riskFilter]);

  const fetchClients = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      let url = `${import.meta.env.VITE_API_URL}/clients?sort=${sortBy}&order=${order}&limit=50`;
      
      if (riskFilter) url += `&risk_level=${riskFilter}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
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
            <option value="incomeValue">Доходу</option>
            <option value="target">Целевому значению</option>
            <option value="ovrd_sum">Сумме просрочки</option>
            <option value="loan_cur_amt">Сумме кредита</option>
            <option value="hdb_income_ratio">HDB Income Ratio</option>
          </select>
        </label>
        
        <label>
          Порядок:
          <select value={order} onChange={(e) => setOrder(e.target.value)}>
            <option value="desc">↓ Убывающий</option>
            <option value="asc">↑ Возрастающий</option>
          </select>
        </label>
        
        <label>
          Риск:
          <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
            <option value="">Все уровни</option>
            <option value="LOW">Низкий</option>
            <option value="MEDIUM">Средний</option>
            <option value="HIGH">Высокий</option>
          </select>
        </label>
      </div>

      <table className="clients-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Target</th>
            <th>Доход (₽)</th>
            <th>Кредитовый оборот (₽)</th>
            <th>Просрочка (₽)</th>
            <th>Сумма кредита (₽)</th>
            <th>HDB Income Ratio</th>
            <th>Решение</th>
            <th>Риск</th>
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => {
            return (
              <tr key={client.id} className="client-row">
                <td className="client-id">{client.id}</td>
                <td className="target">
                  {client.target ? client.target.toLocaleString() : '-'} ₽
                </td>
                <td className="income highlight">
                  {client.incomeValue ? client.incomeValue.toLocaleString() : '-'} ₽
                </td>
                <td className="turnover">
                  {client.avg_cur_cr_turn ? client.avg_cur_cr_turn.toLocaleString() : '-'} ₽
                </td>
                <td className="debt">
                  {client.ovrd_sum ? client.ovrd_sum.toLocaleString() : '-'} ₽
                </td>
                <td className="loan">
                  {client.loan_cur_amt ? client.loan_cur_amt.toLocaleString() : '-'} ₽
                </td>
                <td className="hdb-ratio">
                  {client.hdb_income_ratio !== null && client.hdb_income_ratio !== undefined
                    ? client.hdb_income_ratio.toFixed(4)
                    : '-'}
                </td>
                <td className="credit-decision">
                  {client.recommendation === 'APPROVE' ? (
                    <span className="decision-approve-badge">✓ ОДОБРЕНО</span>
                  ) : client.recommendation === 'REJECT' ? (
                    <span className="decision-reject-badge">✗ ОТКЛОНЕНО</span>
                  ) : (
                    <span className="decision-review-badge">? НА РАССМОТРЕНИИ</span>
                  )}
                </td>
                <td className="risk">
                  <RiskBadge riskLevel={client.risk_level} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {clients.length === 0 && (
        <div className="empty-state">
          <p>Нет данных о клиентах</p>
        </div>
      )}
    </div>
  );
}
