import { fetchApi } from './client'

export interface SearchQueryRequest {
  query: string
  top_k?: number
  similarity_threshold?: number | null
  document_ids?: string[] | null
  document_type?: string | null
}

export interface RetrievedChunk {
  id: string
  document_id: string
  document_filename: string
  document_type: string
  chunk_index: number
  content: string
  similarity_score: number
  distance: number
  metadata?: {
    page_number?: number
    section?: string
    block_type?: string
    is_table?: boolean
    table_index?: number
    table_headers?: string[]
    character_length?: number
    token_count?: number
    [key: string]: unknown
  } | null
}

export interface SearchQueryResponse {
  query: string
  total_results: number
  top_k: number
  similarity_threshold?: number | null
  results: RetrievedChunk[]
}

export async function searchRetrieval(
  payload: SearchQueryRequest
): Promise<SearchQueryResponse> {
  return fetchApi<SearchQueryResponse>('/api/retrieval/search', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
