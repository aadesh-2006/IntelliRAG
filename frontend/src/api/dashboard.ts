import { fetchApi } from './client'
import { DocumentItem } from './documents'

export interface DashboardStats {
  total_documents: number
  processed_documents: number
  processing_documents: number
  failed_documents: number
  ready_documents: number
  uploaded_documents: number
  embedding_documents: number
  total_chunks: number
  total_storage_bytes: number
  documents_by_status: Record<string, number>
  documents_by_type: Record<string, number>
  documents_by_file_type: Record<string, number>
  recent_documents: DocumentItem[]
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchApi<DashboardStats>('/api/dashboard/stats', {
    method: 'GET',
  })
}
