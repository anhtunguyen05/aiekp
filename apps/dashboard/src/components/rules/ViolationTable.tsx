'use client';

import React from 'react';
import { Warning, ArrowSquareOut, XCircle } from '@phosphor-icons/react';
import { useDispatch } from 'react-redux';
import { setSelectedNodeId, setZoomToNodeId } from '@/store/graphSlice';
import { RuleViolation } from '@/lib/api-types';

// ---------------------------------------------------------------------------
// Rule type display helpers
// ---------------------------------------------------------------------------

const RULE_LABELS: Record<string, string> = {
  'no-circular-deps': 'Circular Dep',
  'max-fan-in': 'High Fan-In',
  'max-fan-out': 'High Fan-Out',
  'no-cross-layer': 'Cross-Layer',
  'max-complexity': 'High Complexity',
};

const RULE_COLORS: Record<string, string> = {
  'no-circular-deps': 'text-red-400 bg-red-500/10',
  'max-fan-in': 'text-orange-400 bg-orange-500/10',
  'max-fan-out': 'text-amber-400 bg-amber-500/10',
  'no-cross-layer': 'text-pink-400 bg-pink-500/10',
  'max-complexity': 'text-violet-400 bg-violet-500/10',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface ViolationTableProps {
  violations: RuleViolation[];
  totalViolations: number;
  rulesRun: string[];
}

export function ViolationTable({ violations, totalViolations, rulesRun }: ViolationTableProps) {
  const dispatch = useDispatch();

  if (violations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="p-4 rounded-2xl bg-emerald-500/10 text-emerald-400 mb-4">
          <Warning size={32} weight="duotone" />
        </div>
        <p className="text-sm font-medium text-zinc-300">No violations found</p>
        <p className="text-xs text-zinc-500 mt-1">
          All {rulesRun.length} rule(s) passed on the current Knowledge Graph.
        </p>
      </div>
    );
  }

  // Group violations by rule type
  const grouped = violations.reduce<Record<string, RuleViolation[]>>((acc, v) => {
    const key = v.rule_type;
    if (!acc[key]) acc[key] = [];
    acc[key].push(v);
    return acc;
  }, {});

  const handleNodeClick = (nodeId: string) => {
    dispatch(setSelectedNodeId(nodeId));
    dispatch(setZoomToNodeId(nodeId));
  };

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center justify-between px-1">
        <p className="text-xs text-zinc-400">
          <span className="font-semibold text-red-400">{totalViolations}</span> violation
          {totalViolations !== 1 ? 's' : ''} across {rulesRun.length} rule
          {rulesRun.length !== 1 ? 's' : ''}
        </p>
        <p className="text-xs text-zinc-600">Click any row to jump to node →</p>
      </div>

      {/* Per-rule groups */}
      {Object.entries(grouped).map(([ruleType, items]) => {
        const colorCls = RULE_COLORS[ruleType] ?? 'text-zinc-400 bg-zinc-700/30';
        const label = RULE_LABELS[ruleType] ?? ruleType;

        return (
          <div key={ruleType} className="rounded-2xl border border-white/8 overflow-hidden">
            {/* Group header */}
            <div className="flex items-center gap-2 px-4 py-2.5 bg-zinc-800/60 border-b border-white/8">
              <span className={`px-2 py-0.5 rounded-md text-xs font-semibold ${colorCls}`}>
                {label}
              </span>
              <span className="text-xs text-zinc-500 ml-auto">{items.length} node(s)</span>
            </div>

            {/* Violation rows */}
            <div className="divide-y divide-white/5">
              {items.map((v, idx) => (
                <button
                  key={`${v.node_id}-${idx}`}
                  onClick={() => handleNodeClick(v.node_id)}
                  className="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-white/5 transition-colors group"
                >
                  <XCircle
                    size={16}
                    weight="fill"
                    className="text-red-500 shrink-0 mt-0.5"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-zinc-200 truncate">
                        {v.node_label}
                      </span>
                      <span className="text-xs text-zinc-600 shrink-0 hidden sm:block">
                        {v.node_type}
                      </span>
                    </div>
                    <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">{v.detail}</p>
                    <p className="text-xs text-zinc-700 font-mono truncate mt-0.5">{v.node_id}</p>
                  </div>
                  <ArrowSquareOut
                    size={14}
                    className="text-zinc-600 group-hover:text-indigo-400 transition-colors shrink-0 mt-1"
                  />
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
