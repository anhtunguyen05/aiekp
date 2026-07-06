import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { setHighlightedNodeIds, setSelectedNodeId } from '@/store/graphSlice';
import { ChevronDown, ChevronRight, Layers, FileCode, SearchCode, Folder } from 'lucide-react';
export interface EvidenceSource {
  id: string;
  type: string;
  label: string;
  snippet?: string;
}

interface EvidenceProps {
  sources: EvidenceSource[];
}

export function EvidencePanel({ sources }: EvidenceProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const dispatch = useDispatch();

  if (!sources || sources.length === 0) return null;

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'File': return <FileCode size={14} className="text-blue-400" />;
      case 'Class': return <Layers size={14} className="text-purple-400" />;
      case 'Function': return <SearchCode size={14} className="text-emerald-400" />;
      default: return <Folder size={14} className="text-amber-400" />;
    }
  };

  const handleEvidenceClick = (nodeId: string) => {
    dispatch(setHighlightedNodeIds([nodeId]));
    dispatch(setSelectedNodeId(nodeId));
  };

  return (
    <div className="mt-4 border border-zinc-800 rounded-lg overflow-hidden bg-zinc-950/50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 bg-zinc-900/50 hover:bg-zinc-800/80 transition-colors text-sm font-medium text-zinc-300"
      >
        <span className="flex items-center gap-2">
          {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          Evidence ({sources.length} sources)
        </span>
      </button>

      {isExpanded && (
        <div className="p-3 space-y-2 border-t border-zinc-800">
          {sources.map((source, idx) => (
            <div
              key={`${source.id}-${idx}`}
              onClick={() => handleEvidenceClick(source.id)}
              className="p-3 rounded-md bg-zinc-900 border border-zinc-800 hover:border-zinc-600 cursor-pointer transition-colors"
            >
              <div className="flex items-center gap-2 mb-1">
                {getNodeIcon(source.type)}
                <span className="text-sm font-medium text-zinc-200">{source.label || source.id}</span>
                <span className="ml-auto text-xs text-zinc-500 bg-zinc-950 px-2 py-0.5 rounded-full border border-zinc-800">
                  {source.type}
                </span>
              </div>
              {source.snippet && (
                <div className="mt-2 text-xs text-zinc-400 font-mono bg-zinc-950 p-2 rounded overflow-x-auto whitespace-pre-wrap">
                  {source.snippet}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
