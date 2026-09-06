import { fetchApi } from './client'

export type ReminderType = 'EXPIRY' | 'WARRANTY' | 'RENEWAL' | 'PAYMENT' | 'DEADLINE' | 'CUSTOM'
export type ReminderStatus = 'PENDING' | 'DUE' | 'COMPLETED' | 'CANCELLED'

export interface ActionableDateCandidate {
  date: string
  type: string
  title: string
  source_text: string
  page?: number | null
  section?: string | null
  confidence: number
}

export interface ActionableDatesListResponse {
  document_id: string
  document_filename: string
  candidates_count: number
  candidates: ActionableDateCandidate[]
}

export interface ReminderItem {
  id: string
  user_id: string
  document_id?: string | null
  document_filename?: string | null
  title: string
  description?: string | null
  reminder_type: string
  due_at: string
  remind_at: string
  status: string
  source_text?: string | null
  source_page?: number | null
  source_section?: string | null
  created_at: string
  updated_at: string
  completed_at?: string | null
}

export interface ReminderSummary {
  total_pending: number
  due_count: number
  overdue_count: number
  upcoming_count: number
  completed_count: number
  expiry_count: number
  warranty_count: number
  renewal_count: number
  next_reminder?: ReminderItem | null
}

export interface ReminderCreatePayload {
  document_id?: string | null
  title: string
  description?: string | null
  reminder_type?: string
  due_at: string
  lead_time_days?: number | null
  remind_at?: string | null
  source_text?: string | null
  source_page?: number | null
  source_section?: string | null
}

export interface ReminderUpdatePayload {
  title?: string
  description?: string | null
  reminder_type?: string
  due_at?: string
  remind_at?: string
  status?: string
}

export interface ProcessDueResult {
  processed_count: number
  transitioned_due_count: number
  evaluated_at: string
}

export async function getReminders(params?: {
  status?: string
  reminder_type?: string
  document_id?: string
  upcoming?: boolean
  overdue?: boolean
}): Promise<ReminderItem[]> {
  const query = new URLSearchParams()
  if (params?.status && params.status !== 'ALL') {
    query.set('status', params.status)
  }
  if (params?.reminder_type && params.reminder_type !== 'ALL') {
    query.set('reminder_type', params.reminder_type)
  }
  if (params?.document_id) {
    query.set('document_id', params.document_id)
  }
  if (params?.upcoming !== undefined) {
    query.set('upcoming', String(params.upcoming))
  }
  if (params?.overdue !== undefined) {
    query.set('overdue', String(params.overdue))
  }

  const qs = query.toString()
  const endpoint = qs ? `/api/reminders?${qs}` : '/api/reminders'
  return fetchApi<ReminderItem[]>(endpoint, { method: 'GET' })
}

export async function getRemindersSummary(): Promise<ReminderSummary> {
  return fetchApi<ReminderSummary>('/api/reminders/summary', { method: 'GET' })
}

export async function createReminder(payload: ReminderCreatePayload): Promise<ReminderItem> {
  return fetchApi<ReminderItem>('/api/reminders', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getReminder(id: string): Promise<ReminderItem> {
  return fetchApi<ReminderItem>(`/api/reminders/${id}`, { method: 'GET' })
}

export async function updateReminder(id: string, payload: ReminderUpdatePayload): Promise<ReminderItem> {
  return fetchApi<ReminderItem>(`/api/reminders/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function completeReminder(id: string): Promise<ReminderItem> {
  return fetchApi<ReminderItem>(`/api/reminders/${id}/complete`, {
    method: 'POST',
  })
}

export async function deleteReminder(id: string): Promise<void> {
  return fetchApi<void>(`/api/reminders/${id}`, {
    method: 'DELETE',
  })
}

export async function processDueReminders(): Promise<ProcessDueResult> {
  return fetchApi<ProcessDueResult>('/api/reminders/process-due', {
    method: 'POST',
  })
}

export async function scanDocumentActionableDates(documentId: string): Promise<ActionableDatesListResponse> {
  return fetchApi<ActionableDatesListResponse>(`/api/documents/${documentId}/actionable-dates`, {
    method: 'POST',
  })
}
