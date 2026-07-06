'use client';

import React, { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node as RFNode,
  Edge as RFEdge,
  ReactFlowProvider,
  useReactFlow,
  BackgroundVariant,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { setSelectedNodeId, clearSelection, expandNodes } from '@/store/graphSlice';
import { FileNode, ClassNode, FunctionNode, DefaultNode, DirectoryNode } from './nodes/CustomNodes';
import { computeElkLayout } from '@/lib/elk-layout';

const nodeTypes = {
  custom: DefaultNode,
  Directory: DirectoryNode,
  File: FileNode,
  Class: ClassNode,
  Function: FunctionNode,
};

interface GraphCanvasProps {
  initialNodes: RFNode[];
  initialEdges: RFEdge[];
}

function FlowCanvas({ initialNodes, initialEdges }: GraphCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<RFNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<RFEdge>([]);

  const dispatch = useDispatch();
  const { fitView } = useReactFlow();

  const expandedNodeIds = useSelector((state: RootState) => state.graph.expandedNodeIds);
  const selectedNodeId = useSelector((state: RootState) => state.graph.selectedNodeId);
  const highlightedNodeIds = useSelector((state: RootState) => state.graph.highlightedNodeIds);
  const searchQuery = useSelector((state: RootState) => state.graph.searchQuery);

  useEffect(() => {
    const computeLayout = async () => {
      // ─────────────────────────────────────────────
      // 1. Decide which nodes are visible
      //    Root nodes (no parentId) are always visible.
      //    A child becomes visible when its direct parent is both
      //    visible AND listed in expandedNodeIds.
      // ─────────────────────────────────────────────
      const expandedSet = new Set<string>(expandedNodeIds);
      const visibleIds = new Set<string>(
        initialNodes.filter(n => !n.data.parentId).map(n => n.id)
      );

      let changed = true;
      while (changed) {
        changed = false;
        initialNodes.forEach(n => {
          const pid = n.data.parentId as string | undefined;
          if (!visibleIds.has(n.id) && pid && visibleIds.has(pid) && expandedSet.has(pid)) {
            visibleIds.add(n.id);
            changed = true;
          }
        });
      }

      // ─────────────────────────────────────────────
      // 2. Build the visible node list
      // ─────────────────────────────────────────────
      const visibleNodes: RFNode[] = initialNodes
        .filter(n => visibleIds.has(n.id))
        .map(n => ({
          ...n,
          type: (n.data.type as string) in nodeTypes ? (n.data.type as string) : 'custom',
        }));

      // ─────────────────────────────────────────────
      // 3. Build semantic (non-hierarchy) edges with edge-lifting.
      //    Hierarchy edges (Directory→File→Class→Function) are generated
      //    automatically inside computeElkLayout from parentId, so we
      //    only supply the "data relationship" edges here.
      // ─────────────────────────────────────────────
      const getVisibleAncestor = (id: string): string | null => {
        let cur: string | undefined = id;
        while (cur) {
          if (visibleIds.has(cur)) return cur;
          const n = initialNodes.find(n => n.id === cur);
          cur = n?.data.parentId as string | undefined;
        }
        return null;
      };

      const semanticEdgesMap = new Map<string, RFEdge>();

      initialEdges.forEach(e => {
        const rawType = (e.data?.originalData as any)?.type as string;
        // Skip structural edges — they are already covered by parentId hierarchy
        if (rawType === 'DEFINES' || rawType === 'CONTAINS') return;

        const src = getVisibleAncestor(e.source);
        const tgt = getVisibleAncestor(e.target);
        if (!src || !tgt || src === tgt) return;

        const key = `sem::${src}→${tgt}`;
        if (semanticEdgesMap.has(key)) return;

        semanticEdgesMap.set(key, {
          id: key,
          source: src,
          target: tgt,
          type: 'default',
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: '#60a5fa', width: 14, height: 14 },
          style: { stroke: '#60a5fa', strokeWidth: 2, opacity: 0.75 },
          label: rawType,
          labelStyle: { fill: '#93c5fd', fontSize: 10 },
          labelBgStyle: { fill: 'transparent' },
        });
      });

      const semanticEdges = Array.from(semanticEdgesMap.values());

      // ─────────────────────────────────────────────
      // 4. Run ELK layout.
      //    computeElkLayout will inject hierarchy edges (amber dashed for
      //    Directory→*, blue dashed for File→Class/Function) from parentId,
      //    then layout all nodes with generous spacing.
      // ─────────────────────────────────────────────
      const { nodes: laid, edges: laidEdges } = await computeElkLayout(visibleNodes, semanticEdges);

      setNodes(laid);
      setEdges(laidEdges);

      // Fit the view after a short paint delay
      setTimeout(() => fitView({ padding: 0.18, duration: 700 }), 80);
    };

    computeLayout();
  }, [initialNodes, initialEdges, expandedNodeIds, setNodes, setEdges, fitView]);

  // ─────────────────────────────────────────────
  // Highlight / search opacity effects
  // ─────────────────────────────────────────────
  useEffect(() => {
    // Auto-expand parents of highlighted nodes so they become visible
    if (highlightedNodeIds.length > 0) {
      const parentsToExpand = new Set<string>();
      highlightedNodeIds.forEach(id => {
        let cur = initialNodes.find(n => n.id === id)?.data?.parentId as string | undefined;
        while (cur) {
          parentsToExpand.add(cur);
          cur = initialNodes.find(n => n.id === cur)?.data?.parentId as string | undefined;
        }
      });
      if (parentsToExpand.size > 0) {
        dispatch(expandNodes(Array.from(parentsToExpand)));
      }
    }

    setNodes(nds =>
      nds.map(node => {
        const isSelected = node.id === selectedNodeId;
        const isHighlighted = highlightedNodeIds.length > 0
          ? highlightedNodeIds.includes(node.id)
          : false;

        let opacity = 1;
        if (highlightedNodeIds.length > 0 && !isHighlighted && !isSelected) opacity = 0.2;
        if (searchQuery && !(node.data?.label as string || '').toLowerCase().includes(searchQuery.toLowerCase())) opacity = 0.1;

        return {
          ...node,
          selected: isSelected,
          style: { ...node.style, opacity, transition: 'opacity 0.3s ease' },
        };
      })
    );

    setEdges(eds =>
      eds.map(edge => {
        // Keep hierarchy edges (amber/blue dashes) always at full opacity
        const isHierarchy = edge.id.startsWith('hier::');
        let opacity = isHierarchy ? 0.6 : 1;
        if (!isHierarchy && highlightedNodeIds.length > 0) {
          const hit = highlightedNodeIds.includes(edge.source) || highlightedNodeIds.includes(edge.target);
          if (!hit) opacity = 0.1;
        }
        return { ...edge, style: { ...edge.style, opacity, transition: 'opacity 0.3s ease' } };
      })
    );
  }, [selectedNodeId, highlightedNodeIds, searchQuery, setNodes, setEdges]);

  const onNodeClick = useCallback((_event: React.MouseEvent, node: RFNode) => {
    dispatch(setSelectedNodeId(node.id));
  }, [dispatch]);

  const onPaneClick = useCallback(() => {
    dispatch(clearSelection());
  }, [dispatch]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      onPaneClick={onPaneClick}
      nodeTypes={nodeTypes}
      fitView
      className="bg-zinc-950"
      minZoom={0.03}
      maxZoom={2}
    >
      <Background color="#27272a" variant={BackgroundVariant.Dots} gap={20} size={1} />
      <Controls className="bg-zinc-900 border-zinc-800 fill-zinc-400" />
    </ReactFlow>
  );
}

export function GraphCanvas(props: GraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <FlowCanvas {...props} />
    </ReactFlowProvider>
  );
}
