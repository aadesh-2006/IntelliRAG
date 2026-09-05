import React, { useState, useEffect } from 'react'
import {
  Bot,
  Sparkles,
  SlidersHorizontal,
  FileText,
  Copy,
  Check,
  RotateCcw,
  BookOpen,
  HelpCircle,
  Cpu,
  Filter,
  AlertCircle,
} from 'lucide-react'
import { queryRAG, RAGQueryRequest, RAGQueryResponse } from '../api/rag'
import { getDocuments, DocumentItem } from '../api/documents'

interface RAGQueryCardProps {
  refreshTrigger?: number
}

export const RAGQueryCard: React.FC<RAGQueryCardProps> = ({ refreshTrigger = 0 }) => {
  const [query, setQuery] = useState<string>('')
  const [topK, setTopK] = useState<number>(5)
  const [similarityThreshold, setSimilarityThreshold] = useState<number | null>(0.25)
  const [selectedDocType, setSelectedDocType] = useState<string>('ALL')
  const [selectedDocId, setSelectedDocId] = useState<string>('ALL')
  const [documents, setDocuments] = useState<DocumentItem[]>([])

  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [ragResponse, setRagResponse] = useState<RAGQueryResponse | null>(null)
  const [copiedAnswer, setCopiedAnswer] = useState<boolean>(false)
  const [copiedCitationId, setCopiedCitationId] = useState<number | null>(null)
  const [showFilters, setShowFilters] = useState<boolean>(false)

  useEffect(() => {
    async function loadDocs() {
      try {
        const res = await getDocuments(undefined, 100, 0)
        setDocuments(res.items.filter((d) => d.status === 'READY' || d.status === 'PROCESSED'))
      } catch {
      }
    }
    loadDocs()
  }, [refreshTrigger])

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)

    const payload: RAGQueryRequest = {
      query: query.trim(),
      top_k: topK,
      similarity_threshold: similarityThreshold,
      document_type: selectedDocType !== 'ALL' ? selectedDocType : null,
      document_ids: selectedDocId !== 'ALL' ? [selectedDocId] : null,
    }

    try {
      const res = await queryRAG(payload)
      setRagResponse(res)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to generate RAG answer')
      }
      setRagResponse(null)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyAnswer = () => {
    if (!ragResponse?.answer) return
    navigator.clipboard.writeText(ragResponse.answer)
    setCopiedAnswer(true)
    setTimeout(() => setCopiedAnswer(false), 2000)
  }

  const handleCopyCitation = (citId: number, snippet: string) => {
    navigator.clipboard.writeText(snippet)
    setCopiedCitationId(citId)
    setTimeout(() => setCopiedCitationId(null), 2000)
  }

  const handleResetFilters = () => {
    setTopK(5)
    setSimilarityThreshold(0.25)
    setSelectedDocType('ALL')
    setSelectedDocId('ALL')
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-400" />
              Grounded RAG Answer Generation
            </h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Module 8 Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Ask questions in natural language and receive grounded answers backed by verified source citations.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-medium border transition-colors ${
            showFilters || selectedDocType !== 'ALL' || selectedDocId !== 'ALL' || similarityThreshold !== 0.25 || topK !== 5
              ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300'
              : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-800'
          }`}
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>RAG Settings</span>
          {(selectedDocType !== 'ALL' || selectedDocId !== 'ALL' || similarityThreshold !== 0.25 || topK !== 5) && (
            <span className="w-2 h-2 rounded-full bg-indigo-400" />
          )}
        </button>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your indexed documents (e.g. 'What was the Q3 net revenue and profit margin?')..."
            className="w-full bg-slate-950/80 border border-slate-700 rounded-xl pl-11 pr-28 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 transition-colors"
          />
          <HelpCircle className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold text-white transition-colors flex items-center space-x-1.5 shadow-sm"
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Answering...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Ask AI</span>
              </>
            )}
          </button>
        </div>

        {showFilters && (
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-4 animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Filter className="w-3.5 h-3.5 text-indigo-400" />
                RAG Pipeline Refinements
              </span>
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3" />
                Reset Defaults
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1.5">
                  Retrieved Chunks (top_k)
                </label>
                <select
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value={3}>Top 3 Chunks</option>
                  <option value={5}>Top 5 Chunks (Default)</option>
                  <option value={10}>Top 10 Chunks</option>
                  <option value={15}>Top 15 Chunks</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1.5">
                  Min Similarity Threshold
                </label>
                <select
                  value={similarityThreshold === null ? 'none' : similarityThreshold.toString()}
                  onChange={(e) =>
                    setSimilarityThreshold(e.target.value === 'none' ? null : Number(e.target.value))
                  }
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="none">No Minimum (All Matches)</option>
                  <option value="0.25">&gt;= 0.25 (Default Balanced)</option>
                  <option value="0.50">&gt;= 0.50 (Moderate)</option>
                  <option value="0.70">&gt;= 0.70 (High Precision)</option>
                  <option value="0.85">&gt;= 0.85 (Strict)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1.5">
                  Document Type Scope
                </label>
                <select
                  value={selectedDocType}
                  onChange={(e) => setSelectedDocType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="ALL">All Document Types</option>
                  <option value="GENERAL">General Document</option>
                  <option value="GENERAL_DOCUMENT">General Document (Alias)</option>
                  <option value="INVOICE">Invoice</option>
                  <option value="BALANCE_SHEET">Balance Sheet</option>
                  <option value="P_AND_L">Profit &amp; Loss</option>
                  <option value="CRICKET_BROCHURE">Cricket Brochure</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1.5">
                  Target Specific Document
                </label>
                <select
                  value={selectedDocId}
                  onChange={(e) => setSelectedDocId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 truncate"
                >
                  <option value="ALL">All Documents ({documents.length})</option>
                  {documents.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.original_filename}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
      </form>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {ragResponse && (
        <div className="space-y-6 pt-2 animate-fade-in">
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  Synthesized Answer
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                    ragResponse.has_sufficient_context
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}
                >
                  {ragResponse.has_sufficient_context ? 'Grounded Context' : 'Insufficient Evidence'}
                </span>
              </div>

              <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono">
                <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                  <Cpu className="w-3 h-3 text-indigo-400" />
                  {ragResponse.model_info.provider} / {ragResponse.model_info.model}
                </span>

                <button
                  type="button"
                  onClick={handleCopyAnswer}
                  className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                  title="Copy generated answer"
                >
                  {copiedAnswer ? (
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap font-sans">
              {ragResponse.answer}
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                Verified Citations &amp; Evidence ({ragResponse.citations.length})
              </h4>
            </div>

            {ragResponse.citations.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-950/40 border border-dashed border-slate-800 text-center text-xs text-slate-500">
                No citations referenced for this query.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {ragResponse.citations.map((cit) => {
                  const isCopied = copiedCitationId === cit.citation_id
                  return (
                    <div
                      key={cit.citation_id}
                      className="border border-slate-800/80 bg-slate-950/50 hover:bg-slate-900/40 rounded-xl p-3.5 space-y-2 transition-all"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 text-[10px] font-mono font-bold border border-indigo-500/30">
                            [Source {cit.citation_id}]
                          </span>
                          <span className="text-xs font-semibold text-slate-200 truncate max-w-[160px] flex items-center gap-1">
                            <FileText className="w-3 h-3 text-slate-400 shrink-0" />
                            {cit.document_filename}
                          </span>
                        </div>

                        <div className="flex items-center space-x-1.5">
                          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                            {(cit.similarity_score * 100).toFixed(1)}%
                          </span>
                          <button
                            type="button"
                            onClick={() => handleCopyCitation(cit.citation_id, cit.content_snippet)}
                            className="p-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                            title="Copy snippet"
                          >
                            {isCopied ? (
                              <Check className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400">
                        {cit.page_number && (
                          <span className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                            Page {cit.page_number}
                          </span>
                        )}
                        {cit.section && (
                          <span className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 truncate max-w-[140px]">
                            {cit.section}
                          </span>
                        )}
                        <span className="text-slate-500 font-mono">Chunk #{cit.chunk_index}</span>
                      </div>

                      <div className="text-[11px] text-slate-400 bg-slate-900/60 p-2 rounded-lg border border-slate-800/40 line-clamp-3 font-mono leading-normal">
                        {cit.content_snippet}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
