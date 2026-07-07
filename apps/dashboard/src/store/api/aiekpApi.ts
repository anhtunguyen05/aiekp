import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import { ApiNode, ApiEdge } from '@/lib/graph-utils';
import { ImpactAnalysisResponse, RuleDefinition, RuleCheckResponse } from '@/lib/api-types';

interface NodesResponse {
  nodes: ApiNode[];
}

interface EdgesResponse {
  edges: ApiEdge[];
}


export const aiekpApi = createApi({
  reducerPath: 'aiekpApi',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    prepareHeaders: (headers) => {
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      if (apiKey) {
        headers.set('X-API-Key', apiKey);
      }
      return headers;
    },
  }),
  tagTypes: ['Graph', 'Stats'],
  endpoints: (builder) => ({
    getNodes: builder.query<NodesResponse, void>({ 
      query: () => '/graph/nodes',
      providesTags: ['Graph']
    }),
    getEdges: builder.query<EdgesResponse, void>({ 
      query: () => '/graph/edges',
      providesTags: ['Graph']
    }),
    getNodeById: builder.query<unknown, string>({ query: (id) => `/graph/nodes/${encodeURIComponent(id)}` }),
    getImpact: builder.query<ImpactAnalysisResponse, string>({ query: (id) => `/graph/impact/${encodeURIComponent(id)}` }),
    getStats: builder.query<{ nodes_by_label: Record<string, number>; hotspots: { id: string; label: string; impact_score: number; connections: number }[] }, void>({ 
      query: () => '/stats',
      providesTags: ['Stats']
    }),
    checkRules: builder.mutation<RuleCheckResponse, RuleDefinition[]>({
      query: (rules) => ({
        url: '/rules/check',
        method: 'POST',
        body: rules,
      }),
    }),
  }),
})

export const {
  useGetNodesQuery,
  useGetEdgesQuery,
  useGetNodeByIdQuery,
  useGetImpactQuery,
  useGetStatsQuery,
  useCheckRulesMutation,
} = aiekpApi
