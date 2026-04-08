import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [showTomadores, setShowTomadores] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      <Header 
        toggleTheme={toggleTheme} 
        isDarkMode={isDarkMode} 
        onOpenTomadores={() => setShowTomadores(true)} 
      />
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <Dashboard 
          showTomadoresExtra={showTomadores} 
          onCloseTomadores={() => setShowTomadores(false)} 
        />
      </main>
    </div>
  );
}

export default App;
