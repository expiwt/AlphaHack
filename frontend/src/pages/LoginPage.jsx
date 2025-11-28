import React, { useState } from 'react';
import axios from 'axios';

export default function LoginPage() {
  const [email, setEmail] = useState('test@alfabank.ru');
  const [password, setPassword] = useState('test123');
  const [fullName, setFullName] = useState('Test User');
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isRegister ? '/auth/register' : '/auth/login';
      const data = isRegister 
        ? { email, password, full_name: fullName }
        : { email, password };

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}${endpoint}`,
        data
      );

      const token = response.data.access_token;
      localStorage.setItem('token', token);
      
      // Перезагружаем страницу чтобы приложение это заметило
      window.location.href = '/';
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при входе');
    }

    setLoading(false);
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Альфа-Банк</h1>
        <p>Система прогноза доходов</p>

        <form onSubmit={handleAuth} className="login-form">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          {isRegister && (
            <input
              type="text"
              placeholder="ФИО"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          )}

          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Загрузка...' : isRegister ? 'Регистрация' : 'Вход'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        <div className="auth-toggle">
          {isRegister ? (
            <>
              Уже есть аккаунт?{' '}
              <button onClick={() => setIsRegister(false)} className="link-button">
                Войти
              </button>
            </>
          ) : (
            <>
              Нет аккаунта?{' '}
              <button onClick={() => setIsRegister(true)} className="link-button">
                Регистрация
              </button>
            </>
          )}
        </div>

        <div className="demo-credentials">
          Demo: test@alfabank.ru / test123
        </div>
      </div>
    </div>
  );
}
