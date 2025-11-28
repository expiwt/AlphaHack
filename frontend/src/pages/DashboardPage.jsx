import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/dashboard`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setDashboard(response.data);
    } catch (error) {
      alert('Ошибка загрузки dashboard');
    }
    setLoading(false);
  };

  if (loading) return <div>Загрузка...</div>;
  if (!dashboard) return <div>Ошибка загрузки данных</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Система прогноза доходов Альфа-Банка</h1>
        <button onClick={() => {
          localStorage.removeItem('token');
          window.location.href = '/';
        }}>Выход</button>
      </header>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Всего прогнозов</div>
          <div className="stat-value">{dashboard.stats.total_predictions}</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Всего клиентов</div>
          <div className="stat-value">{dashboard.stats.total_clients}</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Средняя уверенность</div>
          <div className="stat-value">{(dashboard.stats.avg_confidence * 100).toFixed(1)}%</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Версия модели</div>
          <div className="stat-value">{dashboard.stats.model_version}</div>
        </div>
      </section>

      <section className="metrics-section">
        <h2>Метрики качества</h2>
        <table className="metrics-table">
          <thead>
            <tr>
              <th>Метрика</th>
              <th>Обучение</th>
              <th>Тест</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.stats.metrics.map((m) => (
              <tr key={m.metric_name}>
                <td>{m.metric_name}</td>
                <td>{m.train_value.toFixed(4)}</td>
                <td>{m.test_value.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="distribution-section">
        <h2>Распределение по категориям дохода</h2>
        <div className="distribution-grid">
          {dashboard.income_distribution.map((d) => (
            <div key={d.category} className="distribution-item">
              <div className="category-label">{d.category}</div>
              <div className="category-count">{d.count}</div>
              <div className="category-percent">{d.percentage.toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
