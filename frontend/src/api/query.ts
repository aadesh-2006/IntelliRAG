import { fetchApi } from './client'
import { Citation } from './rag'

export type RouteType = 'SQL' | 'RAG' | 'HYBRID'

export type QueryIntent =
  | 'DOCUMENT_METADATA'
  | 'DOCUMENT_DATES_EXPIRATION'
  | 'REMINDER_LOOKUP'
  | 'CRICKET_STATISTICS'
  | 'RAG_DOCUMENT_QUESTION'
  | 'DOCUMENT_COMPARISON'
  | 'HYBRID_DOCUMENT_ANALYSIS'
  | 'UNSUPPORTED'

export interface QueryRouterRequest {
  query: string
  document_ids?: string[]
  document_type?: string
  top_k?: number
  similarity_threshold?: number
  force_route?: RouteType
}

export interface QueryRouterResponse {
  query: string
  route: RouteType
  intent: QueryIntent
  confidence: number
  answer: string
  structured_data?: Record<string, any>
  citations?: Citation[]
  retrieved_chunks_count: number
  has_sufficient_context: boolean
  model_info?: Record<string, any>
  execution_time_ms?: number
}

export async function routeQuery(request: QueryRouterRequest): Promise<QueryRouterResponse> {
  return fetchApi<QueryRouterResponse>('/api/query', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
