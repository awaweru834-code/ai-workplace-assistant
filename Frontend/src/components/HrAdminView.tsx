"use client";

import { useState } from 'react';
import ChatBox from '@/components/ChatBox';
import CreateUserForm from '@/components/CreateUserForm';
import EmployeeList from '@/components/EmployeeList';
import UploadDropzone from '@/components/UploadDropzone';

export default function HrAdminView() {
  const [activeTab, setActiveTab] = useState<'chat' | 'create' | 'list'| 'upload'>('chat');

  // Helper function for elegant tab styling
  const getTabStyle = (tabName: string) => {
    return activeTab === tabName 
      ? 'bg-slate-900 text-white shadow-lg translate-x-1' 
      : 'bg-transparent text-slate-600 hover:bg-slate-100 border border-transparent hover:border-slate-200';
  };

  return (
    <div className="flex flex-col md:flex-row gap-8 mt-4 min-h-[750px]">
      
      {/* LEFT SIDEBAR: Executive Navigation */}
      <div className="w-full md:w-72 flex flex-col gap-3">
        <div className="px-5 py-4 mb-2">
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Admin Controls</h2>
        </div>
        
        <button 
          onClick={() => setActiveTab('chat')}
          className={`text-left px-5 py-4 rounded-xl font-medium transition-all duration-300 ${getTabStyle('chat')}`}
        >
          <div className="flex items-center gap-4">
            <span className="text-xl opacity-80">💬</span> HR Assistant
          </div>
        </button>
        
        <button 
          onClick={() => setActiveTab('create')}
          className={`text-left px-5 py-4 rounded-xl font-medium transition-all duration-300 ${getTabStyle('create')}`}
        >
          <div className="flex items-center gap-4">
            <span className="text-xl opacity-80">✨</span> Account Creation
          </div>
        </button>

        <button 
          onClick={() => setActiveTab('list')}
          className={`text-left px-5 py-4 rounded-xl font-medium transition-all duration-300 ${getTabStyle('list')}`}
        >
          <div className="flex items-center gap-4">
            <span className="text-xl opacity-80">👥</span> Employee Database
          </div>
        </button>


        <button 
          onClick={() => setActiveTab('upload')}
          className={`text-left px-5 py-4 rounded-xl font-medium transition-all duration-300 ${getTabStyle('upload')}`}>
          <div className="flex items-center gap-4">
            <span className="text-xl opacity-80">📁</span> Policy Upload
          </div>
        </button>
      </div>

      {/* RIGHT SIDE CONTENT */}
      <div className="flex-1 bg-white rounded-3xl shadow-sm border border-slate-200 p-2">
        {activeTab === 'chat' && <ChatBox />}
        {activeTab === 'create' && <CreateUserForm />}
        {activeTab === 'list' && <EmployeeList />}
        {activeTab === 'upload' && <UploadDropzone />}
      </div>

    </div>
  );
}