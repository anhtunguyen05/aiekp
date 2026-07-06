import ELK from 'elkjs/lib/elk.bundled.js';
import { Node as RFNode, Edge as RFEdge } from '@xyflow/react';
import { MarkerType } from '@xyflow/react';

const elk = new ELK();

/** Compute ELK layout. Automatically generates parent→child edges for hierarchy. */
export async function computeElkLayout(
  nodes: RFNode[],
  edges: RFEdge[],
): Promise<{ nodes: RFNode[]; edges: RFEdge[] }> {
  if (nodes.length === 0) return { nodes, edges };

  // ── Build a map of parentId → children ──────────────────────────────────
  const childrenOf = new Map<string, string[]>();
  nodes.forEach(n => {
    const pid = n.data?.parentId as string | undefined;
    if (pid) {
      if (!childrenOf.has(pid)) childrenOf.set(pid, []);
      childrenOf.get(pid)!.push(n.id);
    }
  });

  // ── Synthesize hierarchy edges (Directory→File, File→Class, etc.) ────────
  // These are visual-only edges that help ELK space things correctly and
  // give the user a clear visual connector between parent and children.
  const syntheticEdgeMap = new Map<string, RFEdge>();
  nodes.forEach(n => {
    const pid = n.data?.parentId as string | undefined;
    if (!pid) return;
    const edgeId = `hier::${pid}→${n.id}`;
    if (syntheticEdgeMap.has(edgeId)) return;

    const parentNode = nodes.find(p => p.id === pid);
    const parentType = parentNode?.data?.type as string | undefined;

    // Pick colors per relationship
    const isDir = parentType === 'Directory';
    const isFile = parentType === 'File';

    syntheticEdgeMap.set(edgeId, {
      id: edgeId,
      source: pid,
      target: n.id,
      type: 'smoothstep',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: isDir ? '#f59e0b' : isFile ? '#60a5fa' : '#a78bfa',
        width: 14,
        height: 14,
      },
      style: {
        stroke: isDir ? '#f59e0b' : isFile ? '#60a5fa' : '#a78bfa',
        strokeWidth: 1.5,
        strokeDasharray: isDir ? '6,4' : undefined,
        opacity: 0.6,
      },
    });
  });

  // Merge hierarchy edges with caller-supplied edges (hierarchy first so they
  // appear under data edges visually)
  const allEdges: RFEdge[] = [
    ...Array.from(syntheticEdgeMap.values()),
    ...edges.filter(e => !syntheticEdgeMap.has(e.id)),
  ];

  // ── ELK layout options ───────────────────────────────────────────────────
  // Larger spacing so siblings are clearly separated, especially when a
  // sibling group is expanded to show its children.
  const elkOptions = {
    'elk.algorithm': 'layered',
    'elk.direction': 'DOWN',
    'elk.edgeRouting': 'ORTHOGONAL',
    'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',
    // Spacing between siblings on the same layer
    'elk.spacing.nodeNode': '150',
    // Spacing between layers (depth levels)
    'elk.layered.spacing.nodeNodeBetweenLayers': '200',
    // Extra padding so edges have room to route without overlapping nodes
    'elk.layered.spacing.edgeNodeBetweenLayers': '40',
    'elk.spacing.edgeEdge': '20',
    'elk.spacing.edgeNode': '20',
    // Minimize crossings
    'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
  };

  const graph = {
    id: 'root',
    layoutOptions: elkOptions,
    children: nodes.map(n => ({
      id: n.id,
      width: (n.data?.width as number) || 220,
      height: (n.data?.height as number) || 56,
    })),
    edges: allEdges.map(e => ({
      id: e.id,
      sources: [e.source],
      targets: [e.target],
    })),
  };

  try {
    const layoutedGraph = await elk.layout(graph);

    const layoutedNodes = nodes.map(node => {
      const elkNode = layoutedGraph.children?.find(n => n.id === node.id);
      if (elkNode) {
        return { ...node, position: { x: elkNode.x ?? 0, y: elkNode.y ?? 0 } };
      }
      return node;
    });

    return { nodes: layoutedNodes, edges: allEdges };
  } catch (err) {
    console.error('ELK layout error:', err);
    return { nodes, edges: allEdges };
  }
}
