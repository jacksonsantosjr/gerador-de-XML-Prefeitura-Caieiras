import React from 'react';
import { Database, FileCode2, Sun, Moon } from 'lucide-react';

export default function Header({ toggleTheme, isDarkMode }) {
  return (
    <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm sticky top-0 z-10 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="bg-emerald-100 dark:bg-emerald-900/30 p-2 rounded-md">
              <FileCode2 className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h1 className="text-xl font-bold text-slate-800 dark:text-white tracking-tight">
              Conversor RPS <span className="text-emerald-600 dark:text-emerald-400">&gt; XML</span>
            </h1>
          </div>
          <nav className="flex items-center space-x-2 sm:space-x-4">
            <button className="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white px-3 py-2 rounded-sm text-sm font-medium transition-colors" title="Tela atual de envio de planilhas">
              Faturamento
            </button>
            <button className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center space-x-1 px-3 py-2 rounded-sm text-sm font-medium transition-colors" title="Visualização do seu banco de dados de clientes (Supabase) - Em breve">
              <Database className="h-4 w-4 mr-1" />
              <span className="hidden sm:inline">Tomadores</span>
            </button>
            <div className="pl-4 border-l border-slate-200 dark:border-slate-700 ml-2">
               <button onClick={toggleTheme} className="p-2 rounded-md text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                 {isDarkMode ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
               </button>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
