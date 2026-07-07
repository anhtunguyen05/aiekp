'use client';

import React, { useState } from 'react';
import { ShieldWarning, Play, ArrowClockwise } from '@phosphor-icons/react';
import { useDispatch } from 'react-redux';
import { useCheckRulesMutation } from '@/store/api/aiekpApi';
import { setViolationNodeIds, clearViolations } from '@/store/graphSlice';
import { RuleType, RuleViolation } from '@/lib/api-types';
import { RuleList, buildDefaultConfigs, toRuleDefinitions } from '@/components/rules/RuleList';
import { ViolationTable } from '@/components/rules/ViolationTable';

export default function RulesPage() {
  const dispatch = useDispatch();
  const [checkRules, { isLoading }] = useCheckRulesMutation();

  // Rule configuration state
  const [configs, setConfigs] = useState(buildDefaultConfigs());

  // Audit result state
  const [violations, setViolations] = useState<RuleViolation[]>([]);
  const [totalViolations, setTotalViolations] = useState(0);
  const [rulesRun, setRulesRun] = useState<string[]>([]);
  const [hasRun, setHasRun] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const enabledCount = Object.values(configs).filter((c) => c.enabled).length;

  // -------------------------------------------------------------------------
  // Handlers
  // -------------------------------------------------------------------------

  const handleToggle = (type: RuleType) => {
    setConfigs((prev) => ({
      ...prev,
      [type]: { ...prev[type], enabled: !prev[type].enabled },
    }));
  };

  const handleThresholdChange = (type: RuleType, value: number) => {
    setConfigs((prev) => ({
      ...prev,
      [type]: { ...prev[type], threshold: value },
    }));
  };

  const handleParamChange = (
    type: RuleType,
    key: 'sourcePattern' | 'targetPattern',
    value: string
  ) => {
    setConfigs((prev) => ({
      ...prev,
      [type]: { ...prev[type], [key]: value },
    }));
  };

  const handleRunAudit = async () => {
    const rules = toRuleDefinitions(configs);
    if (rules.length === 0) return;

    setError(null);
    dispatch(clearViolations());

    try {
      const result = await checkRules(rules).unwrap();
      setViolations(result.violations);
      setTotalViolations(result.total_violations);
      setRulesRun(result.rules_run);
      setHasRun(true);

      // Push violation node IDs to Redux so the graph can highlight them
      const violatedIds = [
        ...new Set(result.violations.map((v) => v.node_id).filter((id) => id !== '__error__')),
      ];
      dispatch(setViolationNodeIds(violatedIds));
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'data' in err
          ? (err as { data: { detail: string } }).data?.detail
          : 'Failed to connect to the API. Is the backend running?';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  const handleClear = () => {
    setViolations([]);
    setTotalViolations(0);
    setRulesRun([]);
    setHasRun(false);
    setError(null);
    dispatch(clearViolations());
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100">
      {/* ------------------------------------------------------------------ */}
      {/* Header */}
      {/* ------------------------------------------------------------------ */}
      <header className="flex items-center gap-4 px-6 py-4 border-b border-white/10 bg-zinc-900/60 backdrop-blur-md shrink-0">
        <div className="p-2.5 rounded-xl bg-red-500/15 text-red-400">
          <ShieldWarning size={22} weight="duotone" />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight">Architectural Rule Engine</h1>
          <p className="text-xs text-zinc-500">
            Define architecture rules and detect violations across your Knowledge Graph.
          </p>
        </div>

        <div className="ml-auto flex items-center gap-2">
          {hasRun && (
            <button
              onClick={handleClear}
              className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              <ArrowClockwise size={16} />
              Clear
            </button>
          )}
          <button
            onClick={handleRunAudit}
            disabled={isLoading || enabledCount === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-700 disabled:text-zinc-500 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Running…
              </>
            ) : (
              <>
                <Play size={16} weight="fill" />
                Run Audit{enabledCount > 0 ? ` (${enabledCount})` : ''}
              </>
            )}
          </button>
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Body: two-column layout */}
      {/* ------------------------------------------------------------------ */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Rule configuration */}
        <aside className="w-96 shrink-0 border-r border-white/10 overflow-y-auto p-5 bg-zinc-900/30">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-4">
            Rules Configuration
          </p>
          <RuleList
            configs={configs}
            onToggle={handleToggle}
            onThresholdChange={handleThresholdChange}
            onParamChange={handleParamChange}
          />
        </aside>

        {/* Right: Results */}
        <main className="flex-1 overflow-y-auto p-5">
          {/* Error banner */}
          {error && (
            <div className="mb-5 flex items-start gap-3 px-4 py-3 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              <ShieldWarning size={18} className="shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          {!hasRun && !error && (
            <div className="flex flex-col items-center justify-center h-full text-center py-20 opacity-50">
              <ShieldWarning size={48} weight="thin" className="text-zinc-600 mb-4" />
              <p className="text-sm text-zinc-500">
                Enable rules on the left and click <strong>Run Audit</strong> to start.
              </p>
            </div>
          )}

          {hasRun && !error && (
            <>
              <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-4">
                Audit Results
              </p>
              <ViolationTable
                violations={violations}
                totalViolations={totalViolations}
                rulesRun={rulesRun}
              />
            </>
          )}
        </main>
      </div>
    </div>
  );
}
