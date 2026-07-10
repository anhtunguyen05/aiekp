'use client';

import { Sidebar } from './Sidebar';
import { usePathname } from 'next/navigation';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === '/login';

  return (
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden text-zinc-50 font-sans">
      {!isLoginPage && <Sidebar />}
      <main className="flex-1 h-full relative overflow-hidden">
        {children}
      </main>
    </div>
  );
}
