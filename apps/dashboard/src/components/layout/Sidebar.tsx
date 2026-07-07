import Link from 'next/link';
import { Search, MessageSquare, FolderGit2, ShieldAlert, FileText } from 'lucide-react';

export function Sidebar() {
  return (
    <div className="w-64 bg-zinc-900 text-white h-screen flex flex-col border-r border-zinc-800">
      <div className="p-4 border-b border-zinc-800">
        <h1 className="text-xl font-bold tracking-tight">AIEKP</h1>
        <p className="text-xs text-zinc-400">Knowledge Graph Dashboard</p>
      </div>
      <nav className="flex-1 py-4">
        <ul className="space-y-1 px-2">
          <li>
            <Link href="/" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-sm">
              <Search size={18} />
              <span>Knowledge Graph</span>
            </Link>
          </li>
          <li>
            <Link href="/chat" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-sm">
              <MessageSquare size={18} />
              <span>AI Chat</span>
            </Link>
          </li>
          <li>
            <Link href="/repositories" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-sm">
              <FolderGit2 size={18} />
              <span>Repositories</span>
            </Link>
          </li>
          <li>
            <Link href="/rules" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-sm">
              <ShieldAlert size={18} />
              <span>Rules Engine</span>
            </Link>
          </li>
          <li>
            <Link href="/docs" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-sm">
              <FileText size={18} />
              <span>Docs Generator</span>
            </Link>
          </li>
        </ul>
      </nav>
      <div className="p-4 text-xs text-zinc-500 border-t border-zinc-800">
        v1.0.0
      </div>
    </div>
  );
}
