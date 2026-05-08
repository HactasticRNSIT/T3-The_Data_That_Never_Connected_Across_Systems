import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../../store/authSlice';

const Navbar = () => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { user } = useSelector((state) => state.auth);
  const alertsTotal = useSelector((state) => state.alerts.total);

  const navStyles = {
    position: 'fixed', top: 0, left: 0, right: 0, height: '60px',
    background: '#0d1829', borderBottom: '1px solid #1e2d4a',
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 24px', zIndex: 1000
  };

  const linkStyles = (path) => ({
    color: location.pathname === path ? '#44aaff' : '#8faec8',
    textDecoration: 'none', fontSize: '14px', fontWeight: 600,
    marginRight: '24px', position: 'relative'
  });

  return (
    <nav style={navStyles}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: '#e2edff', fontSize: '18px', fontWeight: 800, marginRight: '48px', fontFamily: "'Space Grotesk', sans-serif" }}>
          SafeGrid
        </div>
        <Link to="/dashboard" style={linkStyles('/dashboard')}>Map Dashboard</Link>
        <Link to="/alerts" style={linkStyles('/alerts')}>
          Alerts
          {alertsTotal > 0 && (
            <span style={{
              background: '#ff5555', color: '#fff', fontSize: '10px',
              padding: '2px 6px', borderRadius: '10px', marginLeft: '6px'
            }}>
              {alertsTotal}
            </span>
          )}
        </Link>
        <Link to="/public" style={linkStyles('/public')} target="_blank">Public View</Link>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: '#6a8aaa', fontSize: '12px', marginRight: '16px' }}>
          Logged in as: <span style={{ color: '#44aaff', textTransform: 'uppercase' }}>{user?.sector}</span>
        </div>
        <button 
          onClick={() => dispatch(logout())}
          style={{
            background: 'transparent', border: '1px solid #1e2d4a', color: '#8faec8',
            padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px'
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
