"use client";

import { useState } from 'react';
import { createUser } from '@/services/api';

export default function CreateUserForm() {
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername.trim() || !newPassword.trim()) return;
    
    setIsSubmitting(true);
    setStatus({ type: '', message: '' });

    try {
      await createUser(newUsername, newPassword);
      setStatus({ type: 'success', message: `Account for ${newUsername} created successfully!` });
      setNewUsername('');
      setNewPassword('');
    } catch (error) {
      setStatus({ type: 'error', message: 'Failed to create user. Check permissions or network.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 border-b pb-3 mb-4">Create New Hire Account</h3>
      
      {status.message && (
        <div className={`p-3 mb-4 rounded-md text-sm ${status.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
          {status.message}
        </div>
      )}

      <form onSubmit={handleCreate} className="flex flex-col gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            type="text"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Temporary Password</label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
            required
          />
        </div>
        <button 
          type="submit" 
          disabled={isSubmitting}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition disabled:opacity-50 mt-2 font-medium"
        >
          {isSubmitting ? 'Creating...' : 'Create Account'}
        </button>
      </form>
    </div>
  );
}