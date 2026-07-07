export interface AffectedNode {
  id: string;
  type: string;
  label: string;
  depth?: number;
  via_relation: string;
}

export interface ImpactAnalysisResponse {
  source_node: { id: string; type: string; label: string };
  affected: {
    direct: AffectedNode[];
    indirect: AffectedNode[];
  };
  total_count: number;
}

// ---------------------------------------------------------------------------
// Rule Engine types
// ---------------------------------------------------------------------------

export interface RuleDefinition {
  type: RuleType;
  threshold?: number;
  params?: Record<string, string>;
}

export type RuleType =
  | 'no-circular-deps'
  | 'max-fan-in'
  | 'max-fan-out'
  | 'no-cross-layer'
  | 'max-complexity';

export interface RuleViolation {
  rule_type: RuleType;
  node_id: string;
  node_label: string;
  node_type: string;
  detail: string;
}

export interface RuleCheckResponse {
  violations: RuleViolation[];
  total_violations: number;
  rules_run: string[];
}

export type DocType =
  | 'architecture_overview'
  | 'onboarding_guide'
  | 'key_entry_points'
  | 'module_dependencies';

export interface DocGenerateRequest {
  doc_type: DocType;
  session_id?: string;
}
