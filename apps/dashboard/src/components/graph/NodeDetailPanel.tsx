'use client';

import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { useGetImpactQuery, useGetNodesQuery } from '@/store/api/aiekpApi';
import { setSelectedNodeId, setHighlightedNodeIds } from '@/store/graphSlice';
import { Node as RFNode } from '@xyflow/react';
import { AffectedNode } from '@/lib/api-types';
import { Layers, FileCode, SearchCode, Folder } from 'lucide-react';

export function NodeDetailPanel({ nodes }: { nodes: RFNode[] }) {
  const dispatch = useDispatch();
  const selectedNodeId = useSelector((state: RootState) => state.graph.selectedNodeId);
  const highlightedNodeIds = useSelector((state: RootState) => state.graph.highlightedNodeIds);

  const { data: impactData, isLoading: isLoadingImpact, refetch } = useGetImpactQuery(selectedNodeId as string, {
    skip: !selectedNodeId,
  });
  const { isLoading: isLoadingNodes } = useGetNodesQuery();

  if (!selectedNodeId) {
    if (isLoadingNodes) {
      return (
        <div className="w-96 bg-zinc-900 border-l border-zinc-800 h-full overflow-y-auto flex flex-col shadow-xl z-20">
          <div className="p-4 border-b border-zinc-800 bg-zinc-950/50">
            <div className="h-6 w-3/4 bg-zinc-800 rounded animate-pulse mb-2"></div>
            <div className="h-4 w-1/4 bg-zinc-800 rounded animate-pulse"></div>
          </div>
          <div className="p-4 border-b border-zinc-800 space-y-3">
            <div className="h-4 w-1/3 bg-zinc-800 rounded animate-pulse"></div>
            <div className="h-10 w-full bg-zinc-800 rounded animate-pulse"></div>
          </div>
          <div className="p-4 space-y-4 flex-1">
            <div className="h-4 w-1/4 bg-zinc-800 rounded animate-pulse mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i}>
                  <div className="h-3 w-1/4 bg-zinc-800 rounded animate-pulse mb-1"></div>
                  <div className="h-4 w-full bg-zinc-800 rounded animate-pulse"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }
    return null;
  }

  const selectedNode = nodes.find(n => n.id === selectedNodeId);
  const originalData = selectedNode?.data?.originalData as any;
  const nodeLabel = selectedNode?.data?.label as string;

  const handleAnalyzeImpact = () => {
    if (impactData?.affected) {
      dispatch(setHighlightedNodeIds(impactData.affected.map((n) => n.id)));
    } else {
      refetch().then((res) => {
        if (res.data?.affected) {
          dispatch(setHighlightedNodeIds(res.data.affected.map((n) => n.id)));
        }
      });
    }
  };

  const handleClearImpact = () => {
    dispatch(setHighlightedNodeIds([]));
  };

  const handleExportMarkdown = () => {
    if (!impactData || !impactData.affected.length) return;
    
    let mdContent = `# Impact Analysis for ${impactData.source_node.label}\n\n`;
    mdContent += `**Type**: ${impactData.source_node.type}\n`;
    mdContent += `**ID**: \`${impactData.source_node.id}\`\n\n`;
    
    const maxDepth = Math.max(...impactData.affected.map(n => n.depth));
    for (let d = 1; d <= maxDepth; d++) {
      const nodesAtDepth = impactData.affected.filter(n => n.depth === d);
      if (nodesAtDepth.length > 0) {
        mdContent += `## Depth ${d} (${d === 1 ? 'Direct' : 'Indirect'})\n\n`;
        nodesAtDepth.forEach(n => {
          mdContent += `- **${n.label}** (\`${n.type}\`) via _${n.via_relation}_\n`;
        });
        mdContent += '\n';
      }
    }
    
    const blob = new Blob([mdContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `impact-analysis-${nodeLabel || 'node'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'File': return <FileCode size={14} className="text-blue-400" />;
      case 'Class': return <Layers size={14} className="text-purple-400" />;
      case 'Function': return <SearchCode size={14} className="text-emerald-400" />;
      default: return <Folder size={14} className="text-amber-400" />;
    }
  };

  // Group affected nodes by depth
  const affectedByDepth = impactData?.affected ? impactData.affected.reduce((acc, node) => {
    if (!acc[node.depth]) acc[node.depth] = [];
    acc[node.depth].push(node);
    return acc;
  }, {} as Record<number, AffectedNode[]>) : {};

  return (
    <div className="w-96 bg-zinc-900 border-l border-zinc-800 h-full overflow-y-auto flex flex-col shadow-xl z-20">
      <div className="p-4 border-b border-zinc-800 bg-zinc-950/50">
        <h2 className="text-lg font-semibold text-white break-all">
          {nodeLabel || selectedNodeId}
        </h2>
        <div className="mt-1 flex items-center gap-2">
          <span className="inline-flex items-center rounded-full bg-zinc-800 px-2 py-1 text-xs font-medium text-zinc-300">
            {originalData?.type || 'Unknown'}
          </span>
        </div>
      </div>

      <div className="p-4 border-b border-zinc-800">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-3">Actions</h3>
        
        {originalData?.type === 'Directory' ? (
          <div className="text-sm text-zinc-500 italic text-center p-2 bg-zinc-950/50 rounded-md border border-zinc-800">
            Impact analysis is not available for directory nodes.
          </div>
        ) : (
          <>
            {highlightedNodeIds.length > 0 ? (
              <button
                onClick={handleClearImpact}
                className="w-full flex justify-center py-2 px-4 border border-zinc-700 rounded-md shadow-sm text-sm font-medium text-white bg-zinc-800 hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-zinc-500"
              >
                Clear Impact Analysis
              </button>
            ) : (
              <button
                onClick={handleAnalyzeImpact}
                disabled={isLoadingImpact || (impactData && impactData.affected.length === 0)}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:bg-zinc-700 disabled:text-zinc-400"
              >
                {isLoadingImpact 
                  ? 'Analyzing...' 
                  : (impactData && impactData.affected.length === 0 
                      ? 'No Impact Found' 
                      : 'Analyze Impact')}
              </button>
            )}
            
            {/* Remove the redundant text below since it's now on the disabled button */}
          </>
        )}
      </div>

      {highlightedNodeIds.length > 0 && impactData?.affected && impactData.affected.length > 0 && (
        <div className="p-4 border-b border-zinc-800">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Affected Nodes</h3>
            <button 
              onClick={handleExportMarkdown}
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Export .md
            </button>
          </div>
          <div className="space-y-4">
            {Object.entries(affectedByDepth).map(([depth, nodes]) => (
              <div key={depth}>
                <h4 className="text-xs font-semibold text-zinc-500 mb-2">
                  Depth {depth} {Number(depth) === 1 ? '(Direct)' : '(Indirect)'}
                </h4>
                <ul className="space-y-2">
                  {nodes.map(node => (
                    <li 
                      key={node.id}
                      className="flex flex-col gap-1 p-2 rounded bg-zinc-950/50 hover:bg-zinc-800/80 cursor-pointer border border-zinc-800/50"
                      onClick={() => dispatch(setSelectedNodeId(node.id))}
                    >
                      <div className="flex items-center gap-2">
                        {getNodeIcon(node.type)}
                        <span className="text-sm font-medium text-zinc-200 truncate" title={node.label}>{node.label}</span>
                      </div>
                      <div className="flex justify-between items-center pl-6">
                        <span className="text-xs text-zinc-500">{node.type}</span>
                        <span className="text-[10px] bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-400 font-mono">
                          via {node.via_relation}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="p-4 flex-1">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-3">Properties</h3>
        <dl className="space-y-3">
          {originalData?.properties && Object.entries(originalData.properties).map(([key, value]) => (
            <div key={key} className="break-all">
              <dt className="text-xs text-zinc-500">{key}</dt>
              <dd className="text-sm text-zinc-200 mt-1">
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}
