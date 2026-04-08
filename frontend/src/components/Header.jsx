import React from 'react';
import { Database, FileCode2 } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-slate-900 border-b border-slate-800 shadow-sm sticky top-0 z-10 backdrop-blur-md bg-opacity-80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="bg-sastre-teal p-2 rounded-lg bg-opacity-20">
              <FileCode2 className="h-6 w-6 text-emerald-400" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Sastre <span className="text-emerald-400">NFS-e</span>
            </h1>
          </div>
          <nav className="flex space-x-4">
            <button className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
              Faturamento
            </button>
            <button className="text-slate-400 hover:text-white flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              <Database className="h-4 w-4 mr-1" />
              Tomadores
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
