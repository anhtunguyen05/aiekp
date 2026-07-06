"use client";

import { useEffect, useState } from "react";
import StatsCard from "./StatsCard";
import { File, Box, Braces, Link, Database, RefreshCw, Trash2 } from "lucide-react";
import { useGetStatsQuery, aiekpApi } from "@/store/api/aiekpApi";
import { useDispatch } from "react-redux";

export function DashboardOverlay() {
  const { data, isLoading: loading, refetch } = useGetStatsQuery();
  const dispatch = useDispatch();

  const handleRefresh = () => {
    refetch();
    dispatch(aiekpApi.util.invalidateTags(["Graph"]));
  };

  const handleClearGraph = async () => {
    if (!confirm("Are you sure you want to clear the entire Knowledge Graph? This action cannot be undone.")) return;
    try {
      await fetch("http://127.0.0.1:8000/graph/", {
        method: "DELETE",
        headers: {
          "x-api-key": "aiekp-dev-key"
        }
      });
      handleRefresh();
    } catch (err) {
      console.error("Failed to clear graph:", err);
    }
  };

  if (loading || !data) return null;

  return (
    <div className="absolute top-4 right-4 flex flex-col gap-4 pointer-events-none z-10 w-64 max-h-[calc(100vh-2rem)] overflow-y-auto custom-scrollbar">
      {/* Action Bar */}
      <div className="flex justify-end pointer-events-auto gap-2">
        <button
          onClick={handleClearGraph}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-red-900/50 text-red-200 hover:bg-red-800 hover:text-white rounded-md border border-red-800/50 transition-colors shadow-sm"
          title="Clear Knowledge Graph"
        >
          <Trash2 size={14} /> Clear
        </button>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white rounded-md border border-zinc-700 transition-colors shadow-sm"
          title="Refresh Dashboard Data"
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Overview Stats */}
      <div className="flex flex-col gap-3 pointer-events-auto">
        <StatsCard
          title="Total Files"
          value={data.nodes_by_label["File"] || 0}
          icon={<File size={20} />}
        />
        <StatsCard
          title="Total Classes"
          value={data.nodes_by_label["Class"] || 0}
          icon={<Box size={20} />}
        />
        <StatsCard
          title="Total Functions"
          value={data.nodes_by_label["Function"] || 0}
          icon={<Braces size={20} />}
        />
      </div>

      {/* Complexity Hotspots */}
      {data.hotspots && data.hotspots.length > 0 && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 backdrop-blur-sm p-4 pointer-events-auto">
          <h3 className="text-zinc-400 font-medium text-sm flex items-center gap-2 mb-3">
            <Link size={16} /> Complexity Hotspots
          </h3>
          <ul className="space-y-3">
            {data.hotspots.map((hotspot: any) => (
              <li key={hotspot.id} className="flex justify-between items-center text-sm">
                <span className="text-zinc-300 truncate w-40" title={hotspot.label}>
                  {hotspot.label}
                </span>
                <span className="text-zinc-500 text-xs px-2 py-1 bg-zinc-800 rounded">
                  {hotspot.connections} conn
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
