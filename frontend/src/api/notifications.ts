import { fetchApi } from './client'

export type NotificationType =
  | 'DOCUMENT_UPLOADED'
  | 'DOCUMENT_PROCESSED'
  | 'DOCUMENT_FAILED'
  | 'REMINDER_DUE'
  | 'REMINDER_OVERDUE'
  | 'QUERY_ALERT'
  | string

export type NotificationChannel = 'IN_APP' | 'EMAIL' | 'WEBHOOK' | string
export type NotificationStatus = 'PENDING' | 'SENT' | 'FAILED' | 'READ' | string
export type NotificationSeverity = 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' | string

export interface NotificationItem {
  id: string
  user_id: string
  notification_type: NotificationType
  title: string
  message: string
  channel: NotificationChannel
  status: NotificationStatus
  severity: NotificationSeverity
  related_document_id?: string | null
  related_reminder_id?: string | null
  related_conversation_id?: string | null
  payload_metadata?: Record<string, any> | null
  retry_count: number
  created_at: string
  sent_at?: string | null
  read_at?: string | null
  failed_at?: string | null
  failure_reason?: string | null
}

export interface NotificationListResponse {
  items: NotificationItem[]
  total: number
  unread_count: number
}

export interface UnreadCountResponse {
  unread_count: number
}

export interface NotificationPreference {
  in_app_enabled: boolean
  email_enabled: boolean
  webhook_enabled: boolean
  document_event_notifications: boolean
  reminder_notifications: boolean
  query_alert_notifications: boolean
  email_address?: string | null
  webhook_url?: string | null
  has_webhook_secret: boolean
  updated_at: string
}

export interface NotificationPreferenceUpdatePayload {
  in_app_enabled?: boolean
  email_enabled?: boolean
  webhook_enabled?: boolean
  document_event_notifications?: boolean
  reminder_notifications?: boolean
  query_alert_notifications?: boolean
  email_address?: string | null
  webhook_url?: string | null
  webhook_secret?: string | null
}

export interface NotificationProcessResult {
  processed_count: number
  delivered_count: number
  failed_count: number
  evaluated_at: string
}

export async function getNotifications(params?: {
  unread?: boolean
  notification_type?: string
  severity?: string
  channel?: string
  skip?: number
  limit?: number
}): Promise<NotificationListResponse> {
  const query = new URLSearchParams()
  if (params?.unread !== undefined) {
    query.set('unread', String(params.unread))
  }
  if (params?.notification_type && params.notification_type !== 'ALL') {
    query.set('notification_type', params.notification_type)
  }
  if (params?.severity && params.severity !== 'ALL') {
    query.set('severity', params.severity)
  }
  if (params?.channel && params.channel !== 'ALL') {
    query.set('channel', params.channel)
  }
  if (params?.skip !== undefined) {
    query.set('skip', String(params.skip))
  }
  if (params?.limit !== undefined) {
    query.set('limit', String(params.limit))
  }

  const qs = query.toString()
  const endpoint = qs ? `/api/notifications?${qs}` : '/api/notifications'
  return fetchApi<NotificationListResponse>(endpoint, { method: 'GET' })
}

export async function getUnreadCount(): Promise<UnreadCountResponse> {
  return fetchApi<UnreadCountResponse>('/api/notifications/unread-count', { method: 'GET' })
}

export async function markNotificationAsRead(id: string): Promise<NotificationItem> {
  return fetchApi<NotificationItem>(`/api/notifications/${id}/read`, {
    method: 'PATCH',
  })
}

export async function markAllNotificationsAsRead(): Promise<{ count: number }> {
  return fetchApi<{ count: number }>('/api/notifications/mark-all-read', {
    method: 'POST',
  })
}

export async function deleteNotification(id: string): Promise<void> {
  return fetchApi<void>(`/api/notifications/${id}`, {
    method: 'DELETE',
  })
}

export async function processPendingNotifications(): Promise<NotificationProcessResult> {
  return fetchApi<NotificationProcessResult>('/api/notifications/process-pending', {
    method: 'POST',
  })
}

export async function getNotificationPreferences(): Promise<NotificationPreference> {
  return fetchApi<NotificationPreference>('/api/notification-preferences', { method: 'GET' })
}

export async function updateNotificationPreferences(
  payload: NotificationPreferenceUpdatePayload
): Promise<NotificationPreference> {
  return fetchApi<NotificationPreference>('/api/notification-preferences', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}
