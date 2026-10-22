import React from 'react';
import { Car, Siren, Shield, ChevronRight } from 'lucide-react';

interface WelcomeScreenProps {
  onSelectRole: (role: 'driver' | 'emergency' | 'police') => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectRole }) => {
  const containerStyle: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    backgroundColor: 'white',
    padding: '24px 24px 24px 24px',
    paddingTop: '16px',
    userSelect: 'none',
  };

  const headerStyle: React.CSSProperties = {
    marginTop: '24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: '16px',
  };

  const logoBoxStyle: React.CSSProperties = {
    width: '40px',
    height: '40px',
    borderRadius: '16px',
    backgroundColor: '#1e293b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  };

  const dotStyle = (color: string): React.CSSProperties => ({
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    backgroundColor: color,
    boxShadow: `0 0 6px ${color}`,
  });

  const logoDotsStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    alignItems: 'center',
  };

  const titleStyle: React.CSSProperties = {
    fontFamily: "'Outfit', sans-serif",
    fontSize: '20px',
    fontWeight: 'bold',
    letterSpacing: '-0.02em',
    color: '#0f172a',
  };

  const headingStyle: React.CSSProperties = {
    fontFamily: "'Outfit', sans-serif",
    fontSize: '24px',
    fontWeight: '800',
    color: '#0f172a',
    lineHeight: 1.2,
    marginTop: '8px',
  };

  const subtextStyle: React.CSSProperties = {
    fontSize: '12px',
    color: '#64748b',
    lineHeight: 1.4,
    maxWidth: '280px',
  };

  const cardsContainerStyle: React.CSSProperties = {
    marginTop: '32px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  };

  const cardLabelStyle: React.CSSProperties = {
    fontSize: '11px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: '#94a3b8',
  };

  const cardButtonStyle = (hoverColor: string): React.CSSProperties => ({
    width: '100%',
    textAlign: 'left',
    padding: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    border: '1px solid #e2e8f0',
    borderRadius: '18px',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s',
  });

  const cardIconStyle = (bgColor: string, iconColor: string): React.CSSProperties => ({
    width: '40px',
    height: '40px',
    borderRadius: '12px',
    backgroundColor: bgColor,
    color: iconColor,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  });

  const cardContentStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
    flex: 1,
  };

  const cardTitleStyle: React.CSSProperties = {
    fontFamily: "'Outfit', sans-serif",
    fontWeight: '700',
    fontSize: '14px',
    color: '#0f172a',
  };

  const cardDescStyle: React.CSSProperties = {
    fontSize: '11px',
    color: '#64748b',
  };

  const footerStyle: React.CSSProperties = {
    paddingTop: '16px',
    textAlign: 'center',
  };

  const footerTextStyle: React.CSSProperties = {
    fontSize: '11px',
    color: '#94a3b8',
  };

  const navPillStyle: React.CSSProperties = {
    width: '110px',
    height: '4px',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderRadius: '2px',
    margin: '6px auto 4px',
  };

  return (
    <div style={containerStyle}>
      <div>
        {/* Brand Logo & Header */}
        <div style={headerStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={logoBoxStyle}>
              <div style={logoDotsStyle}>
                <div style={dotStyle('#ef4444')} />
                <div style={dotStyle('#fbbf24')} />
                <div style={dotStyle('#10b981')} />
              </div>
            </div>
            <span style={titleStyle}>UATMMS</span>
          </div>

          <div style={{ marginTop: '8px' }}>
            <h1 style={headingStyle}>
              Smarter signals.<br />
              Safer roads.<br />
              Faster responses.
            </h1>
            <p style={subtextStyle}>
              Live traffic, safe routes and emergency green corridors.
            </p>
          </div>
        </div>

        {/* Continue As Selection Cards */}
        <div style={cardsContainerStyle}>
          <span style={cardLabelStyle}>
            Continue as
          </span>

          {/* Role 1: Driver / Commuter */}
          <button
            onClick={() => onSelectRole('driver')}
            style={cardButtonStyle('#blue')}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#fbbf24';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={cardIconStyle('#eff6ff', '#2563eb')}>
                <Car size={20} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h3 style={cardTitleStyle}>
                  Driver / Commuter
                </h3>
                <p style={cardDescStyle}>Live traffic, alerts and smart routes</p>
              </div>
            </div>
            <ChevronRight size={16} color={'#cbd5e1'} />
          </button>

          {/* Role 2: Ambulance / Fire Crew */}
          <button
            onClick={() => onSelectRole('emergency')}
            style={cardButtonStyle('#red')}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#ef4444';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={cardIconStyle('#fef2f2', '#dc2626')}>
                <Siren size={20} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h3 style={cardTitleStyle}>
                  Ambulance / Fire crew
                </h3>
                <p style={cardDescStyle}>Request a green corridor</p>
              </div>
            </div>
            <ChevronRight size={16} color={'#cbd5e1'} />
          </button>

          {/* Role 3: Traffic Police (Field) */}
          <button
            onClick={() => onSelectRole('police')}
            style={cardButtonStyle('#amber')}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#f59e0b';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={cardIconStyle('#fffbeb', '#b45309')}>
                <Shield size={20} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h3 style={cardTitleStyle}>
                  Traffic Police (field)
                </h3>
                <p style={cardDescStyle}>Verify incidents on the ground</p>
              </div>
            </div>
            <ChevronRight size={16} color={'#cbd5e1'} />
          </button>
        </div>
      </div>

      {/* Footer Info */}
      <div style={footerStyle}>
        <p style={footerTextStyle}>
          Staff consoles (Operator, Admin, Hospital) are on the web app.
        </p>
        <div style={navPillStyle} />
      </div>
    </div>
  );
};
