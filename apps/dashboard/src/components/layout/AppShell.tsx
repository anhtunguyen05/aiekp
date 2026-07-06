import { Sidebar } from './Sidebar';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden text-zinc-50 font-sans">
      <Sidebar />
      <main className="flex-1 h-full relative overflow-hidden">
        {children}
      </main>
    </div>
  );
}
