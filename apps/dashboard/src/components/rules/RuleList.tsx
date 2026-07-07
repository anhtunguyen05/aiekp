'use client';

import React from 'react';
import { ShieldCheck, ArrowsClockwise, ArrowFatLineDown, ArrowFatLineUp, ArrowsLeftRight, GitFork } from '@phosphor-icons/react';
import { RuleDefinition, RuleType } from '@/lib/api-types';

// ---------------------------------------------------------------------------
// Static rule metadata
// ---------------------------------------------------------------------------

interface RuleMeta {
  type: RuleType;
  label: string;
  description: string;
  icon: React.ReactNode;
  defaultThreshold?: number;
  hasThreshold: boolean;
  hasParams: boolean;
}

const RULE_METADATA: RuleMeta[] = [
  {
    type: 'no-circular-deps',
    label: 'No Circular Dependencies',
    description: 'Detect nodes that participate in a circular dependency cycle.',
    icon: <ArrowsClockwise size={20} weight="duotone" />,
    hasThreshold: false,
    hasParams: false,
  },
  {
    type: 'max-fan-in',
    label: 'Max Fan-In',
    description: 'Flag nodes with too many incoming connections (hotspot detection).',
    icon: <ArrowFatLineDown size={20} weight="duotone" />,
    defaultThreshold: 10,
    hasThreshold: true,
    hasParams: false,
  },
  {
    type: 'max-fan-out',
    label: 'Max Fan-Out',
    description: 'Flag nodes that depend on too many others (high coupling).',
    icon: <ArrowFatLineUp size={20} weight="duotone" />,
    defaultThreshold: 10,
    hasThreshold: true,
    hasParams: false,
  },
  {
    type: 'no-cross-layer',
    label: 'No Cross-Layer Imports',
    description:
      'Detect direct dependencies that violate your layer architecture (e.g. UI → DB).',
    icon: <ArrowsLeftRight size={20} weight="duotone" />,
    hasThreshold: false,
    hasParams: true,
  },
  {
    type: 'max-complexity',
    label: 'Max Complexity',
    description: 'Flag files / modules that contain too many direct children.',
    icon: <GitFork size={20} weight="duotone" />,
    defaultThreshold: 20,
    hasThreshold: true,
    hasParams: false,
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface RuleConfig {
  enabled: boolean;
  threshold: number;
  sourcePattern: string;
  targetPattern: string;
}

type RuleConfigMap = Record<RuleType, RuleConfig>;

interface RuleListProps {
  configs: RuleConfigMap;
  onToggle: (type: RuleType) => void;
  onThresholdChange: (type: RuleType, value: number) => void;
  onParamChange: (type: RuleType, key: 'sourcePattern' | 'targetPattern', value: string) => void;
}

export function RuleList({ configs, onToggle, onThresholdChange, onParamChange }: RuleListProps) {
  return (
    <div className="space-y-3">
      {RULE_METADATA.map((meta) => {
        const cfg = configs[meta.type];
        return (
          <div
            key={meta.type}
            className={`rounded-2xl border transition-all duration-200 ${
              cfg.enabled
                ? 'border-indigo-500/50 bg-indigo-500/5'
                : 'border-white/10 bg-zinc-900/40'
            }`}
          >
            {/* Rule header */}
            <div className="flex items-center gap-4 p-4">
              {/* Toggle */}
              <button
                onClick={() => onToggle(meta.type)}
                className={`w-10 h-6 rounded-full transition-colors duration-200 relative shrink-0 ${
                  cfg.enabled ? 'bg-indigo-500' : 'bg-zinc-700'
                }`}
                aria-label={`Toggle ${meta.label}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 ${
                    cfg.enabled ? 'translate-x-5' : 'translate-x-1'
                  }`}
                />
              </button>

              {/* Icon + Text */}
              <div
                className={`p-2 rounded-xl shrink-0 ${
                  cfg.enabled ? 'bg-indigo-500/20 text-indigo-400' : 'bg-zinc-800 text-zinc-500'
                }`}
              >
                {meta.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`font-medium text-sm ${cfg.enabled ? 'text-zinc-100' : 'text-zinc-400'}`}>
                  {meta.label}
                </p>
                <p className="text-xs text-zinc-500 mt-0.5 truncate">{meta.description}</p>
              </div>
            </div>

            {/* Threshold input */}
            {cfg.enabled && meta.hasThreshold && (
              <div className="px-4 pb-4 flex items-center gap-3 border-t border-white/5 pt-3">
                <label className="text-xs text-zinc-400 whitespace-nowrap">Threshold (N):</label>
                <input
                  type="number"
                  min={1}
                  value={cfg.threshold}
                  onChange={(e) => onThresholdChange(meta.type, Number(e.target.value))}
                  className="w-24 px-3 py-1.5 rounded-lg bg-zinc-800 border border-white/10 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            )}

            {/* Cross-layer pattern inputs */}
            {cfg.enabled && meta.hasParams && (
              <div className="px-4 pb-4 space-y-2 border-t border-white/5 pt-3">
                <div className="flex items-center gap-3">
                  <label className="text-xs text-zinc-400 w-28 shrink-0">Source pattern:</label>
                  <input
                    type="text"
                    value={cfg.sourcePattern}
                    placeholder=".*/ui/.*|.*/components/.*"
                    onChange={(e) => onParamChange(meta.type, 'sourcePattern', e.target.value)}
                    className="flex-1 px-3 py-1.5 rounded-lg bg-zinc-800 border border-white/10 text-xs text-zinc-100 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <label className="text-xs text-zinc-400 w-28 shrink-0">Target pattern:</label>
                  <input
                    type="text"
                    value={cfg.targetPattern}
                    placeholder=".*/db/.*|.*/models/.*"
                    onChange={(e) => onParamChange(meta.type, 'targetPattern', e.target.value)}
                    className="flex-1 px-3 py-1.5 rounded-lg bg-zinc-800 border border-white/10 text-xs text-zinc-100 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Legend */}
      <div className="flex items-center gap-2 text-xs text-zinc-500 pt-1">
        <ShieldCheck size={14} className="text-indigo-400" />
        <span>{RULE_METADATA.filter((m) => configs[m.type].enabled).length} rule(s) active</span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helper: build initial config map
// ---------------------------------------------------------------------------

export function buildDefaultConfigs(): RuleConfigMap {
  return Object.fromEntries(
    RULE_METADATA.map((m) => [
      m.type,
      {
        enabled: false,
        threshold: m.defaultThreshold ?? 10,
        sourcePattern: '.*/ui/.*|.*/components/.*|.*/pages/.*|.*/app/.*',
        targetPattern: '.*/db/.*|.*/database/.*|.*/models/.*|.*/prisma/.*',
      },
    ])
  ) as RuleConfigMap;
}

// ---------------------------------------------------------------------------
// Helper: convert config map → RuleDefinition[]
// ---------------------------------------------------------------------------

export function toRuleDefinitions(configs: RuleConfigMap): RuleDefinition[] {
  return RULE_METADATA.filter((m) => configs[m.type].enabled).map((m) => {
    const cfg = configs[m.type];
    const rule: RuleDefinition = { type: m.type };
    if (m.hasThreshold) rule.threshold = cfg.threshold;
    if (m.hasParams) {
      rule.params = {
        source_pattern: cfg.sourcePattern,
        target_pattern: cfg.targetPattern,
      };
    }
    return rule;
  });
}
