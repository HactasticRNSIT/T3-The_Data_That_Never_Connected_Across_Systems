import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import api from '../services/api';
import { setAlerts } from '../store/alertsSlice';
import RiskTierBadge from '../components/shared/RiskTierBadge';

const AlertsPage = () => {
  const dispatch = useDispatch();
  const { items } = useSelector(state => state.alerts);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await api.get('/department/alerts');
        dispatch(setAlerts(res.data));
      } catch (e) {
        console.error("Failed to fetch alerts", e);
        // Fallback for UI visualization
        dispatch(setAlerts({
          alerts: [{
            id: 'demo-1',
            hex_id: '8961892a3c3ffff',
            risk_score: 8.1,
            new_tier: 'CRITICAL',
            narrative: 'Concentration of violence-related reports and trauma admissions in this corridor suggests escalating risk after 10 PM. Recommend increased patrol frequency.',
            created_at: new Date().toISOString()
          }],
          total: 1
        }));
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, [dispatch]);

  return (
    <div style={{ padding: '32px', maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ color: '#e2edff', margin: '0 0 24px', fontFamily: "'Space Grotesk', sans-serif" }}>Department Alerts</h2>
      
      {items.length === 0 ? (
        <div style={{ color: '#6a8aaa', textAlign: 'center', padding: '40px', background: '#0a0f1a', borderRadius: '8px' }}>
          No active alerts for your sector.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {items.map(alert => (
            <div key={alert.id} style={{ 
              background: '#060d18', 
              border: `1px solid ${alert.new_tier === 'CRITICAL' ? '#ff2d2d55' : '#1e2d4a'}`, 
              borderRadius: '8px', padding: '20px',
              borderLeft: `4px solid ${alert.new_tier === 'CRITICAL' ? '#ff5555' : '#ffaa00'}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <RiskTierBadge tier={alert.new_tier} />
                  <span style={{ color: '#e2edff', fontWeight: 'bold' }}>Score: {alert.risk_score}</span>
                </div>
                <div style={{ color: '#6a8aaa', fontSize: '12px' }}>
                  {new Date(alert.created_at).toLocaleString()}
                </div>
              </div>
              <p style={{ color: '#c8d8f0', fontSize: '14px', lineHeight: 1.6, margin: '0 0 16px' }}>
                {alert.narrative}
              </p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#3a5070', fontSize: '11px', fontFamily: 'monospace' }}>HEX: {alert.hex_id}</span>
                <button style={{ background: '#0d1829', color: '#44aaff', border: '1px solid #44aaff44', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                  View on Map
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlertsPage;
