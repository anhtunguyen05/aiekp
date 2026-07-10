"use client";

import { useState } from "react";
import { FolderGit2, Search, Play } from "lucide-react";
import { RepositoryProgress } from "@/components/repositories/RepositoryProgress";
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

export default function RepositoriesPage() {
  const [repoPath, setRepoPath] = useState("");
  const [activeScan, setActiveScan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const token = useSelector((state: RootState) => state.auth.token);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoPath.trim()) return;

    setError(null);
    try {
      const res = await fetch("http://localhost:8000/ingest/", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ repo_path: repoPath.trim() }),
      });

      const data = await res.json();
      if (!res.ok || data.status === "error") {
        setError(data.message || "Failed to start ingestion");
        return;
      }

      setActiveScan(repoPath.trim());
    } catch (err) {
      console.error(err);
      setError("Failed to communicate with API server.");
    }
  };

  return (
    <div className="flex flex-col h-full w-full overflow-y-auto custom-scrollbar bg-zinc-950 p-8">
      <div className="max-w-4xl mx-auto w-full space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 flex items-center gap-2">
            <FolderGit2 className="text-amber-500" /> Repository Management
          </h1>
          <p className="text-zinc-400 mt-2 text-sm">
            Ingest and scan source code repositories into the Knowledge Graph.
          </p>
        </div>

        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-medium text-zinc-200 mb-4 flex items-center gap-2">
            <Search size={18} /> New Scan
          </h2>
          <form onSubmit={handleScan} className="flex gap-4">
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="e.g. /path/to/repo or D:\projects\repo"
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-zinc-100 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600 transition-colors"
            />
            <button
              type="submit"
              disabled={!repoPath.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play size={16} fill="currentColor" /> Scan Now
            </button>
          </form>
          {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
        </div>

        {activeScan && (
          <div className="space-y-4">
            <h2 className="text-lg font-medium text-zinc-200">Active Scan</h2>
            <RepositoryProgress repoPath={activeScan} />
          </div>
        )}
      </div>
    </div>
  );
}
