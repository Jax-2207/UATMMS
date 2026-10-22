import React from 'react';
import { UserPlus, CheckCircle2 } from 'lucide-react';

export const UsersRolesPage: React.FC = () => {

  const users = [
    { id: 'RD', name: 'Rahul Deshmukh', role: 'System Admin', zone: 'HQ', status: 'Active', lastActive: 'Just now' },
    { id: 'PK', name: 'Priya Kulkarni', role: 'Traffic Operator', zone: 'Zone A', status: 'Active', lastActive: '2 min ago' },
    { id: 'IS', name: 'Insp. S. Patil', role: 'Traffic Police', zone: 'Zone A', status: 'Active', lastActive: '8 min ago' },
    { id: 'DA', name: 'Dr. A. Joshi', role: 'Hospital ER', zone: 'City Hospital', status: 'Active', lastActive: '15 min ago' },
    { id: 'A#', name: 'Ambulance #A1 driver', role: 'Ambulance Driver', zone: 'Fleet 108', status: 'On duty', lastActive: 'Now' },
    { id: 'Fc', name: 'Fire crew #F1', role: 'Firefighter', zone: 'Station 2', status: 'On duty', lastActive: 'Now' },
    { id: 'SM', name: 'Sneha More', role: 'Traffic Operator', zone: 'Zone B', status: 'Invited', lastActive: '—' },
  ];

  const permissions = [
    { name: 'View live map', roles: ['Admin', 'Operator', 'Police', 'Emergency', 'Hospital', 'Public'] },
    { name: 'Control signals', roles: ['Admin', 'Operator'] },
    { name: 'Raise emergency', roles: ['Admin', 'Emergency', 'Hospital'] },
    { name: 'Verify incidents', roles: ['Admin', 'Operator', 'Police'] },
    { name: 'Manage users', roles: ['Admin'] },
    { name: 'Edit policies', roles: ['Admin'] },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Users & Role Permissions</h1>
          <p className="text-slate-400 text-sm">Role-based access control (RBAC) · invite · suspend</p>
        </div>
        <input
          type="text"
          placeholder="Search name, role, zone…"
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm w-64"
        />
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Users List */}
        <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold">Users</h3>
            <span className="text-xs text-slate-400">{users.length} users</span>
          </div>

          <div className="space-y-2 mb-6">
            <div className="grid grid-cols-5 gap-4 px-4 py-2 text-xs font-bold text-slate-400 border-b border-slate-800">
              <div>Name</div>
              <div>Role</div>
              <div>Zone / Org</div>
              <div>Status</div>
              <div>Last active</div>
            </div>

            {users.map((user) => (
              <div key={user.id} className="grid grid-cols-5 gap-4 p-3 bg-slate-800/30 rounded-lg items-center hover:bg-slate-800/50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center font-bold text-xs">
                    {user.id}
                  </div>
                  <span className="text-sm font-medium truncate">{user.name}</span>
                </div>
                <span className="text-sm text-orange-400 font-medium">{user.role}</span>
                <span className="text-sm text-slate-400">{user.zone}</span>
                <span className={`text-xs font-bold px-2 py-1 rounded w-fit ${
                  user.status === 'Active' ? 'bg-emerald-500/20 text-emerald-400' :
                  user.status === 'On duty' ? 'bg-cyan-500/20 text-cyan-400' :
                  'bg-orange-500/20 text-orange-400'
                }`}>
                  {user.status}
                </span>
                <span className="text-sm text-slate-400">{user.lastActive}</span>
              </div>
            ))}
          </div>

          <button className="w-full bg-orange-600 text-white font-bold py-2 rounded-lg hover:bg-orange-700 text-sm flex items-center justify-center gap-2">
            <UserPlus className="w-4 h-4" /> Invite user
          </button>
        </div>

        {/* Invite Form */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4">+ Invite user</h3>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-slate-400 block mb-2">Email</label>
              <input
                type="email"
                placeholder="name@domain.com"
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-2">Role</label>
              <select className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white">
                <option>System Admin</option>
                <option>Traffic Operator</option>
                <option>Traffic Police</option>
                <option>Hospital ER</option>
                <option>Ambulance Driver</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-2">Zone / Organization</label>
              <input
                type="text"
                placeholder="Zone A / City Hospital"
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white"
              />
            </div>
            <button className="w-full bg-orange-600 text-white font-bold py-2 rounded-lg hover:bg-orange-700 text-sm">
              Send invitation
            </button>
          </div>
        </div>
      </div>

      {/* Role Permissions Matrix */}
      <div className="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-semibold">Role Permissions</h3>
          <button className="text-orange-500 text-xs font-bold hover:text-orange-600">Edit</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-4 py-3 text-xs font-bold text-slate-400">Permission</th>
                {['Admin', 'Operator', 'Police', 'Emergency', 'Hospital', 'Public'].map((role) => (
                  <th key={role} className="text-center px-3 py-3 text-xs font-bold text-slate-400">{role}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {permissions.map((perm, idx) => (
                <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                  <td className="px-4 py-3 text-sm text-slate-300">{perm.name}</td>
                  {['Admin', 'Operator', 'Police', 'Emergency', 'Hospital', 'Public'].map((role) => (
                    <td key={role} className="text-center px-3 py-3">
                      {perm.roles.includes(role) ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mx-auto" />
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-xs text-slate-400 mt-6">
          Public users can only view traffic and receive alerts. Emergency roles can raise priority requests but cannot edit signal timing — only the safety engine can.
        </p>
      </div>
    </div>
  );
};
