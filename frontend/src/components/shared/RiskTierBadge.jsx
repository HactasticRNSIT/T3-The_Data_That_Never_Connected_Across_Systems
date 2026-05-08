import React from 'react';

const RiskTierBadge = ({ tier }) => {
  const styles = {
    LOW: { bg: '#00ff8822', color: '#00cc66', border: '#00ff8855' },
    MODERATE: { bg: '#ffaa0022', color: '#ffcc44', border: '#ffaa0055' },
    HIGH: { bg: '#ff660022', color: '#ff8844', border: '#ff660055' },
    CRITICAL: { bg: '#ff2d2d22', color: '#ff5555', border: '#ff2d2d55' },
  };

  const s = styles[tier] || styles.LOW;

  return (
    <span style={{
      background: s.bg,
      color: s.color,
      border: `1px solid ${s.border}`,
      padding: '2px 8px',
      borderRadius: '4px',
      fontSize: '11px',
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: '0.05em'
    }}>
      {tier}
    </span>
  );
};

export default RiskTierBadge;
