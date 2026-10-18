import React from 'react';

interface NetworkMapProps {
  mode?: 'driver_home' | 'driver_route' | 'emergency_active' | 'police';
  height?: number;
  highlightRoute?: boolean;
}

export const NetworkMap: React.FC<NetworkMapProps> = ({ 
  mode = 'driver_home', 
  height = 220,
}) => {
  // Graph Nodes
  const nodes = [
    { id: 'J8', x: 70, y: 40, label: 'J8', status: 'normal' },
    { id: 'J7', x: 120, y: 110, label: 'J7 (You)', status: 'heavy' },
    { id: 'J12', x: 230, y: 50, label: 'J12', status: 'accident' },
    { id: 'J4', x: 200, y: 130, label: 'J4', status: 'smooth' },
    { id: 'J3', x: 80, y: 175, label: 'J3', status: 'normal' },
    { id: 'J5', x: 270, y: 140, label: 'J5', status: 'normal' },
    { id: 'H', x: 310, y: 80, label: 'H (Hospital)', status: 'hospital' },
  ];

  // Edges between junctions
  const edges = [
    { from: 'J8', to: 'J7', color: '#10b981' }, // green
    { from: 'J8', to: 'J12', color: '#f59e0b' }, // amber
    { from: 'J7', to: 'J12', color: '#ef4444' }, // red (accident diversion)
    { from: 'J7', to: 'J4', color: '#10b981' },
    { from: 'J7', to: 'J3', color: '#10b981' },
    { from: 'J4', to: 'J5', color: '#10b981' },
    { from: 'J12', to: 'J5', color: '#f59e0b' },
    { from: 'J5', to: 'H', color: '#10b981' },
    { from: 'J12', to: 'H', color: '#94a3b8' },
  ];

  // Node position helper
  const getNode = (id: string) => nodes.find(n => n.id === id);

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-[#eaf1f8] border border-slate-200/80 shadow-inner flex items-center justify-center select-none" style={{ height }}>
      {/* City Map Grid / Road Blocks Background */}
      <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="city-grid" width="28" height="28" patternUnits="userSpaceOnUse">
            <rect width="28" height="28" fill="#f0f4f9" />
            <rect x="2" y="2" width="24" height="24" rx="4" fill="#e2e8f0" opacity="0.6" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#city-grid)" />

        {/* Regular Traffic Edges */}
        {edges.map((e, idx) => {
          const n1 = getNode(e.from);
          const n2 = getNode(e.to);
          if (!n1 || !n2) return null;
          return (
            <line
              key={idx}
              x1={n1.x}
              y1={n1.y}
              x2={n2.x}
              y2={n2.y}
              stroke={e.color}
              strokeWidth="4"
              strokeLinecap="round"
              opacity="0.8"
            />
          );
        })}

        {/* Highlighted Driver Route (J7 -> J8 -> J4) */}
        {mode === 'driver_route' && (
          <path
            d="M 120 110 L 70 40 L 200 130"
            fill="none"
            stroke="#2563eb"
            strokeWidth="6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Highlighted Green Corridor Path (J7 -> J3 -> J4 -> J5 -> H) */}
        {mode === 'emergency_active' && (
          <>
            <path
              d="M 120 110 L 80 175 L 200 130 L 270 140 L 310 80"
              fill="none"
              stroke="#22c55e"
              strokeWidth="8"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="drop-shadow-[0_0_8px_rgba(34,197,94,0.8)]"
            />
            {/* Animated Ambulance Pulse along corridor */}
            <circle cx="150" cy="148" r="6" fill="#dc2626" className="animate-ping" />
            <circle cx="150" cy="148" r="7" fill="#dc2626" stroke="#ffffff" strokeWidth="2" />
          </>
        )}

        {/* Network Nodes (Intersections) */}
        {nodes.map(n => {
          const isHeavy = n.status === 'heavy';
          const isAccident = n.status === 'accident';
          const isHospital = n.status === 'hospital';

          return (
            <g key={n.id}>
              {/* Outer halo */}
              <circle
                cx={n.x}
                cy={n.y}
                r={isHospital || isHeavy || isAccident ? 10 : 7}
                fill={
                  isHospital
                    ? '#3b82f6'
                    : isAccident
                    ? '#ef4444'
                    : isHeavy
                    ? '#f97316'
                    : '#ffffff'
                }
                stroke={isHospital ? '#1d4ed8' : isAccident ? '#b91c1c' : '#64748b'}
                strokeWidth="2"
              />
              
              {/* Node Icon / Letter */}
              <text
                x={n.x}
                y={n.y + 3}
                fontSize={isHospital ? "8" : "7"}
                fontWeight="700"
                textAnchor="middle"
                fill={isHospital || isAccident || isHeavy ? '#ffffff' : '#1e293b'}
                className="select-none pointer-events-none"
              >
                {n.id}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Floating Status Badge on Map */}
      {mode === 'emergency_active' && (
        <div className="absolute top-2.5 left-2.5 bg-emerald-600/90 text-white text-[10px] font-bold px-2.5 py-1 rounded-full shadow-md flex items-center gap-1.5 backdrop-blur-sm">
          <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
          <span>GREEN WAVE ACTIVE • CORRIDOR 108</span>
        </div>
      )}

      {mode === 'police' && (
        <div className="absolute top-2.5 left-2.5 bg-red-600/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-md">
          Incident: J12 Gandhi Chowk
        </div>
      )}
    </div>
  );
};
