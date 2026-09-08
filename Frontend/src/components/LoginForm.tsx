"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { loginUser } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const { setUser } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const decoded = await loginUser(username, password);
      
      setUser(decoded);
      router.push('/dashboard');
      
    } catch (err) {
      setError('Login failed. Check your credentials.');
    }
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="p-10 bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl rounded-2xl w-96 flex flex-col gap-5"
    >
      <h2 className="text-3xl font-bold text-white mb-2 text-center tracking-wide">Portal Login</h2>
      
      {error && (
        <p className="text-red-200 bg-red-900/50 p-3 rounded-lg text-sm text-center border border-red-500/30">
          {error}
        </p>
      )}
      
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="border border-white/20 bg-white/10 p-3 rounded-xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
        required
      />
      
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="border border-white/20 bg-white/10 p-3 rounded-xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
        required
      />
      
      <button 
        type="submit" 
        className="bg-blue-600 text-white p-3 rounded-xl font-semibold hover:bg-blue-700 transition shadow-lg mt-2"
      >
        Sign In
      </button>
    </form>
  );
}