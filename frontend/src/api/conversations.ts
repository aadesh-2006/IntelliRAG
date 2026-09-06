import { fetchApi } from './client'
import { Citation } from './rag'

export interface GroundingMetadata {
  retrieved_sources: number
  highest_similarity: number
  average_similarity: number
  has_sufficient_context: boolean
  model_info?: {
    provider: string
    model: string
  }
}

export interface ConversationMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[] | null
  grounding_metadata?: GroundingMetadata | null
  is_sufficient_context: boolean
  created_at: string
}

export interface Conversation {
  id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
  message_count?: number
}

export interface ConversationDetail {
  id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
  messages: ConversationMessage[]
}

export interface SendMessagePayload {
  content: string
  document_ids?: string[] | null
  document_type?: string | null
  top_k?: number
  similarity_threshold?: number | null
}

export interface SendMessageResponse {
  user_message: ConversationMessage
  assistant_message: ConversationMessage
}

export async function createConversation(title?: string): Promise<Conversation> {
  return fetchApi<Conversation>('/api/conversations', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
}

export async function listConversations(): Promise<Conversation[]> {
  return fetchApi<Conversation[]>('/api/conversations', {
    method: 'GET',
  })
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  return fetchApi<ConversationDetail>(`/api/conversations/${conversationId}`, {
    method: 'GET',
  })
}

export async function deleteConversation(conversationId: string): Promise<void> {
  return fetchApi<void>(`/api/conversations/${conversationId}`, {
    method: 'DELETE',
  })
}

export async function sendMessage(
  conversationId: string,
  payload: SendMessagePayload
): Promise<SendMessageResponse> {
  return fetchApi<SendMessageResponse>(`/api/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
