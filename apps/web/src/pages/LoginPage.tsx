import React, { useState } from 'react';
import { Lock, Mail } from 'lucide-react';

interface LoginPageProps {
  onSelectRole: (role: 'operator' | 'admin' | 'police' | 'hospital') => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSelectRole }) => {
  const [email, setEmail] = useState('priya.kulkarni@kolhapur-traffic.gov.in');
  const [password, setPassword] = useState('••••••••••');
  const [showPassword, setShowPassword] = useState(false);

  const containerStyle: React.CSSProperties = {
    minHeight: '100vh',
    display: 'flex',
    backgroundColor: '#0f172a',
  };

  const leftStyle: React.CSSProperties = {
    flex: 1,
    padding: '48px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    backgroundColor: '#1e293b',
    color: 'white',
  };

  const rightStyle: React.CSSProperties = {
    flex: 1,
    padding: '48px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    backgroundColor: 'white',
  };

  const logoStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '48px',
  };

  const logoBoxStyle: React.CSSProperties = {
    width: '40px',
    height: '40px',
    borderRadius: '8px',
    background: 'linear-gradient(to bottom right, #ef4444, #f59e0b, #10b981)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    fontSize: '12px',
  };

  const h1Style: React.CSSProperties = {
    fontSize: '48px',
    fontWeight: 'bold',
    lineHeight: 1.2,
    marginBottom: '24px',
  };

  const statsStyle: React.CSSProperties = {
    display: 'flex',
    gap: '32px',
    margin: '32px 0 24px 0',
  };

  const formContainerStyle: React.CSSProperties = {
    maxWidth: '448px',
    width: '100%',
  };

  const h2Style: React.CSSProperties = {
    fontSize: '30px',
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: '8px',
  };

  const inputGroupStyle: React.CSSProperties = {
    marginBottom: '20px',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '12px',
    fontWeight: '600',
    color: '#475569',
    marginBottom: '8px',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    paddingLeft: '40px',
    paddingRight: '16px',
    paddingTop: '8px',
    paddingBottom: '8px',
    border: '1px solid #cbd5e1',
    borderRadius: '8px',
    backgroundColor: '#f1f5f9',
    color: '#0f172a',
    fontSize: '14px',
    position: 'relative',
  };

  const iconStyle: React.CSSProperties = {
    position: 'absolute',
    left: '12px',
    top: '50%',
    transform: 'translateY(-50%)',
    color: '#94a3b8',
    width: '16px',
    height: '16px',
  };

  const buttonStyle: React.CSSProperties = {
    width: '100%',
    backgroundColor: '#ea580c',
    color: 'white',
    fontWeight: 'bold',
    padding: '10px 20px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    marginBottom: '24px',
  };

  const rolesGridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
  };

  const roleCardStyle: React.CSSProperties = {
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #e2e8f0',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'all 0.2s',
  };

  const footerStyle: React.CSSProperties = {
    textAlign: 'center',
    fontSize: '12px',
    color: '#94a3b8',
  };

  return (
    <div style={containerStyle}>
      {/* Left Side - Branding */}
      <div style={leftStyle}>
        <div>
          <div style={logoStyle}>
            <div style={logoBoxStyle}>
              <span>U</span>
            </div>
            <span style={{ fontSize: '24px', fontWeight: 'bold' }}>UATMMS</span>
          </div>

          <h1 style={h1Style}>
            Smarter signals.<br />
            Safer roads.<br />
            Faster responses.
          </h1>

          <p style={{ fontSize: '18px', color: '#cbd5e1', marginBottom: '32px', maxWidth: '448px' }}>
            AI-powered, network-level traffic management with automatic green corridors for ambulances and fire trucks.
          </p>

          <div style={statsStyle}>
            <div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#f97316' }}>↓ 42%</div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>waiting time</div>
            </div>
            <div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#f97316' }}>↓ 38%</div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>emergency travel</div>
            </div>
            <div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#10b981' }}>0</div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>safety violations</div>
            </div>
          </div>

          <p style={{ fontSize: '11px', color: '#64748b', marginTop: '24px' }}>
            Demo targets from simulation — to be validated in pilot.
          </p>
        </div>

        {/* Network Graph */}
        <div style={{
          width: '100%',
          height: '192px',
          backgroundColor: '#334155',
          borderRadius: '12px',
          border: '1px solid #475569',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{ color: '#94a3b8', fontSize: '14px' }}>Network Topology Visualization</div>
        </div>
      </div>

      {/* Right Side - Login */}
      <div style={rightStyle}>
        <div style={formContainerStyle}>
          <h2 style={h2Style}>Welcome back</h2>
          <p style={{ color: '#475569', marginBottom: '32px', fontSize: '14px' }}>Sign in to your UATMMS console, or pick a demo role to explore.</p>

          {/* Login Form */}
          <div style={{ marginBottom: '32px' }}>
            <div style={inputGroupStyle}>
              <label style={labelStyle}>Email / Employee ID</label>
              <div style={{ position: 'relative' }}>
                <Mail style={iconStyle as any} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={inputStyle}
                />
              </div>
            </div>

            <div style={inputGroupStyle}>
              <label style={labelStyle}>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock style={iconStyle as any} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(p) => setPassword(p.currentTarget.value)}
                  style={inputStyle}
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: '12px',
                    color: '#475569',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>
          </div>

          <button style={buttonStyle}>
            Sign in
          </button>

          <div style={{ textAlign: 'center', fontSize: '14px', color: '#475569', marginBottom: '32px' }}>
            or choose a demo role
          </div>

          {/* Demo Roles */}
          <div style={rolesGridStyle}>
            <button
              onClick={() => onSelectRole('operator')}
              style={{
                ...roleCardStyle,
                borderColor: 'transparent',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#ea580c';
                e.currentTarget.style.backgroundColor = '#fed7aa';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '14px' }}>Traffic Operator</div>
              <div style={{ fontSize: '11px', color: '#475569' }}>Monitor & control live network</div>
              <div style={{ fontSize: '12px', color: '#ea580c', fontWeight: '600', marginTop: '8px' }}>Web →</div>
            </button>

            <button
              onClick={() => onSelectRole('admin')}
              style={roleCardStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#ea580c';
                e.currentTarget.style.backgroundColor = '#fed7aa';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '14px' }}>System Admin</div>
              <div style={{ fontSize: '11px', color: '#475569' }}>Users, policies, analytics</div>
              <div style={{ fontSize: '12px', color: '#ea580c', fontWeight: '600', marginTop: '8px' }}>Web →</div>
            </button>

            <button
              onClick={() => onSelectRole('police')}
              style={roleCardStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#ea580c';
                e.currentTarget.style.backgroundColor = '#fed7aa';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '14px' }}>Traffic Police</div>
              <div style={{ fontSize: '11px', color: '#475569' }}>Verify incidents · manual override</div>
              <div style={{ fontSize: '12px', color: '#ea580c', fontWeight: '600', marginTop: '8px' }}>Web →</div>
            </button>

            <button
              onClick={() => onSelectRole('hospital')}
              style={roleCardStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#10b981';
                e.currentTarget.style.backgroundColor = '#dcfce7';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '14px' }}>Hospital / ER</div>
              <div style={{ fontSize: '11px', color: '#475569' }}>Track ambulances · dispatch</div>
              <div style={{ fontSize: '12px', color: '#10b981', fontWeight: '600', marginTop: '8px' }}>Web →</div>
            </button>
          </div>
        </div>

        <div style={footerStyle}>
          © 2026 UATMMS. All rights reserved.
        </div>
      </div>
    </div>
  );
};
