"use client";

import UserProfile from '@/components/UserProfile';
import ChatBox from '@/components/ChatBox';

export default function NewHireView() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-4">
      
      {/* LEFT SIDE: Assistant Context & User Profile */}
      <div className="lg:col-span-1 flex flex-col gap-6">
        
        {/* Premium Welcome Card */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-8 rounded-2xl shadow-xl text-white relative overflow-hidden">
          {/* Subtle background decoration */}
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/5 rounded-full blur-2xl"></div>
          
          <div className="flex items-center gap-4 mb-6 relative z-10">
            <div className="w-12 h-12 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-white font-bold backdrop-blur-sm">
              AI
            </div>
            <h2 className="text-2xl font-bold tracking-tight">HR Co-Worker</h2>
          </div>
          <p className="text-slate-300 text-sm leading-relaxed relative z-10">
            Welcome to your enterprise portal. I am connected to the company's secure database. Ask me about onboarding, software access, and corporate policies.
          </p>
        </div>

        <UserProfile />
      </div>

      {/* RIGHT SIDE: The Main AI Chat Interface */}
      <div className="lg:col-span-2">
        <ChatBox />
      </div>
    </div>
  );
}