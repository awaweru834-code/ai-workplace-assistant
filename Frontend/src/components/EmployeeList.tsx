"use client";

import { useState, useEffect } from 'react';
import { getAllUsers, deactivateUser } from '@/services/api';

interface User {
  id: number;
  username: string;
  role: string;
  is_active?: boolean; // We add this optionally, just in case your FastAPI backend supports it
}

export default function EmployeeList() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  
  // 1. New local state to track which buttons have been clicked during this session
  const [deactivatedIds, setDeactivatedIds] = useState<number[]>([]);

  const fetchUsers = async () => {
    try {
      const data = await getAllUsers();
      setUsers(data);
    } catch (error) {
      console.error("Failed to fetch users", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleDeactivate = async (userId: number) => {
    try {
      // Call the API bridge
      await deactivateUser(userId);
      
      // 2. Instantly update the UI state so the button changes text and locks
      setDeactivatedIds((prev) => [...prev, userId]);
      
    } catch (error) {
      console.error("Failed to deactivate user", error);
    }
  };

  if (loading) return <div className="text-gray-500 animate-pulse p-4">Loading employee database...</div>;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 border-b pb-3 mb-4">Employee Database</h3>
      <ul className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
        {users.map((user) => {
          // 3. Check if the user is deactivated (either from a backend flag or our local click state)
          const isDeactivated = user.is_active === false || deactivatedIds.includes(user.id);

          return (
            <li key={user.id} className="flex justify-between items-center p-4 bg-gray-50 border border-gray-200 rounded-md">
              <div>
                <p className="font-medium text-gray-900">{user.username}</p>
                <p className="text-xs text-gray-500 capitalize">{user.role.replace('_', ' ')}</p>
              </div>
              
              {/* 4. Conditional styling and disabled attribute based on the deactivated status */}
              <button 
                onClick={() => handleDeactivate(user.id)}
                disabled={isDeactivated}
                className={`text-sm px-4 py-1.5 rounded transition font-medium ${
                  isDeactivated 
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                    : 'bg-red-100 text-red-600 hover:bg-red-200 shadow-sm'
                }`}
              >
                {isDeactivated ? 'Deactivated' : 'Deactivate'}
              </button>
            </li>
          );
        })}
        {users.length === 0 && <p className="text-gray-500 text-sm">No users found.</p>}
      </ul>
    </div>
  );
}