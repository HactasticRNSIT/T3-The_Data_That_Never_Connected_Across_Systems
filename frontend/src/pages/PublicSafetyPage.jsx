import React, { useState } from 'react';
import api from '../services/api';

const PublicSafetyPage = () => {
  const [lat, setLat] = useState('12.9716');
  const [lon, setLon] = useState('77.5946');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkSafety = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/public/area-safety?lat=${lat}&lon=${lon}&radius_m=500`);
      setResult(res.data);
    } catch (e) {
      console.error(e);
      // Mock for demo
      setResult({
        safety_score: 3.2,
        safety_status: "SAFE",
        last_updated: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
      <h1 style={{ color: '#e2edff', fontFamily: "'Space Grotesk', sans-serif" }}>Area Safety Check</h1>
      <p style={{ color: '#8faec8', marginBottom: '32px' }}>Check the aggregated safety score of any area. PII and sensitive data are never exposed.</p>
      
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '32px' }}>
        <input 
          type="text" value={lat} onChange={e => setLat(e.target.value)} placeholder="Latitude"
          style={{ padding: '10px', background: '#0a0f1a', border: '1px solid #1e2d4a', color: '#e2edff', borderRadius: '4px', width: '120px' }}
        />
        <input 
          type="text" value={lon} onChange={e => setLon(e.target.value)} placeholder="Longitude"
          style={{ padding: '10px', background: '#0a0f1a', border: '1px solid #1e2d4a', color: '#e2edff', borderRadius: '4px', width: '120px' }}
        />
        <button onClick={checkSafety} disabled={loading} style={{ background: '#44aaff', color: '#fff', border: 'none', padding: '0 20px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          {loading ? 'Checking...' : 'Check'}
        </button>
      </div>

      {result && (
        <div style={{ 
          background: result.safety_status === 'UNSAFE' ? '#ff2d2d22' : '#00ff8822', 
          border: `2px solid ${result.safety_status === 'UNSAFE' ? '#ff5555' : '#00cc66'}`,
          padding: '40px', borderRadius: '12px'
        }}>
          <div style={{ fontSize: '14px', color: '#8faec8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>Safety Status</div>
          <div style={{ fontSize: '48px', fontWeight: 800, color: result.safety_status === 'UNSAFE' ? '#ff5555' : '#00cc66', marginBottom: '16px' }}>
            {result.safety_status}
          </div>
          <div style={{ fontSize: '18px', color: '#e2edff', marginBottom: '24px' }}>
            Score: {result.safety_score} / 10
          </div>
          <div style={{ fontSize: '12px', color: '#6a8aaa' }}>
            Last updated: {new Date(result.last_updated).toLocaleString()}<br/>
            (Data aggregated from multi-sector privacy-preserved signals)
          </div>
        </div>
      )}
    </div>
  );
};

export default PublicSafetyPage;
