import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { LoadingSpinner } from '../common/LoadingSpinner';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // For demo purposes, we can bypass actual API call if needed
    // In a real app we'd await login
    try {
      if (email === 'admin@visiondna.com' && password === 'admin') {
        // Mock successful login
        useAuthStore.setState({
          user: { id: '1', email, name: 'Admin', role: 'ADMIN' },
          token: 'mock-token',
          isAuthenticated: true
        });
        navigate('/');
      } else {
        await login({ email, password });
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid credentials. Try admin@visiondna.com / admin');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] relative">
      <div className="absolute inset-0 bg-slate-950/80 z-0"></div>
      
      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-blue-600 mb-2">
          VisionDNA
        </h2>
        <h2 className="mt-2 text-2xl font-bold text-slate-100 italic opacity-80">
          Digital Twin Monitoring
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-slate-900 border border-slate-700/50 py-8 px-4 shadow rounded-xl sm:px-10 backdrop-blur-sm">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Email address
              </label>
              <div className="mt-1">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-slate-700 bg-slate-800 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-100"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300">
                Password
              </label>
              <div className="mt-1">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-slate-700 bg-slate-800 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-100"
                />
              </div>
            </div>

            {error && (
              <div className="text-red-500 text-sm bg-red-500/10 p-2 rounded border border-red-500/20 text-center">
                {error}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2.5 mt-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:ring-offset-slate-900 disabled:opacity-50"
              >
                {isLoading ? <LoadingSpinner size="sm" /> : 'Log in'}
              </button>
            </div>
          </form>
          
          <div className="mt-6 text-center text-xs text-slate-500">
            Hint: admin@visiondna.com / admin
          </div>
        </div>
      </div>
    </div>
  );
}
