import { fetchApi } from './client'
import { authStorage } from './authStorage'

export type DocumentType = 'INVOICE' | 'BALANCE_SHEET' | 'P_AND_L' | 'CRICKET_BROCHURE' | 'GENERAL'

export interface BoundingBox {
  x0: number
  y0: number
  x1: number
  y1: number
  page_number: number
}

export interface TableCell {
  row_index: number
  col_index: number
  content: string
  bbox?: BoundingBox
}

export interface TableRow {
  row_index: number
  cells: TableCell[]
}

export interface TableBlock {
  table_index: number
  page_number: number
  headers: string[]
  rows: TableRow[]
  caption?: string
  bbox?: BoundingBox
}

export interface TextBlock {
  block_id: string
  block_type: string
  text: string
  page_number: number
  bbox?: BoundingBox
  confidence?: number
}

export interface DocumentPage {
  page_number: number
  width?: number
  height?: number
  text_blocks: TextBlock[]
  tables: TableBlock[]
  has_ocr: boolean
}

export interface ExtractedMetadata {
  document_id: string
  processor: string
  page_count: number
  total_text_blocks: number
  total_tables: number
  full_text: string
  pages: DocumentPage[]
  metadata: Record<string, unknown>
  processed_at: string
}

export interface DocumentItem {
  id: string
  user_id: string
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  status: 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'EMBEDDING' | 'READY' | 'FAILED' | string
  document_type: DocumentType | string
  processed_at?: string
  processing_error?: string
  created_at: string
  updated_at: string
}

export interface DocumentContentResponse {
  document_id: string
  filename: string
  original_filename: string
  status: string
  document_type: string
  processed_at?: string
  processing_error?: string
  extracted_text?: string
  extracted_metadata?: ExtractedMetadata
}

export interface DocumentListResponse {
  items: DocumentItem[]
  total: number
  limit: number
  offset: number
}

export interface ChunkItem {
  id: string
  document_id: string
  chunk_index: number
  content: string
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
  }
  created_at: string
}

export interface ChunkListResponse {
  items: ChunkItem[]
  total: number
  document_id: string
  status: string
  embedding_dimension: number
}

export async function uploadDocument(
  file: File,
  documentType: DocumentType = 'GENERAL'
): Promise<DocumentItem> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)

  return fetchApi<DocumentItem>('/api/documents/upload', {
    method: 'POST',
    body: formData,
  })
}

export async function getDocuments(
  documentType?: string,
  limit: number = 50,
  offset: number = 0
): Promise<DocumentListResponse> {
  const params = new URLSearchParams()
  if (documentType && documentType !== 'ALL') {
    params.append('document_type', documentType)
  }
  params.append('limit', limit.toString())
  params.append('offset', offset.toString())

  const endpoint = `/api/documents?${params.toString()}`
  return fetchApi<DocumentListResponse>(endpoint, {
    method: 'GET',
  })
}

export async function getDocument(id: string): Promise<DocumentItem> {
  return fetchApi<DocumentItem>(`/api/documents/${id}`, {
    method: 'GET',
  })
}

export async function processDocument(id: string): Promise<DocumentContentResponse> {
  return fetchApi<DocumentContentResponse>(`/api/documents/${id}/process`, {
    method: 'POST',
  })
}

export async function getDocumentContent(id: string): Promise<DocumentContentResponse> {
  return fetchApi<DocumentContentResponse>(`/api/documents/${id}/content`, {
    method: 'GET',
  })
}

export async function embedDocument(id: string): Promise<ChunkListResponse> {
  return fetchApi<ChunkListResponse>(`/api/documents/${id}/embed`, {
    method: 'POST',
  })
}

export async function getDocumentChunks(id: string): Promise<ChunkListResponse> {
  return fetchApi<ChunkListResponse>(`/api/documents/${id}/chunks`, {
    method: 'GET',
  })
}

export async function deleteDocument(id: string): Promise<void> {
  await fetchApi<void>(`/api/documents/${id}`, {
    method: 'DELETE',
  })
}

export async function downloadDocument(id: string, originalFilename: string): Promise<void> {
  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const cleanBase = BASE_URL.endsWith('/') ? BASE_URL.slice(0, -1) : BASE_URL
  const url = `${cleanBase}/api/documents/${id}/download`

  const token = authStorage.getToken()
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {}

  const response = await fetch(url, { headers })
  if (!response.ok) {
    throw new Error(`Failed to download file (${response.status})`)
  }

  const blob = await response.blob()
  const downloadUrl = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = downloadUrl
  a.download = originalFilename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(downloadUrl)
}
