"use client";

import { useEffect, useState } from 'react';
import { getUserProfile } from '@/services/api';

export default function UserProfile() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getUserProfile();
        setProfile(data);
      } catch (err) {
        setError('Failed to load profile data.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []); // The empty array ensures this only runs once on mount

  if (loading) return <div className="text-gray-500 animate-pulse">Loading profile...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="bg-gray-50 p-4 rounded-md border border-gray-200 mt-4">
      <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mb-2">My Profile</h3>
      <ul className="text-sm text-gray-700 space-y-2">
        <li><strong>ID:</strong> {profile?.id}</li>
        <li><strong>Username:</strong> {profile?.username}</li>
        <li><strong>Role:</strong> {profile?.role?.replace('_', ' ')}</li>
        {/* Add any other fields your FastAPI backend returns, like department or email */}
      </ul>
    </div>
  );
}