"use client";

import { useState, useRef } from 'react';
import { uploadPolicyDocument } from '@/services/api';

export default function UploadDropzone() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.type !== 'application/pdf') {
        setStatus({ type: 'error', message: 'Only PDF files are supported.' });
        setFile(null);
        return;
      }
      setFile(selected);
      setStatus({ type: '', message: '' });
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setStatus({ type: '', message: '' });

    try {
      await uploadPolicyDocument(file);
      setStatus({ type: 'success', message: `${file.name} was successfully ingested into the AI database.` });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (error) {
      setStatus({ type: 'error', message: 'Upload failed. Ensure the backend RAG pipeline is running.' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
      <h3 className="text-xl font-bold text-slate-900 mb-2">Policy Ingestion</h3>
      <p className="text-slate-500 text-sm mb-6">Upload company PDFs to update the HR Assistant's knowledge base.</p>

      {status.message && (
        <div className={`p-4 mb-6 rounded-lg text-sm border ${
          status.type === 'success' ? 'bg-green-50 text-green-800 border-green-200' : 'bg-red-50 text-red-800 border-red-200'
        }`}>
          {status.message}
        </div>
      )}

      {/* Dropzone Area */}
      <div 
        className="border-2 border-dashed border-slate-300 rounded-xl p-10 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <span className="text-4xl mb-4 opacity-50">📄</span>
        <p className="text-slate-700 font-medium mb-1">Click to select a PDF document</p>
        <p className="text-slate-400 text-xs">Maximum file size: 10MB</p>
        
        <input 
          type="file" 
          accept="application/pdf"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* Selected File Details & Upload Button */}
      {file && (
        <div className="mt-6 p-4 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-sm font-medium text-slate-800">{file.name}</span>
            <span className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
          </div>
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
          >
            {isUploading ? 'Ingesting...' : 'Upload & Train AI'}
          </button>
        </div>
      )}
    </div>
  );
}