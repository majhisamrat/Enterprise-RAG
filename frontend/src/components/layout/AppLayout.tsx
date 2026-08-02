import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { cn } from '@/lib/utils';

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background dot-grid-pattern text-foreground relative overflow-x-hidden selection:bg-primary/20 selection:text-primary transition-colors duration-300">
      {/* Ambient background mesh lighting */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden opacity-60 dark:opacity-100">
        <div className="absolute -top-40 -left-40 w-[700px] h-[700px] bg-primary/10 rounded-full blur-[150px]" />
        <div className="absolute top-1/3 -right-40 w-[700px] h-[700px] bg-purple-600/10 rounded-full blur-[150px]" />
        <div className="absolute -bottom-40 left-1/3 w-[700px] h-[700px] bg-cyan-400/10 rounded-full blur-[150px]" />
      </div>

      <div className="flex min-h-screen relative z-10">
        <Sidebar 
          collapsed={collapsed} 
          onToggle={() => setCollapsed(!collapsed)}
        />

        <main
          className={cn(
            'flex-1 transition-all duration-300 ease-out min-h-screen flex flex-col',
            collapsed ? 'ml-[76px]' : 'ml-72',
          )}
        >
          <div className="p-6 md:p-10 max-w-[1600px] w-full mx-auto flex-1 flex flex-col">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
