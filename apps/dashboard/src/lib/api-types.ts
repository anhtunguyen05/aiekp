export interface AffectedNode {
  id: string;
  type: string;
  label: string;
  depth: number;
  via_relation: string;
}

export interface ImpactAnalysisResponse {
  source_node: { id: string; type: string; label: string };
  affected: AffectedNode[];
}
