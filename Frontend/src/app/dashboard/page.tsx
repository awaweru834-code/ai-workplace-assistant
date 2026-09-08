"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import HrAdminView from '@/components/HrAdminView';
import NewHireView from '@/components/NewHireView';

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  // Route protection: Kick unauthenticated users back to login
  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  // Prevent rendering if user is null while the redirect happens
  if (!user) return null;

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Enterprise HR Portal</h1>
        <span className="px-4 py-2 bg-gray-200 text-gray-700 rounded-full text-sm font-bold uppercase tracking-wider">
          Role: {user.role.replace('_', ' ')}
        </span>
      </header>

      {/* The Dynamic Role Router */}
      {user.role === 'hr_admin' ? <HrAdminView /> : <NewHireView />}
    </main>
  );
}