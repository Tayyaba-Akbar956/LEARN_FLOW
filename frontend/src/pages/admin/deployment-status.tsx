import React, { useState, useEffect } from 'react';
import Head from 'next/head';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  latency: number | null;
  lastChecked: string;
}

const DeploymentStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Chat Service', status: 'loading', latency: null, lastChecked: '-' },
    { name: 'Code Execution', status: 'loading', latency: null, lastChecked: '-' },
    { name: 'Exercise Engine', status: 'loading', latency: null, lastChecked: '-' },
    { name: 'Teacher Portal', status: 'loading', latency: null, lastChecked: '-' },
  ]);

  useEffect(() => {
    // Mocking status check
    const timer = setTimeout(() => {
      setServices([
        { name: 'Chat Service', status: 'healthy', latency: 45, lastChecked: new Date().toLocaleTimeString() },
        { name: 'Code Execution', status: 'healthy', latency: 120, lastChecked: new Date().toLocaleTimeString() },
        { name: 'Exercise Engine', status: 'healthy', latency: 85, lastChecked: new Date().toLocaleTimeString() },
        { name: 'Teacher Portal', status: 'unhealthy', latency: null, lastChecked: new Date().toLocaleTimeString() },
      ]);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <Head>
        <title>Admin - Deployment Status | LearnFlow</title>
      </Head>

      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            Deployment Status
          </h1>
          <p className="text-gray-400 mt-2">Monitor the health and performance of LearnFlow microservices.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {services.map((service) => (
            <div 
              key={service.name} 
              className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg transition-transform hover:scale-[1.02]"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-100">{service.name}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  service.status === 'healthy' ? 'bg-green-500/20 text-green-400 border border-green-500/50' :
                  service.status === 'unhealthy' ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                  'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50 animate-pulse'
                }`}>
                  {service.status}
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Latency</span>
                  <span className="font-mono">{service.latency !== null ? `${service.latency}ms` : '-'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Last Checked</span>
                  <span className="text-gray-300">{service.lastChecked}</span>
                </div>
              </div>

              {service.status === 'healthy' && (
                <div className="mt-6 h-1 w-full bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-green-500 w-full opacity-50"></div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-12 p-6 bg-blue-900/20 border border-blue-500/30 rounded-xl">
          <h2 className="text-lg font-semibold text-blue-300 mb-2">System Insights</h2>
          <p className="text-sm text-gray-400">
            All services are currently operational within expected parameters except for the Teacher Portal, 
            which is experiencing intermittent connectivity issues in the stagging environment.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DeploymentStatus;
