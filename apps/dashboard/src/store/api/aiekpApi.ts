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
    prepareHeaders: (headers, { getState }) => {
      // Access auth token from Redux state
      const token = (getState() as any).auth?.token;
      
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Graph', 'Stats'],
  endpoints: (builder) => ({
    login: builder.mutation<any, any>({
      query: (credentials) => {
        // We use application/x-www-form-urlencoded because OAuth2PasswordRequestForm expects form data
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        return {
          url: '/auth/login',
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        };
      },
    }),
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
  useLoginMutation,
  useGetNodesQuery,
  useGetEdgesQuery,
  useGetNodeByIdQuery,
  useGetImpactQuery,
  useGetStatsQuery,
  useCheckRulesMutation,
} = aiekpApi
