'use client';

import React from 'react';
import { Handle, Position, NodeProps, Node as RFNode } from '@xyflow/react';
import { File, Cube, Function as FnIcon, Minus, Plus, Folder, FolderOpen } from '@phosphor-icons/react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { toggleExpandedNodeId } from '@/store/graphSlice';

// Helper for premium liquid glass styling based on design-taste-frontend
const glassClasses = "bg-zinc-900/60 backdrop-blur-md border border-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.5)]";

// Type definition for node data
export interface CustomNodeData extends Record<string, unknown> {
  label: string;
  type: string;
  originalData: Record<string, unknown>;
  parentId?: string;
  isExpandable?: boolean; // determined if there are edges connecting out to children
}

const BaseNode = ({ selected, children, colorClass }: { data: CustomNodeData, selected: boolean, children: React.ReactNode, colorClass: string }) => {
  return (
    <div className={`relative px-4 py-3 rounded-2xl min-w-[200px] max-w-[280px] transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]
      ${glassClasses}
      ${selected ? `ring-2 ring-offset-2 ring-offset-zinc-950 ${colorClass}` : 'hover:-translate-y-[2px]'}
    `}>
      <Handle type="target" position={Position.Top} className="opacity-0" />
      {children}
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

export const FileNode = ({ data, selected, id }: NodeProps<RFNode<CustomNodeData>>) => {
  const dispatch = useDispatch();
  const isExpanded = useSelector((state: RootState) => state.graph.expandedNodeIds.includes(id));
  
  return (
    <BaseNode data={data} selected={!!selected} colorClass="ring-blue-500">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 rounded-xl bg-blue-500/20 text-blue-400 shrink-0">
            <File size={20} weight="duotone" />
          </div>
          <div className="flex flex-col truncate">
            <span className="text-xs font-semibold tracking-wider text-blue-400 uppercase">File</span>
            <span className="text-sm font-medium text-zinc-100 truncate">{data.label}</span>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            dispatch(toggleExpandedNodeId(id));
          }}
          className="p-1.5 rounded-lg bg-zinc-800/50 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 transition-colors"
        >
          {isExpanded ? <Minus size={16} /> : <Plus size={16} />}
        </button>
      </div>
    </BaseNode>
  );
};

export const ClassNode = ({ data, selected, id }: NodeProps<RFNode<CustomNodeData>>) => {
  const dispatch = useDispatch();
  const isExpanded = useSelector((state: RootState) => state.graph.expandedNodeIds.includes(id));

  return (
    <BaseNode data={data} selected={!!selected} colorClass="ring-purple-500">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400 shrink-0">
            <Cube size={20} weight="duotone" />
          </div>
          <div className="flex flex-col truncate">
            <span className="text-xs font-semibold tracking-wider text-purple-400 uppercase">Class</span>
            <span className="text-sm font-medium text-zinc-100 truncate">{data.label}</span>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            dispatch(toggleExpandedNodeId(id));
          }}
          className="p-1.5 rounded-lg bg-zinc-800/50 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 transition-colors"
        >
          {isExpanded ? <Minus size={16} /> : <Plus size={16} />}
        </button>
      </div>
    </BaseNode>
  );
};

export const FunctionNode = ({ data, selected }: NodeProps<RFNode<CustomNodeData>>) => {
  return (
    <BaseNode data={data} selected={!!selected} colorClass="ring-emerald-500">
      <div className="flex items-center gap-3 overflow-hidden">
        <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 shrink-0">
          <FnIcon size={20} weight="duotone" />
        </div>
        <div className="flex flex-col truncate">
          <span className="text-xs font-semibold tracking-wider text-emerald-400 uppercase">Function</span>
          <span className="text-sm font-medium text-zinc-100 truncate">{data.label}</span>
        </div>
      </div>
    </BaseNode>
  );
};

export const DefaultNode = ({ data, selected }: NodeProps<RFNode<CustomNodeData>>) => {
  return (
    <BaseNode data={data} selected={!!selected} colorClass="ring-zinc-500">
      <div className="flex items-center gap-3 overflow-hidden">
        <div className="p-2 rounded-xl bg-zinc-700/50 text-zinc-400 shrink-0">
          <File size={20} weight="duotone" />
        </div>
        <div className="flex flex-col truncate">
          <span className="text-xs font-semibold tracking-wider text-zinc-400 uppercase">{data.type || 'Node'}</span>
          <span className="text-sm font-medium text-zinc-100 truncate">{data.label}</span>
        </div>
      </div>
    </BaseNode>
  );
};

export const DirectoryNode = ({ data, selected, id }: NodeProps<RFNode<CustomNodeData>>) => {
  const dispatch = useDispatch();
  const isExpanded = useSelector((state: RootState) => state.graph.expandedNodeIds.includes(id));

  return (
    <BaseNode data={data} selected={!!selected} colorClass="ring-amber-500">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
            {isExpanded ? <FolderOpen size={20} weight="duotone" /> : <Folder size={20} weight="duotone" />}
          </div>
          <div className="flex flex-col truncate">
            <span className="text-xs font-semibold tracking-wider text-amber-400 uppercase">Folder</span>
            <span className="text-sm font-medium text-zinc-100 truncate">{data.label}</span>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            dispatch(toggleExpandedNodeId(id));
          }}
          className="p-1.5 rounded-lg bg-zinc-800/50 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 transition-colors shrink-0"
        >
          {isExpanded ? <Minus size={16} /> : <Plus size={16} />}
        </button>
      </div>
    </BaseNode>
  );
};
