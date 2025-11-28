import React, { useEffect, useState } from 'react';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ClientSearchPage from './pages/ClientSearchPage';
import ClientListPage from './pages/ClientListPage';
import './styles/index.css';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
    setLoading(false);
  }, []);

  if (loading) return <div className="loading">Загрузка...</div>;

  if (!isLoggedIn) return <LoginPage />;

  return (
    <div className="app">
      <nav className="main-nav">
        <div className="nav-brand">Альфа-Банк</div>
        <div className="nav-links">
          <button 
            className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentPage('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`nav-link ${currentPage === 'search' ? 'active' : ''}`}
            onClick={() => setCurrentPage('search')}
          >
            🔍 Поиск клиента
          </button>
          <button 
            className={`nav-link ${currentPage === 'list' ? 'active' : ''}`}
            onClick={() => setCurrentPage('list')}
          >
            📋 Список клиентов
          </button>
          <button 
            className="nav-link logout"
            onClick={() => {
              localStorage.removeItem('token');
              setIsLoggedIn(false);
            }}
          >
            🚪 Выход
          </button>
        </div>
      </nav>

      <main className="main-content">
        {currentPage === 'dashboard' && <DashboardPage />}
        {currentPage === 'search' && <ClientSearchPage />}
        {currentPage === 'list' && <ClientListPage />}
      </main>
    </div>
  );
}
