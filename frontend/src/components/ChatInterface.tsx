import React, { useState, useEffect, useRef } from 'react'
import {
  Bot,
  User,
  Send,
  Plus,
  Trash2,
  SlidersHorizontal,
  Copy,
  Check,
  ShieldCheck,
  AlertCircle,
  Clock,
  Sparkles,
  Layers,
  ChevronRight,
  MessageSquare,
} from 'lucide-react'
import {
  Conversation,
  ConversationDetail,
  ConversationMessage,
  listConversations,
  getConversation,
  createConversation,
  deleteConversation,
  sendMessage,
} from '../api/conversations'
import { getDocuments, DocumentItem } from '../api/documents'

interface ChatInterfaceProps {
  refreshTrigger?: number
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ refreshTrigger = 0 }) => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [activeConv, setActiveConv] = useState<ConversationDetail | null>(null)
  const [loadingConversations, setLoadingConversations] = useState<boolean>(true)
  const [loadingMessages, setLoadingMessages] = useState<boolean>(false)
  const [sending, setSending] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const [inputContent, setInputContent] = useState<string>('')
  const [topK, setTopK] = useState<number>(5)
  const [similarityThreshold, setSimilarityThreshold] = useState<number | null>(0.25)
  const [selectedDocId, setSelectedDocId] = useState<string>('ALL')
  const [selectedDocType, setSelectedDocType] = useState<string>('ALL')
  const [showFilters, setShowFilters] = useState<boolean>(false)
  const [documents, setDocuments] = useState<DocumentItem[]>([])

  const [copiedIndex, setCopiedIndex] = useState<string | null>(null)
  const [copiedCitationKey, setCopiedCitationKey] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    loadDocuments()
    fetchConversations()
  }, [refreshTrigger])

  useEffect(() => {
    if (activeConvId) {
      fetchConversationDetail(activeConvId)
    } else {
      setActiveConv(null)
    }
  }, [activeConvId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeConv?.messages, sending])

  const loadDocuments = async () => {
    try {
      const res = await getDocuments(undefined, 100, 0)
      setDocuments(res.items.filter((d) => d.status === 'READY' || d.status === 'PROCESSED'))
    } catch {
    }
  }

  const fetchConversations = async () => {
    setLoadingConversations(true)
    setError(null)
    try {
      const list = await listConversations()
      setConversations(list)
      if (list.length > 0 && !activeConvId) {
        setActiveConvId(list[0].id)
      } else if (list.length === 0) {
        setActiveConvId(null)
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to load conversation history')
      }
    } finally {
      setLoadingConversations(false)
    }
  }

  const fetchConversationDetail = async (id: string) => {
    setLoadingMessages(true)
    setError(null)
    try {
      const detail = await getConversation(id)
      setActiveConv(detail)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to load conversation messages')
      }
    } finally {
      setLoadingMessages(false)
    }
  }

  const handleNewChat = async () => {
    setError(null)
    try {
      const newConv = await createConversation('New Conversation')
      setConversations((prev) => [newConv, ...prev])
      setActiveConvId(newConv.id)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      }
    }
  }

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    setError(null)
    try {
      await deleteConversation(id)
      const remaining = conversations.filter((c) => c.id !== id)
      setConversations(remaining)
      if (activeConvId === id) {
        setActiveConvId(remaining.length > 0 ? remaining[0].id : null)
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      }
    }
  }

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!inputContent.trim() || sending) return

    let currentId = activeConvId
    if (!currentId) {
      try {
        const created = await createConversation('New Conversation')
        setConversations((prev) => [created, ...prev])
        currentId = created.id
        setActiveConvId(created.id)
      } catch (err: unknown) {
        if (err instanceof Error) setError(err.message)
        return
      }
    }

    const userText = inputContent.trim()
    setInputContent('')
    setSending(true)
    setError(null)

    const tempUserMsg: ConversationMessage = {
      id: 'temp-' + Date.now(),
      conversation_id: currentId,
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
      is_sufficient_context: true,
    }

    setActiveConv((prev) => {
      if (!prev) {
        return {
          id: currentId!,
          user_id: '',
          title: userText.slice(0, 40),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          messages: [tempUserMsg],
        }
      }
      return {
        ...prev,
        messages: [...prev.messages, tempUserMsg],
      }
    })

    try {
      const response = await sendMessage(currentId, {
        content: userText,
        top_k: topK,
        similarity_threshold: similarityThreshold,
        document_ids: selectedDocId !== 'ALL' ? [selectedDocId] : null,
        document_type: selectedDocType !== 'ALL' ? selectedDocType : null,
      })

      setActiveConv((prev) => {
        if (!prev) return null
        const filtered = prev.messages.filter((m) => m.id !== tempUserMsg.id)
        return {
          ...prev,
          messages: [...filtered, response.user_message, response.assistant_message],
        }
      })

      setConversations((prev) =>
        prev.map((c) => {
          if (c.id === currentId) {
            return {
              ...c,
              title: c.title === 'New Conversation' ? userText.slice(0, 40) : c.title,
              updated_at: new Date().toISOString(),
              message_count: (c.message_count || 0) + 2,
            }
          }
          return c
        })
      )
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to generate response')
      }
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(key)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const copyCitation = (text: string, key: string) => {
    navigator.clipboard.writeText(text)
    setCopiedCitationKey(key)
    setTimeout(() => setCopiedCitationKey(null), 2000)
  }

  const documentTypes = [
    'ALL',
    'GENERAL_DOCUMENT',
    'INVOICE',
    'BALANCE_SHEET',
    'POLICY',
    'CRICKET_SCORECARD',
    'TECHNICAL_REPORT',
  ]

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl flex flex-col md:flex-row h-[750px]">
      <div className="w-full md:w-80 border-b md:border-b-0 md:border-r border-slate-800 bg-slate-950/60 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">Conversations</span>
          </div>
          <button
            type="button"
            onClick={handleNewChat}
            className="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white flex items-center space-x-1 transition-colors shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-800/40 p-2 space-y-1">
          {loadingConversations ? (
            <div className="p-6 text-center space-y-2">
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs text-slate-400">Loading chats...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-xs space-y-2">
              <MessageSquare className="w-8 h-8 text-slate-700 mx-auto" />
              <p>No chat history yet.</p>
              <button
                type="button"
                onClick={handleNewChat}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline"
              >
                Start a conversation
              </button>
            </div>
          ) : (
            conversations.map((c) => {
              const isActive = c.id === activeConvId
              return (
                <div
                  key={c.id}
                  onClick={() => setActiveConvId(c.id)}
                  className={`group w-full text-left p-2.5 rounded-xl cursor-pointer transition-all flex items-center justify-between ${
                    isActive
                      ? 'bg-indigo-950/40 border border-indigo-800/50 text-white'
                      : 'hover:bg-slate-900/60 text-slate-300 border border-transparent'
                  }`}
                >
                  <div className="min-w-0 pr-2">
                    <p className="text-xs font-medium truncate">{c.title}</p>
                    <div className="flex items-center space-x-2 text-[10px] text-slate-500 mt-0.5">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(c.updated_at).toLocaleDateString()}</span>
                      {c.message_count !== undefined && c.message_count > 0 && (
                        <span>• {c.message_count} msgs</span>
                      )}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/40 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )
            })
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-slate-900/40 overflow-hidden">
        <div className="p-3.5 px-6 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between gap-4">
          <div className="flex items-center space-x-3 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <h3 className="text-sm font-bold text-white truncate">
                {activeConv?.title || 'Conversational Document Assistant'}
              </h3>
              <p className="text-[11px] text-slate-400">
                Grounded multi-turn RAG across your authenticated documents
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1.5 transition-colors ${
                showFilters || selectedDocId !== 'ALL' || selectedDocType !== 'ALL'
                  ? 'bg-indigo-950/60 border-indigo-700/60 text-indigo-300'
                  : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-750'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Filters</span>
              {(selectedDocId !== 'ALL' || selectedDocType !== 'ALL') && (
                <span className="w-2 h-2 rounded-full bg-indigo-400" />
              )}
            </button>
          </div>
        </div>

        {showFilters && (
          <div className="bg-slate-950/90 border-b border-slate-800 p-4 grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs animate-fade-in">
            <div>
              <label className="block text-slate-400 font-semibold mb-1">Specific Document</label>
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="ALL">All Vault Documents</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.original_filename}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Document Type</label>
              <select
                value={selectedDocType}
                onChange={(e) => setSelectedDocType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {documentTypes.map((dt) => (
                  <option key={dt} value={dt}>
                    {dt}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">
                Top Chunks (k): <span className="font-mono text-indigo-400">{topK}</span>
              </label>
              <input
                type="range"
                min="1"
                max="15"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full accent-indigo-500 mt-1 cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">
                Similarity Threshold:{' '}
                <span className="font-mono text-indigo-400">
                  {similarityThreshold !== null ? similarityThreshold.toFixed(2) : 'None'}
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="0.9"
                step="0.05"
                value={similarityThreshold ?? 0}
                onChange={(e) => setSimilarityThreshold(Number(e.target.value))}
                className="w-full accent-indigo-500 mt-1 cursor-pointer"
              />
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {error && (
            <div className="p-3 bg-rose-950/40 border border-rose-900/50 rounded-xl flex items-center space-x-2.5 text-xs text-rose-300 animate-shake">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {loadingMessages ? (
            <div className="h-full flex flex-col items-center justify-center space-y-3">
              <div className="w-7 h-7 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-400">Loading conversation messages...</p>
            </div>
          ) : !activeConv || activeConv.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-white">Ask your documents anything</h4>
                <p className="text-xs text-slate-400 mt-1">
                  IntelliRAG retrieves relevant passages from your uploaded documents, preserves conversational context, and delivers grounded answers with citations.
                </p>
              </div>

              <div className="w-full grid grid-cols-1 gap-2 pt-2 text-left">
                <button
                  type="button"
                  onClick={() => setInputContent('What are the key terms and deadlines mentioned in my documents?')}
                  className="p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between"
                >
                  <span>What are the key terms and deadlines mentioned?</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                </button>
                <button
                  type="button"
                  onClick={() => setInputContent('Extract and summarize financial figures and total values.')}
                  className="p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors flex items-center justify-between"
                >
                  <span>Extract and summarize financial figures and total values.</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                </button>
              </div>
            </div>
          ) : (
            activeConv.messages.map((msg, index) => {
              const isUser = msg.role === 'user'
              const copyKey = `msg-${index}`

              return (
                <div
                  key={msg.id}
                  className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-2xl rounded-2xl p-4 text-xs space-y-3 shadow-sm ${
                      isUser
                        ? 'bg-indigo-600 text-white rounded-tr-sm ml-12'
                        : 'bg-slate-950/70 border border-slate-800 text-slate-200 rounded-tl-sm'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-4 border-b pb-2 text-[10px] font-semibold uppercase tracking-wider opacity-70 border-white/10">
                      <div className="flex items-center space-x-1.5">
                        <span>{isUser ? 'You' : 'IntelliRAG Assistant'}</span>
                        {!isUser && msg.grounding_metadata?.route && (
                          <span
                            className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold tracking-normal ${
                              msg.grounding_metadata.route === 'SQL'
                                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                : msg.grounding_metadata.route === 'HYBRID'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            }`}
                          >
                            {msg.grounding_metadata.route}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        {!isUser && (
                          <button
                            type="button"
                            onClick={() => copyToClipboard(msg.content, copyKey)}
                            className="hover:text-white transition-colors"
                            title="Copy answer"
                          >
                            {copiedIndex === copyKey ? (
                              <Check className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="leading-relaxed whitespace-pre-wrap font-sans text-[13px]">
                      {msg.content}
                    </div>

                    {!isUser && !msg.is_sufficient_context && (
                      <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-900/50 flex items-center space-x-2 text-amber-300 text-xs">
                        <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                        <span>Insufficient document evidence for full groundedness.</span>
                      </div>
                    )}

                    {!isUser && msg.grounding_metadata && (
                      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 space-y-2">
                        <div className="flex items-center justify-between text-[11px] font-semibold text-slate-300">
                          <span className="flex items-center gap-1.5">
                            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                            Retrieval Grounding Signals
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                              msg.grounding_metadata.has_sufficient_context
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            }`}
                          >
                            {msg.grounding_metadata.has_sufficient_context ? 'Grounded Evidence' : 'Low Evidence'}
                          </span>
                        </div>

                        <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              msg.grounding_metadata.highest_similarity >= 0.6
                                ? 'bg-emerald-500'
                                : msg.grounding_metadata.highest_similarity >= 0.35
                                ? 'bg-indigo-500'
                                : 'bg-amber-500'
                            }`}
                            style={{
                              width: `${Math.min(
                                100,
                                Math.max(10, Math.round(msg.grounding_metadata.highest_similarity * 100))
                              )}%`,
                            }}
                          />
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-400 pt-1 font-mono">
                          <div>
                            <span>Sources: </span>
                            <span className="text-slate-200 font-bold">
                              {msg.grounding_metadata.retrieved_sources}
                            </span>
                          </div>
                          <div>
                            <span>Peak match: </span>
                            <span className="text-slate-200 font-bold">
                              {Math.round(msg.grounding_metadata.highest_similarity * 100)}%
                            </span>
                          </div>
                          <div>
                            <span>Avg match: </span>
                            <span className="text-slate-200 font-bold">
                              {Math.round(msg.grounding_metadata.average_similarity * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div className="space-y-2 pt-1">
                        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Layers className="w-3.5 h-3.5 text-indigo-400" />
                          Source Citations ({msg.citations.length})
                        </div>

                        <div className="grid grid-cols-1 gap-2">
                          {msg.citations.map((c) => {
                            const citKey = `cit-${c.citation_id}-${c.chunk_id}`
                            return (
                              <div
                                key={citKey}
                                className="bg-slate-900/80 border border-slate-800 rounded-xl p-2.5 space-y-1.5 text-slate-300"
                              >
                                <div className="flex items-center justify-between text-[11px]">
                                  <div className="flex items-center space-x-1.5 font-semibold text-slate-200">
                                    <span className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono text-[10px]">
                                      [{c.citation_id}]
                                    </span>
                                    <span className="truncate max-w-[180px]">{c.document_filename}</span>
                                  </div>
                                  <div className="flex items-center space-x-2 text-[10px] text-slate-400">
                                    {c.page_number && <span>Page {c.page_number}</span>}
                                    {c.section && <span>• {c.section}</span>}
                                    <span className="px-1.5 py-0.5 rounded bg-slate-800 font-mono text-indigo-300">
                                      {Math.round(c.similarity_score * 100)}% match
                                    </span>
                                    <button
                                      type="button"
                                      onClick={() => copyCitation(c.content_snippet, citKey)}
                                      className="hover:text-white"
                                      title="Copy snippet"
                                    >
                                      {copiedCitationKey === citKey ? (
                                        <Check className="w-3 h-3 text-emerald-400" />
                                      ) : (
                                        <Copy className="w-3 h-3" />
                                      )}
                                    </button>
                                  </div>
                                </div>
                                <p className="text-[11px] text-slate-400 line-clamp-2 italic bg-slate-950/40 p-1.5 rounded border border-slate-800/60 font-mono">
                                  "{c.content_snippet}"
                                </p>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              )
            })
          )}

          {sending && (
            <div className="flex gap-3.5 justify-start animate-pulse">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-950/70 border border-slate-800 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-300 space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                  <span className="font-semibold text-slate-200">Retrieving document chunks &amp; generating grounded answer...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-800 bg-slate-950/60 space-y-2">
          <div className="relative flex items-end gap-2 bg-slate-900 border border-slate-700 rounded-2xl p-2 focus-within:border-indigo-500 transition-colors">
            <textarea
              rows={2}
              value={inputContent}
              onChange={(e) => setInputContent(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents... (Enter to send, Shift+Enter for new line)"
              disabled={sending}
              className="flex-1 bg-transparent border-0 resize-none text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none px-2 py-1 scrollbar-none"
            />
            <button
              type="submit"
              disabled={!inputContent.trim() || sending}
              className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white shadow-sm transition-all shrink-0"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
            <span>Conversational RAG groundings with direct citation sources.</span>
            <span>Press Enter ↵ to send</span>
          </div>
        </form>
      </div>
    </div>
  )
}
