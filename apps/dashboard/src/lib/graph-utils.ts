import { Node as RFNode, Edge as RFEdge } from '@xyflow/react';

export interface ApiNode {
  id: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface ApiEdge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

// ──────────────────────────────────────────────
// Helpers for path normalization
// ──────────────────────────────────────────────

/** Normalize Windows/POSIX paths to forward-slash and lowercase drive letter */
function normalizePath(p: string): string {
  return p.replace(/\\/g, '/').replace(/^([A-Z]):/, (_, d) => d.toLowerCase() + ':');
}

/** Extract segments from an absolute file path (only directory parts) */
function getPathSegments(filePath: string): string[] {
  const norm = normalizePath(filePath);
  const parts = norm.split('/');
  return parts.slice(0, -1); // everything except the filename itself
}

/** Build a canonical directory ID from a prefix of path segments */
function buildDirId(segments: string[]): string {
  return 'dir::' + segments.join('/');
}

/** Find the common prefix root of all file paths (e.g. "d:/AIEKP") */
function findCommonRoot(filePaths: string[]): string[] {
  if (filePaths.length === 0) return [];
  const first = getPathSegments(normalizePath(filePaths[0]));
  let common = first;
  for (const fp of filePaths) {
    const segs = getPathSegments(normalizePath(fp));
    const maxLen = Math.min(common.length, segs.length);
    let i = 0;
    while (i < maxLen && common[i] === segs[i]) i++;
    common = common.slice(0, i);
  }
  return common;
}

// ──────────────────────────────────────────────
// Main graph builder
// ──────────────────────────────────────────────

export function buildReactFlowGraph(
  nodes: ApiNode[],
  edges: ApiEdge[],
): { nodes: RFNode[]; edges: RFEdge[] } {
  const rfNodes: RFNode[] = [];
  const rfEdges: RFEdge[] = [];

  // ── 1. Filter duplicates: normalize IDs and deduplicate File nodes ──
  const seenFileIds = new Map<string, string>(); // normalized → original id
  const fileNodes = nodes.filter(n => n.type === 'File');
  const deduplicatedFiles = new Set<string>();

  for (const fn of fileNodes) {
    const norm = normalizePath(fn.id);
    if (!seenFileIds.has(norm)) {
      seenFileIds.set(norm, fn.id);
      deduplicatedFiles.add(fn.id);
    }
  }

  // Exclude noisy paths like node_modules
  const EXCLUDED_PATTERNS = ['node_modules'];
  const isExcluded = (id: string) =>
    EXCLUDED_PATTERNS.some(p => normalizePath(id).includes(p));

  const cleanFileNodes = fileNodes.filter(
    n => deduplicatedFiles.has(n.id) && !isExcluded(n.id),
  );

  // ── 2. Build parent map from DEFINES/CONTAINS edges ──
  // For non-file nodes (Class, Function) use the edge-based parentId
  const edgeParentMap = new Map<string, string>();
  edges.forEach(e => {
    if (e.type === 'CONTAINS' || e.type === 'DEFINES') {
      edgeParentMap.set(e.target, e.source);
    }
  });

  // ── 3. Synthesize Directory nodes from File paths ──
  const filePaths = cleanFileNodes.map(n => n.id);
  const commonRoot = findCommonRoot(filePaths);

  // Map: dirId → { label, parentId }
  const dirMeta = new Map<string, { label: string; parentId: string | undefined }>();

  for (const filePath of filePaths) {
    const segs = getPathSegments(normalizePath(filePath));
    // Only create directories BELOW the common root
    for (let depth = commonRoot.length; depth < segs.length; depth++) {
      const dirId = buildDirId(segs.slice(0, depth + 1));
      if (!dirMeta.has(dirId)) {
        const parentId =
          depth > commonRoot.length
            ? buildDirId(segs.slice(0, depth))
            : undefined;
        dirMeta.set(dirId, { label: segs[depth], parentId });
      }
    }
  }

  // Push Directory RF nodes
  for (const [dirId, meta] of dirMeta) {
    rfNodes.push({
      id: dirId,
      position: { x: 0, y: 0 },
      type: 'Directory',
      data: {
        label: meta.label,
        type: 'Directory',
        originalData: null,
        parentId: meta.parentId,
        width: 200,
        height: 52,
      },
    });
  }

  // ── 4. Push File RF nodes (with parentId pointing to their immediate dir) ──
  for (const fileNode of cleanFileNodes) {
    const segs = getPathSegments(normalizePath(fileNode.id));
    const fileName = normalizePath(fileNode.id).split('/').pop() || fileNode.id;

    // Parent dir is the immediate directory above this file
    const parentDirId =
      segs.length > commonRoot.length
        ? buildDirId(segs)
        : undefined;

    rfNodes.push({
      id: fileNode.id,
      position: { x: 0, y: 0 },
      type: 'File',
      data: {
        label: fileName,
        type: 'File',
        originalData: fileNode,
        parentId: parentDirId,
        width: 220,
        height: 56,
      },
    });
  }

  // ── 5. Push Class / Function nodes (parentId from edge map) ──
  const nonFileNodes = nodes.filter(
    n => n.type !== 'File' && !isExcluded(n.id),
  );

  // Deduplicate non-file nodes by normalized ID
  const seenNonFileIds = new Set<string>();
  for (const node of nonFileNodes) {
    const norm = normalizePath(node.id);
    if (seenNonFileIds.has(norm)) continue;
    seenNonFileIds.add(norm);

    // Label = last segment after "::"
    const label = node.id.split('::').pop() || node.id;

    // The parent from the edge map might use a different case → match by normalizing
    const rawParentId = edgeParentMap.get(node.id);
    // Try to find a clean file node whose normalized id matches the raw parent
    let resolvedParentId: string | undefined = rawParentId;
    if (rawParentId) {
      const normParent = normalizePath(rawParentId);
      // Check if it is one of our clean file nodes
      const matchedFile = cleanFileNodes.find(
        f => normalizePath(f.id) === normParent,
      );
      if (matchedFile) {
        resolvedParentId = matchedFile.id;
      }
    }

    rfNodes.push({
      id: node.id,
      position: { x: 0, y: 0 },
      type: node.type as 'Class' | 'Function',
      data: {
        label: label.length > 30 ? label.slice(0, 28) + '…' : label,
        type: node.type,
        originalData: node,
        parentId: resolvedParentId,
        width: node.type === 'Class' ? 200 : 180,
        height: 52,
      },
    });
  }

  // ── 6. Push RF edges (skip structural ones — hierarchy is shown by parentId) ──
  const validNodeIds = new Set(rfNodes.map(n => n.id));
  edges.forEach(edge => {
    if (!validNodeIds.has(edge.source) || !validNodeIds.has(edge.target)) return;

    rfEdges.push({
      id: `${edge.source}→${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'default',
      data: { originalData: edge },
    });
  });

  return { nodes: rfNodes, edges: rfEdges };
}
