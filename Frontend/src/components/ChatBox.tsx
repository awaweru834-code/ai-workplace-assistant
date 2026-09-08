"use client";

import { useState, useEffect, useRef } from 'react';
import { getChatHistory, sendChatMessage } from '@/services/api';

// 1. Updated to match your backend's exact dictionary keys
interface ChatMessage {
  id?: string | number;
  role: string;
  content: string;
  session?: string;
}

export default function ChatBox() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await getChatHistory();
        setMessages(history || []);
      } catch (error) {
        console.error("Failed to load chat history", error);
      }
    };
    loadHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // 2. Map input to the new 'content' key
    const newMsg: ChatMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, newMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await sendChatMessage(newMsg.content);
      // We look for common AI response keys, defaulting to response.content
      const replyText = response.content || response.reply || response; 
      setMessages((prev) => [...prev, { role: 'assistant', content: replyText }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Error connecting to AI.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-[700px] border border-gray-200 rounded-xl bg-white shadow-sm overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
        {messages.length === 0 && (
          <p className="text-center text-gray-400 mt-10">No message history. Say hello to your AI HR Co-Worker!</p>
        )}
        
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-sm shadow-md' 
                : 'bg-white text-gray-800 rounded-bl-sm shadow-sm border border-gray-200'
            }`}>
              {/* 3. Render 'content' instead of 'text' to prevent the React crash */}
              {msg.content}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 text-gray-500 p-4 rounded-2xl rounded-bl-sm text-sm animate-pulse shadow-sm">
              AI is formulating a response...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-100 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about HR policies..."
          className="flex-1 bg-gray-100 border-transparent rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 transition"
          disabled={isTyping}
        />
        <button 
          type="submit" 
          disabled={isTyping || !input.trim()}
          className="bg-blue-600 text-white px-6 py-3 rounded-full hover:bg-blue-700 disabled:opacity-50 transition font-medium shadow-md"
        >
          Send
        </button>
      </form>
    </div>
  );
}