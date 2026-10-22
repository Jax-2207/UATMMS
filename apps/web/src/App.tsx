import { useState } from 'react';
import { LoginPage } from './pages/LoginPage';
import { AdminOverviewPage } from './pages/AdminOverviewPage';
import { AdminAnalyticsPage } from './pages/AdminAnalyticsPage';
import { SafetyPoliciesPage } from './pages/SafetyPoliciesPage';
import { UsersRolesPage } from './pages/UsersRolesPage';
import { OperatorLiveMapPage } from './pages/OperatorLiveMapPage';
import { HospitalCoordinationPage } from './pages/HospitalCoordinationPage';
import { Sidebar } from './components/Sidebar';

type ConsoleRole = 'admin' | 'operator' | 'police' | 'hospital' | null;
type PageId = 'login' | 'overview' | 'analytics' | 'safety' | 'users' | 'live-map' | 'emergency' | 'incidents' | 'signal-control' | 'command-view' | 'incident-queue' | 'coordination';

function App() {
  const [role, setRole] = useState<ConsoleRole>(null);
  const [currentPage, setCurrentPage] = useState<PageId>('overview');

  const handleSelectRole = (selectedRole: 'operator' | 'admin' | 'police' | 'hospital') => {
    setRole(selectedRole);
    
    // Set default page for each role
    switch (selectedRole) {
      case 'admin':
        setCurrentPage('overview');
        break;
      case 'operator':
        setCurrentPage('live-map');
        break;
      case 'police':
        setCurrentPage('command-view');
        break;
      case 'hospital':
        setCurrentPage('coordination');
        break;
    }
  };



  if (!role) {
    return <LoginPage onSelectRole={handleSelectRole} />;
  }

  const renderPage = () => {
    switch (role) {
      case 'admin':
        switch (currentPage) {
          case 'overview': return <AdminOverviewPage />;
          case 'analytics': return <AdminAnalyticsPage />;
          case 'safety': return <SafetyPoliciesPage />;
          case 'users': return <UsersRolesPage />;
          default: return <AdminOverviewPage />;
        }
      
      case 'operator':
        switch (currentPage) {
          case 'live-map': return <OperatorLiveMapPage />;
          default: return <OperatorLiveMapPage />;
        }
      
      case 'police':
        return <div className="p-8 text-white text-2xl">Police Console - Under Development</div>;
      
      case 'hospital':
        switch (currentPage) {
          case 'coordination': return <HospitalCoordinationPage />;
          default: return <HospitalCoordinationPage />;
        }
      
      default:
        return <AdminOverviewPage />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-950">
      <Sidebar 
        role={role} 
        currentPage={currentPage} 
        onNavigate={(page) => setCurrentPage(page as PageId)}
        userName={role === 'admin' ? 'Rahul Deshmukh' : role === 'operator' ? 'Priya Kulkarni' : role === 'police' ? 'Insp. S. Patil' : 'Dr. A. Joshi'}
      />
      
      <div className="flex-1 overflow-auto">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;
