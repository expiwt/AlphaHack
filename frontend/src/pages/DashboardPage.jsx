import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const fileInputRef = useRef(null);

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

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert('Пожалуйста, выберите CSV файл');
      return;
    }

    setUploading(true);
    setUploadMessage('');

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/clients/upload-csv`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setUploadMessage(`Успешно загружено ${response.data.processed_clients} клиентов`);
      
      // Обновляем dashboard после загрузки
      await fetchDashboard();
      
      // Очищаем input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Ошибка загрузки файла';
      setUploadMessage(`Ошибка: ${errorMsg}`);
      alert(`Ошибка загрузки: ${errorMsg}`);
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (!dashboard) return <div>Ошибка загрузки данных</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Система прогноза доходов Альфа-Банка</h1>
        <div className="header-actions">
          <div className="upload-section">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="csv-upload"
              disabled={uploading}
            />
            <label htmlFor="csv-upload" className="upload-button">
              {uploading ? 'Загрузка...' : 'Загрузить CSV'}
            </label>
            {uploadMessage && (
              <div className={`upload-message ${uploadMessage.includes('Ошибка') ? 'error' : 'success'}`}>
                {uploadMessage}
              </div>
            )}
          </div>
        </div>
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

      {dashboard.credit_decisions && (
        <section className="credit-decisions-section">
          <h2>Решения по кредитам</h2>
          <div className="credit-decisions-grid">
            <div className="credit-decision-card approved">
              <div className="decision-card-label">Одобрено</div>
              <div className="decision-card-value">{dashboard.credit_decisions.approved}</div>
              <div className="decision-card-percent">
                {dashboard.credit_decisions.approval_rate.toFixed(1)}%
              </div>
            </div>
            
            <div className="credit-decision-card rejected">
              <div className="decision-card-label">Отклонено</div>
              <div className="decision-card-value">{dashboard.credit_decisions.rejected}</div>
              <div className="decision-card-percent">
                {(100 - dashboard.credit_decisions.approval_rate).toFixed(1)}%
              </div>
            </div>
          </div>
          
          <div className="approval-rate-bar">
            <div 
              className="approval-rate-fill"
              style={{ width: `${dashboard.credit_decisions.approval_rate}%` }}
            ></div>
          </div>
        </section>
      )}
    </div>
  );
}
