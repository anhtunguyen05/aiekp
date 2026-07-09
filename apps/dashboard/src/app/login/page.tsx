'use client';

import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { setCredentials } from '@/store/authSlice';
import { useLoginMutation } from '@/store/api/aiekpApi';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const [login, { isLoading }] = useLoginMutation();
  const dispatch = useDispatch();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      const result = await login({ username: email, password }).unwrap();
      
      // The API returns access_token, token_type, role, tenant_id
      if (result.access_token) {
        dispatch(setCredentials({
          token: result.access_token,
          tenant_id: result.tenant_id,
          role: result.role || 'member'
        }));
        
        router.push('/');
      }
    } catch (err: any) {
      setError(err?.data?.detail || 'Lỗi đăng nhập. Vui lòng kiểm tra lại tài khoản.');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-zinc-950 p-4">
      <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-zinc-100">Đăng nhập AIEKP</h1>
          <p className="text-zinc-400 mt-2 text-sm">Nền tảng Quản trị Tri thức Engineering</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-3 bg-red-950/50 border border-red-900 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-300" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-zinc-100 outline-none transition-all"
              placeholder="admin@aiekp.local"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-300" htmlFor="password">Mật khẩu</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-zinc-100 outline-none transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Đăng nhập'}
          </button>
        </form>
      </div>
    </div>
  );
}
