import React, { useState, useEffect } from 'react'
import {
  Search,
  SlidersHorizontal,
  FileText,
  Copy,
  Check,
  RotateCcw,
  Sparkles,
  Table,
  Filter,
} from 'lucide-react'
import {
  searchRetrieval,
  SearchQueryRequest,
  SearchQueryResponse,
} from '../api/retrieval'
import { getDocuments, DocumentItem } from '../api/documents'

interface SemanticSearchCardProps {
  refreshTrigger?: number
}

export const SemanticSearchCard: React.FC<SemanticSearchCardProps> = ({ refreshTrigger = 0 }) => {
  const [query, setQuery] = useState<string>('')
  const [topK, setTopK] = useState<number>(5)
  const [similarityThreshold, setSimilarityThreshold] = useState<number | null>(null)
  const [selectedDocType, setSelectedDocType] = useState<string>('ALL')
  const [selectedDocId, setSelectedDocId] = useState<string>('ALL')
  const [documents, setDocuments] = useState<DocumentItem[]>([])

  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [searchResponse, setSearchResponse] = useState<SearchQueryResponse | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
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

    const payload: SearchQueryRequest = {
      query: query.trim(),
      top_k: topK,
      similarity_threshold: similarityThreshold,
      document_type: selectedDocType !== 'ALL' ? selectedDocType : null,
      document_ids: selectedDocId !== 'ALL' ? [selectedDocId] : null,
    }

    try {
      const res = await searchRetrieval(payload)
      setSearchResponse(res)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to perform semantic retrieval')
      }
      setSearchResponse(null)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = (chunkId: string, content: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(chunkId)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleResetFilters = () => {
    setTopK(5)
    setSimilarityThreshold(null)
    setSelectedDocType('ALL')
    setSelectedDocId('ALL')
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.75) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    if (score >= 0.5) return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
    return 'text-amber-400 bg-amber-500/10 border-amber-500/20'
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Search className="w-5 h-5 text-indigo-400" />
              Semantic Search & Retrieval
            </h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              pgvector Cosine Distance
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Query indexed vector embeddings across your multimodal processed documents.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-medium border transition-colors ${
            showFilters || selectedDocType !== 'ALL' || selectedDocId !== 'ALL' || similarityThreshold !== null || topK !== 5
              ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300'
              : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-800'
          }`}
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>Filters & Thresholds</span>
          {(selectedDocType !== 'ALL' || selectedDocId !== 'ALL' || similarityThreshold !== null || topK !== 5) && (
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
            placeholder="Search documents by concept, meaning, questions, or metrics (e.g. 'Operating profit margin in Q3')..."
            className="w-full bg-slate-950/80 border border-slate-700 rounded-xl pl-11 pr-28 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 transition-colors"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold text-white transition-colors flex items-center space-x-1.5 shadow-sm"
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Retrieve</span>
              </>
            )}
          </button>
        </div>

        {showFilters && (
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-4 animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Filter className="w-3.5 h-3.5 text-indigo-400" />
                Search Refinements
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
                  Top Results (top_k)
                </label>
                <select
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value={3}>Top 3 Chunks</option>
                  <option value={5}>Top 5 Chunks (Default)</option>
                  <option value={10}>Top 10 Chunks</option>
                  <option value={20}>Top 20 Chunks</option>
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
                  <option value="none">No Minimum (All matches)</option>
                  <option value="0.3">&gt;= 0.30 (Broad match)</option>
                  <option value="0.5">&gt;= 0.50 (Moderate)</option>
                  <option value="0.7">&gt;= 0.70 (High precision)</option>
                  <option value="0.85">&gt;= 0.85 (Strict)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1.5">
                  Document Type
                </label>
                <select
                  value={selectedDocType}
                  onChange={(e) => setSelectedDocType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="ALL">All Types</option>
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
                  Specific Document
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
        <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {searchResponse && (
        <div className="space-y-4 pt-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-xs">
              <span className="font-semibold text-white">Retrieved Chunks:</span>
              <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-mono font-medium">
                {searchResponse.total_results} results
              </span>
              <span className="text-slate-500">for</span>
              <span className="text-slate-300 italic truncate max-w-xs">
                &ldquo;{searchResponse.query}&rdquo;
              </span>
            </div>
          </div>

          {searchResponse.results.length === 0 ? (
            <div className="text-center py-10 border border-dashed border-slate-800 rounded-xl">
              <FileText className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-300">No matching chunks found</p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-sm mx-auto">
                Try lowering the similarity threshold or making sure documents have been processed and indexed into vector embeddings.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {searchResponse.results.map((chunk, index) => {
                const isCopied = copiedId === chunk.id
                const isTable = chunk.metadata?.is_table || false
                const pageNum = chunk.metadata?.page_number
                const sectionName = chunk.metadata?.section

                return (
                  <div
                    key={chunk.id}
                    className="group border border-slate-800 hover:border-indigo-500/40 bg-slate-950/40 hover:bg-slate-900/40 rounded-xl p-4 transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[11px] font-mono font-semibold">
                          #{index + 1}
                        </span>

                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-indigo-400" />
                          {chunk.document_filename}
                        </span>

                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700/60">
                          {chunk.document_type}
                        </span>

                        {pageNum && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800/80 text-slate-400">
                            Page {pageNum}
                          </span>
                        )}

                        {sectionName && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800/60 text-slate-400 truncate max-w-[150px]">
                            {sectionName}
                          </span>
                        )}

                        {isTable && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1">
                            <Table className="w-3 h-3" />
                            Table
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <div
                          className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold border ${getScoreColor(
                            chunk.similarity_score
                          )}`}
                          title={`Cosine Distance: ${chunk.distance}`}
                        >
                          Score: {(chunk.similarity_score * 100).toFixed(1)}%
                        </div>

                        <button
                          type="button"
                          onClick={() => handleCopy(chunk.id, chunk.content)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
                          title="Copy chunk content"
                        >
                          {isCopied ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </div>

                    <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-800/60 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                      {chunk.content}
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
                      <span>Chunk Index: {chunk.chunk_index}</span>
                      <span>Distance: {chunk.distance.toFixed(4)}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
