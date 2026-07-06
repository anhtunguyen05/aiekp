'use client';

import React, { useMemo } from 'react';
import { useGetNodesQuery, useGetEdgesQuery } from '@/store/api/aiekpApi';
import { useDispatch } from 'react-redux';
import { clearSelection } from '@/store/graphSlice';
import { buildReactFlowGraph } from '@/lib/graph-utils';
import dynamic from 'next/dynamic';
import { NodeDetailPanel } from './NodeDetailPanel';
import { SearchBar } from './SearchBar';

const GraphCanvas = dynamic(() => import('./GraphCanvas').then((mod) => mod.GraphCanvas), { ssr: false });

export function KnowledgeGraph() {
  const { data: nodesData, isLoading: isLoadingNodes } = useGetNodesQuery();
  const { data: edgesData, isLoading: isLoadingEdges } = useGetEdgesQuery();
  const dispatch = useDispatch();

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        dispatch(clearSelection());
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [dispatch]);

  const graphData = useMemo(() => {
    if (!nodesData?.nodes || !edgesData?.edges) return null;
    return buildReactFlowGraph(nodesData.nodes, edgesData.edges);
  }, [nodesData, edgesData]);

  if (isLoadingNodes || isLoadingEdges) {
    return (
      <div className="flex items-center justify-center h-full w-full bg-zinc-950 text-zinc-400">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="font-medium text-zinc-300">Loading Architecture View...</p>
        </div>
      </div>
    );
  }

  if (!graphData) {
    return null;
  }

  return (
    <div className="relative w-full h-full flex bg-zinc-950">
      <div className="flex-1 relative overflow-hidden">
        <GraphCanvas initialNodes={graphData.nodes} initialEdges={graphData.edges} />
        <div className="absolute top-4 left-4 w-80 z-10">
          <SearchBar />
        </div>
      </div>
      <NodeDetailPanel nodes={graphData.nodes} />
    </div>
  );
}
