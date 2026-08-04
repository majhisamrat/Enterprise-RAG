import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { cn } from '@/lib/utils';

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="app-aurora min-h-screen bg-[radial-gradient(circle_at_16%_14%,rgba(255,174,68,.72),transparent_23%),radial-gradient(circle_at_89%_10%,rgba(233,83,151,.70),transparent_28%),radial-gradient(circle_at_48%_94%,rgba(120,62,227,.58),transparent_45%),linear-gradient(135deg,#7563ed_0%,#b949c5_48%,#fc6a76_100%)] text-foreground relative overflow-x-hidden selection:bg-primary/20 selection:text-primary transition-colors duration-300">
      {/* Ambient background mesh lighting */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden opacity-80 dark:opacity-100">
        <div className="absolute -top-40 -left-40 w-[700px] h-[700px] bg-amber-300/25 rounded-full blur-[150px]" />
        <div className="absolute top-1/3 -right-40 w-[700px] h-[700px] bg-fuchsia-400/25 rounded-full blur-[150px]" />
        <div className="absolute -bottom-40 left-1/3 w-[700px] h-[700px] bg-violet-300/35 rounded-full blur-[150px]" />
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
          <div className="p-5 md:p-8 lg:p-10 max-w-[1600px] w-full mx-auto flex-1 flex flex-col min-h-0">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
