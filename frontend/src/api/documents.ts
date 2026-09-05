import { fetchApi } from './client'
import { authStorage } from './authStorage'

export type DocumentType = 'INVOICE' | 'BALANCE_SHEET' | 'P_AND_L' | 'CRICKET_BROCHURE' | 'GENERAL'

export interface DocumentItem {
  id: string
  user_id: string
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  status: string
  document_type: DocumentType | string
  created_at: string
  updated_at: string
}

export interface DocumentListResponse {
  items: DocumentItem[]
  total: number
  limit: number
  offset: number
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
