import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface GraphState {
  selectedNodeId: string | null;
  highlightedNodeIds: string[];
  searchQuery: string;
  expandedNodeIds: string[];
  zoomToNodeId: string | null;
  violationNodeIds: string[];  // Rule Engine: nodes with architecture violations
}

const initialState: GraphState = {
  selectedNodeId: null,
  highlightedNodeIds: [],
  searchQuery: '',
  expandedNodeIds: [],
  zoomToNodeId: null,
  violationNodeIds: [],
}

export const graphSlice = createSlice({
  name: 'graph',
  initialState,
  reducers: {
    setSelectedNodeId: (state, action: PayloadAction<string | null>) => {
      state.selectedNodeId = action.payload;
    },
    setHighlightedNodeIds: (state, action: PayloadAction<string[]>) => {
      state.highlightedNodeIds = action.payload;
    },
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
    },
    toggleExpandedNodeId: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      if (state.expandedNodeIds.includes(id)) {
        state.expandedNodeIds = state.expandedNodeIds.filter(n => n !== id);
      } else {
        state.expandedNodeIds.push(id);
      }
    },
    expandNodes: (state, action: PayloadAction<string[]>) => {
      const newIds = action.payload.filter(id => !state.expandedNodeIds.includes(id));
      if (newIds.length > 0) {
        state.expandedNodeIds.push(...newIds);
      }
    },
    clearSelection: (state) => {
      state.selectedNodeId = null;
      state.highlightedNodeIds = [];
    },
    setZoomToNodeId: (state, action: PayloadAction<string | null>) => {
      state.zoomToNodeId = action.payload;
    },
    setViolationNodeIds: (state, action: PayloadAction<string[]>) => {
      state.violationNodeIds = action.payload;
    },
    clearViolations: (state) => {
      state.violationNodeIds = [];
    },
  },
})

export const { setSelectedNodeId, setHighlightedNodeIds, setSearchQuery, toggleExpandedNodeId, expandNodes, clearSelection, setZoomToNodeId, setViolationNodeIds, clearViolations } = graphSlice.actions

export default graphSlice.reducer
