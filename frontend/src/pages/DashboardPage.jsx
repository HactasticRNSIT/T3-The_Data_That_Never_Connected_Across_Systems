import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import api from '../services/api';
import { setHeatmapData, setSelectedHex, updateHexTier } from '../store/mapSlice';
import { addAlert } from '../store/alertsSlice';
import { wsService } from '../services/wsService';
import RiskTierBadge from '../components/shared/RiskTierBadge';

// Helper component to trigger fetching data when map bounds change
const MapEvents = ({ setBounds }) => {
  const map = useMap();
  useEffect(() => {
    const updateBounds = () => {
      const b = map.getBounds();
      setBounds(`${b.getWest()},${b.getSouth()},${b.getEast()},${b.getNorth()}`);
    };
    map.on('moveend', updateBounds);
    updateBounds();
    return () => map.off('moveend', updateBounds);
  }, [map]);
  return null;
};

const DashboardPage = () => {
  const dispatch = useDispatch();
  const { heatmapData, selectedHex } = useSelector(state => state.map);
  const { token } = useSelector(state => state.auth);
  const [bounds, setBounds] = useState('77.55,12.85,77.75,13.05');

  // Fetch heatmap data when bounds change
  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        const res = await api.get(`/map/heatmap?bbox=${bounds}`);
        dispatch(setHeatmapData(res.data));
      } catch (e) {
        // Fallback to mock data if API fails
        const mockData = await import('../mocks/mockHeatmap.json');
        dispatch(setHeatmapData(mockData.default));
      }
    };
    
    // Simple debounce
    const timer = setTimeout(fetchHeatmap, 500);
    return () => clearTimeout(timer);
  }, [bounds, dispatch]);

  // Connect WebSocket
  useEffect(() => {
    if (token) {
      wsService.connect(token);
      const unsubscribe = wsService.subscribe((message) => {
        if (message.event === 'RISK_TIER_CHANGE') {
          dispatch(updateHexTier(message));
        } else if (message.event === 'NEW_ALERT') {
          dispatch(addAlert(message));
        }
      });
      return () => {
        unsubscribe();
        wsService.disconnect();
      };
    }
  }, [token, dispatch]);

  const getStyle = (feature) => {
    const colors = { LOW: '#00cc66', MODERATE: '#ffcc44', HIGH: '#ff8844', CRITICAL: '#ff5555' };
    const tier = feature.properties.risk_tier || 'LOW';
    return {
      fillColor: colors[tier],
      weight: tier === 'CRITICAL' ? 2 : 1,
      opacity: 1,
      color: tier === 'CRITICAL' ? '#ff2d2d' : colors[tier],
      fillOpacity: tier === 'LOW' ? 0.2 : 0.6
    };
  };

  const onEachFeature = (feature, layer) => {
    layer.on({
      click: () => {
        dispatch(setSelectedHex(feature.properties));
      }
    });
  };

  // Trigger demo ingest
  const triggerIngest = async () => {
    try {
      await api.post('/ingest/police', {
        batch_id: "550e8400-e29b-41d4-a716-446655440000",
        timestamp_utc: new Date().toISOString(),
        vectors: [{ lat: 12.977, lon: 77.575, signal_type: "violent_incident", severity: 0.9, hour_of_day: 22, day_of_week: 3, count: 5 }]
      });
      alert('Ingestion simulated!');
    } catch (e) {
      console.error(e);
      alert('Failed to simulate ingest');
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 60px)' }}>
      {/* Map Area */}
      <div style={{ flex: 1, position: 'relative' }}>
        <MapContainer center={[12.9716, 77.5946]} zoom={13} style={{ height: '100%', width: '100%', background: '#0a0f1a' }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
          <MapEvents setBounds={setBounds} />
          {heatmapData.features.length > 0 && (
            <GeoJSON 
              key={JSON.stringify(heatmapData.meta)} 
              data={heatmapData} 
              style={getStyle} 
              onEachFeature={onEachFeature} 
            />
          )}
        </MapContainer>
        
        <button 
          onClick={triggerIngest}
          style={{ position: 'absolute', bottom: 20, left: 20, zIndex: 1000, background: '#ffcc44', color: '#000', padding: '10px 16px', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}
        >
          Simulate Ingest
        </button>
      </div>

      {/* Sidebar for Hex Details */}
      <div style={{ width: '350px', background: '#060d18', borderLeft: '1px solid #1e2d4a', padding: '20px', overflowY: 'auto' }}>
        <h3 style={{ margin: '0 0 16px', color: '#94b8e0', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Hex Details</h3>
        
        {selectedHex ? (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <div style={{ color: '#8faec8', fontSize: '12px', marginBottom: '4px' }}>Risk Tier</div>
              <RiskTierBadge tier={selectedHex.risk_tier} />
              <span style={{ marginLeft: '12px', color: '#e2edff', fontSize: '18px', fontWeight: 'bold' }}>Score: {selectedHex.risk_score}</span>
            </div>
            
            <div style={{ background: '#0a0f1a', padding: '12px', borderRadius: '6px', border: '1px solid #1e2d4a', marginBottom: '16px' }}>
              <div style={{ color: '#8faec8', fontSize: '12px', marginBottom: '8px' }}>Top Signal</div>
              <div style={{ color: '#e2edff', fontWeight: 600 }}>{selectedHex.top_signal || 'N/A'} <span style={{ color: '#44aaff', fontSize: '12px', marginLeft: '8px' }}>({selectedHex.top_sector || 'N/A'})</span></div>
              <div style={{ marginTop: '8px', color: '#8faec8', fontSize: '12px' }}>Total Signals: {selectedHex.signal_count}</div>
            </div>

            {selectedHex.alert_narrative && (
              <div style={{ background: '#ff2d2d11', borderLeft: '3px solid #ff5555', padding: '12px', borderRadius: '4px' }}>
                <div style={{ color: '#ff5555', fontSize: '11px', fontWeight: 'bold', marginBottom: '6px', textTransform: 'uppercase' }}>AI Briefing</div>
                <div style={{ color: '#c8d8f0', fontSize: '13px', lineHeight: 1.5 }}>{selectedHex.alert_narrative}</div>
              </div>
            )}
            
            <div style={{ marginTop: '24px', color: '#3a5070', fontSize: '11px', fontFamily: 'monospace' }}>
              ID: {selectedHex.hex_id}<br/>
              Updated: {new Date(selectedHex.computed_at).toLocaleString()}
            </div>
          </div>
        ) : (
          <div style={{ color: '#6a8aaa', fontSize: '13px', textAlign: 'center', marginTop: '40px' }}>
            Click on a hex on the map to view risk details and AI narratives.
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
