import React, { useState, useEffect } from 'react'
import {
  X,
  Database,
  Search,
  Copy,
  Check,
  Layers,
  Table as TableIcon,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { getDocumentChunks, ChunkItem, ChunkListResponse } from '../api/documents'

interface DocumentChunksModalProps {
  documentId: string
  originalFilename: string
  onClose: () => void
}

export const DocumentChunksModal: React.FC<DocumentChunksModalProps> = ({
  documentId,
  originalFilename,
  onClose,
}) => {
  const [data, setData] = useState<ChunkListResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [copiedId, setCopiedId] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    const fetchChunks = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await getDocumentChunks(documentId)
        if (isMounted) {
          setData(response)
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error) {
            setError(err.message)
          } else {
            setError('Failed to load document vector chunks')
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchChunks()
    return () => {
      isMounted = false
    }
  }, [documentId])

  const handleCopyChunk = (chunkId: string, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(chunkId)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const chunks = data?.items || []
  const filteredChunks = chunks.filter((c: ChunkItem) => {
    if (!searchTerm.trim()) return true
    const term = searchTerm.toLowerCase()
    const contentMatch = c.content.toLowerCase().includes(term)
    const sectionMatch = c.metadata?.section?.toLowerCase().includes(term)
    return contentMatch || sectionMatch
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl h-[88vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/50 shrink-0">
          <div className="flex items-center space-x-3 truncate">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0">
              <Database className="w-5 h-5" />
            </div>
            <div className="truncate">
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white truncate">
                  {originalFilename}
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {data?.status || 'READY'}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Vector Dimension: {data?.embedding_dimension || 768}d · Chunks: {data?.total || 0}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 bg-slate-950/30 border-b border-slate-800 shrink-0 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter chunks by content or section..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center space-x-4 text-xs text-slate-400">
            <span>
              Showing <strong className="text-white">{filteredChunks.length}</strong> of{' '}
              <strong className="text-white">{chunks.length}</strong> chunks
            </span>
          </div>
        </div>

        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading vector embeddings & chunk metadata...</p>
          </div>
        ) : error ? (
          <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-950/50 border border-rose-800 flex items-center justify-center text-rose-400">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">Chunks Unavailable</p>
              <p className="text-xs text-slate-400 max-w-md mt-1">{error}</p>
            </div>
          </div>
        ) : chunks.length === 0 ? (
          <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
            <Layers className="w-12 h-12 text-slate-600" />
            <div>
              <p className="text-sm font-semibold text-white">No Chunks Generated Yet</p>
              <p className="text-xs text-slate-400 max-w-md mt-1">
                Click &quot;Generate Embeddings&quot; in the document actions list to create vector chunks.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {filteredChunks.map((chunk: ChunkItem) => (
              <div
                key={chunk.id}
                className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-3 hover:border-slate-700 transition-colors"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-800/60">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-slate-800 text-cyan-400 border border-slate-700">
                      Chunk #{chunk.chunk_index}
                    </span>

                    {chunk.metadata?.page_number && (
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-800/60 text-slate-300 border border-slate-700/50">
                        Page {chunk.metadata.page_number}
                      </span>
                    )}

                    {chunk.metadata?.section && (
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-950/40 text-indigo-300 border border-indigo-800/40">
                        {chunk.metadata.section}
                      </span>
                    )}

                    {chunk.metadata?.is_table && (
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-purple-950/40 text-purple-300 border border-purple-800/40 inline-flex items-center space-x-1">
                        <TableIcon className="w-2.5 h-2.5" />
                        <span>Table Derived</span>
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] text-slate-500 font-mono">
                      {chunk.metadata?.character_length || chunk.content.length} chars ·{' '}
                      {chunk.metadata?.token_count || chunk.content.split(/\s+/).length} tokens
                    </span>

                    <button
                      onClick={() => handleCopyChunk(chunk.id, chunk.content)}
                      title="Copy chunk text"
                      className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                    >
                      {copiedId === chunk.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                </div>

                <pre className="text-xs font-mono text-slate-200 whitespace-pre-wrap leading-relaxed bg-slate-900/50 p-3 rounded-lg border border-slate-800/40">
                  {chunk.content}
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
