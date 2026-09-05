import { fetchApi } from './client'

export interface Citation {
  citation_id: number
  document_id: string
  document_filename: string
  page_number?: number | null
  section?: string | null
  chunk_id: string
  chunk_index: number
  similarity_score: number
  content_snippet: string
}

export interface RAGQueryRequest {
  query: string
  top_k?: number
  similarity_threshold?: number | null
  document_ids?: string[] | null
  document_type?: string | null
}

export interface RAGQueryResponse {
  query: string
  answer: string
  citations: Citation[]
  retrieved_chunks_count: number
  has_sufficient_context: boolean
  model_info: {
    provider: string
    model: string
  }
}

export async function queryRAG(payload: RAGQueryRequest): Promise<RAGQueryResponse> {
  return fetchApi<RAGQueryResponse>('/api/rag/query', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
