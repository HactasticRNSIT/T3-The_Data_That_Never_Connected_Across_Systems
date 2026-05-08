import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { setCredentials } from '../store/authSlice';
import api from '../services/api';

const LoginPage = () => {
  const [email, setEmail] = useState('officer@police.gov');
  const [password, setPassword] = useState('securepassword123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      // In hackathon dev, this might fail if backend isn't up, 
      // fallback to mock login if needed.
      const res = await api.post('/auth/login', { email, password });
      dispatch(setCredentials(res.data));
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      setError('Invalid credentials or backend not running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: '#060d18' }}>
      <div style={{ width: '360px', padding: '32px', background: '#0d1829', border: '1px solid #1e2d4a', borderRadius: '8px' }}>
        <h2 style={{ margin: '0 0 24px', color: '#e2edff', textAlign: 'center', fontFamily: "'Space Grotesk', sans-serif" }}>SafeGrid Login</h2>
        {error && <div style={{ color: '#ff5555', background: '#ff2d2d22', padding: '10px', borderRadius: '4px', marginBottom: '16px', fontSize: '13px' }}>{error}</div>}
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', color: '#8faec8', fontSize: '12px', marginBottom: '4px' }}>Email</label>
            <input 
              type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              style={{ width: '100%', padding: '10px', background: '#060d18', border: '1px solid #1e2d4a', color: '#e2edff', borderRadius: '4px' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', color: '#8faec8', fontSize: '12px', marginBottom: '4px' }}>Password</label>
            <input 
              type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
              style={{ width: '100%', padding: '10px', background: '#060d18', border: '1px solid #1e2d4a', color: '#e2edff', borderRadius: '4px' }}
            />
          </div>
          <button 
            type="submit" disabled={loading}
            style={{ padding: '12px', background: '#44aaff', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}
          >
            {loading ? 'Logging in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
