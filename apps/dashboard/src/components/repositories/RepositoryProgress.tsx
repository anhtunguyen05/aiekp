"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { useDispatch } from "react-redux";
import { aiekpApi } from "@/store/api/aiekpApi";

interface RepositoryProgressProps {
  repoPath: string;
}

interface ScanStatus {
  status: "starting" | "running" | "completed" | "error" | "unknown";
  progress: number;
  current_file: string;
  total_files: number;
  processed_files: number;
}

export function RepositoryProgress({ repoPath }: RepositoryProgressProps) {
  const [status, setStatus] = useState<ScanStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!repoPath) return;

    // Use SSE to listen to progress
    const eventSource = new EventSource(
      `http://localhost:8000/ingest/progress?repo_path=${encodeURIComponent(repoPath)}`
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ScanStatus;
        setStatus(data);

        // Close connection if completed or error
        if (data.status === "completed" || data.status === "error") {
          eventSource.close();
          
          if (data.status === "completed") {
            // Invalidate the knowledge graph and stats cache so they refresh when user goes back
            dispatch(aiekpApi.util.invalidateTags(["Graph", "Stats"]));
          }
        }
      } catch (err) {
        console.error("Failed to parse SSE data", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE Error", err);
      setError("Connection to server lost.");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [repoPath]);

  if (!status) {
    return (
      <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg flex items-center justify-center text-zinc-500 text-sm">
        Waiting for scan to start...
      </div>
    );
  }

  return (
    <div className="p-6 bg-zinc-900/50 border border-zinc-800 rounded-xl space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-zinc-200">Scan Progress</h3>
        <div className="flex items-center gap-2 text-sm">
          {status.status === "completed" && (
            <span className="flex items-center gap-1 text-emerald-400">
              <CheckCircle2 size={16} /> Completed
            </span>
          )}
          {(status.status === "running" || status.status === "starting") && (
            <span className="flex items-center gap-1 text-amber-400">
              <Loader2 size={16} className="animate-spin" /> {status.status === "starting" ? "Starting" : "Scanning"}
            </span>
          )}
          {status.status === "error" && (
            <span className="flex items-center gap-1 text-red-400">
              <AlertCircle size={16} /> Error
            </span>
          )}
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-zinc-400">
          <span>{status.processed_files} / {status.total_files} files</span>
          <span>{status.progress}%</span>
        </div>
        <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${status.progress}%` }}
          />
        </div>
      </div>

      {status.current_file && status.status === "running" && (
        <p className="text-xs text-zinc-500 truncate" title={status.current_file}>
          Processing: {status.current_file}
        </p>
      )}

      {error && (
        <p className="text-xs text-red-400 mt-2">{error}</p>
      )}
    </div>
  );
}
