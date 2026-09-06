import React, { useState, useEffect } from 'react'
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Layers,
  HardDrive,
  Clock,
  ArrowRight,
  Eye,
  Download,
  Activity,
  BarChart3,
  Bot,
  Search,
  Upload,
  RefreshCw,
} from 'lucide-react'
import { getDashboardStats, DashboardStats } from '../api/dashboard'
import { DocumentItem, downloadDocument } from '../api/documents'
import { DocumentInspectionModal } from './DocumentInspectionModal'
import { DocumentChunksModal } from './DocumentChunksModal'

interface DashboardOverviewProps {
  onNavigateTab: (tab: 'dashboard' | 'documents' | 'chat' | 'rag' | 'search' | 'roadmap') => void
  refreshTrigger?: number
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  onNavigateTab,
  refreshTrigger = 0,
}) => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [inspectDocId, setInspectDocId] = useState<string | null>(null)
  const [chunksDoc, setChunksDoc] = useState<{ id: string; filename: string } | null>(null)

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getDashboardStats()
      setStats(data)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to fetch dashboard metrics')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [refreshTrigger])

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'READY':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Ready
          </span>
        )
      case 'PROCESSED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            Processed
          </span>
        )
      case 'PROCESSING':
      case 'EMBEDDING':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            {status}
          </span>
        )
      case 'FAILED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
            Failed
          </span>
        )
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
            Uploaded
          </span>
        )
    }
  }

  if (loading && !stats) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-6 w-48 bg-slate-800 rounded animate-pulse" />
          <div className="h-8 w-24 bg-slate-800 rounded-lg animate-pulse" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-950/60 rounded-xl border border-slate-800 animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-slate-900/80 border border-rose-900/40 rounded-2xl p-6 text-center space-y-3">
        <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
        <p className="text-sm font-semibold text-white">Failed to Load Dashboard Statistics</p>
        <p className="text-xs text-rose-300 max-w-md mx-auto">{error}</p>
        <button
          onClick={fetchStats}
          className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        <div>
          <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            Workspace Operational Overview
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Real-time status metrics, ingestion statistics, and vector index health for your documents.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={fetchStats}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={() => onNavigateTab('documents')}
            className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white flex items-center space-x-1.5 shadow-sm transition-colors"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-medium uppercase tracking-wider">Total Vault</span>
            <FileText className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">{stats?.total_documents || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Uploaded files</div>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-emerald-900/30 rounded-xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-emerald-400 mb-2">
            <span className="text-[11px] font-medium uppercase tracking-wider">Vector Ready</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-300 font-mono">{stats?.ready_documents || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Searchable &amp; Embedded</div>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-cyan-900/30 rounded-xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cyan-400 mb-2">
            <span className="text-[11px] font-medium uppercase tracking-wider">Processing</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-cyan-300 font-mono">
              {(stats?.processing_documents || 0) + (stats?.embedding_documents || 0)}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">Pipeline in-flight</div>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-indigo-400 mb-2">
            <span className="text-[11px] font-medium uppercase tracking-wider">Vector Chunks</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-indigo-300 font-mono">{stats?.total_chunks || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">768-dim embeddings</div>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-medium uppercase tracking-wider">Storage</span>
            <HardDrive className="w-4 h-4 text-slate-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">
              {formatBytes(stats?.total_storage_bytes || 0)}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">Consumed space</div>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-rose-900/30 rounded-xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-rose-400 mb-2">
            <span className="text-[11px] font-medium uppercase tracking-wider">Failed</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-rose-300 font-mono">{stats?.failed_documents || 0}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Attention needed</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
              Document Classifications
            </h4>
            <span className="text-[11px] text-slate-500 font-mono">
              {Object.keys(stats?.documents_by_type || {}).length} types
            </span>
          </div>

          <div className="space-y-2.5">
            {Object.keys(stats?.documents_by_type || {}).length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-6">No classified documents yet</p>
            ) : (
              Object.entries(stats?.documents_by_type || {}).map(([type, count]) => {
                const total = stats?.total_documents || 1
                const pct = Math.round((count / total) * 100)
                return (
                  <div key={type} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-slate-300">{type}</span>
                      <span className="text-slate-400 font-mono">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-indigo-400" />
              Processing Lifecycle
            </h4>
            <span className="text-[11px] text-slate-500 font-mono">
              {stats?.total_documents || 0} total
            </span>
          </div>

          <div className="space-y-3">
            {['UPLOADED', 'PROCESSING', 'PROCESSED', 'EMBEDDING', 'READY', 'FAILED'].map((st) => {
              const count = stats?.documents_by_status[st] || 0
              return (
                <div
                  key={st}
                  className="flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-800/60 text-xs"
                >
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(st)}
                  </div>
                  <span className="font-mono font-bold text-slate-200">{count}</span>
                </div>
              )
            })}
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5 text-indigo-400" />
                Quick Workflows
              </h4>
            </div>

            <div className="space-y-3">
              <button
                type="button"
                onClick={() => onNavigateTab('chat')}
                className="w-full text-left p-3 rounded-xl bg-indigo-950/20 hover:bg-indigo-950/40 border border-indigo-900/40 hover:border-indigo-700/60 transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Bot className="w-3.5 h-3.5 text-indigo-400" />
                    Document Assistant Chat
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Multi-turn grounded conversation with citations
                  </p>
                </div>
                <ArrowRight className="w-4 h-4 text-indigo-400 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                type="button"
                onClick={() => onNavigateTab('search')}
                className="w-full text-left p-3 rounded-xl bg-slate-950/40 hover:bg-slate-950/80 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Search className="w-3.5 h-3.5 text-indigo-400" />
                    Semantic Vector Search
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Retrieve relevant chunk rankings by cosine score
                  </p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                type="button"
                onClick={() => onNavigateTab('documents')}
                className="w-full text-left p-3 rounded-xl bg-slate-950/40 hover:bg-slate-950/80 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-indigo-400" />
                    Document Vault &amp; Chunker
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Manage files, OCR analysis, and chunk vectors
                  </p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Recent Document Ingestions
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Latest documents in your authenticated workspace vault.
            </p>
          </div>

          <button
            type="button"
            onClick={() => onNavigateTab('documents')}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <span>View All Vault Documents</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {(!stats?.recent_documents || stats.recent_documents.length === 0) ? (
          <div className="p-8 rounded-xl bg-slate-950/40 border border-dashed border-slate-800 text-center space-y-2">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs font-semibold text-slate-300">No documents uploaded yet</p>
            <p className="text-[11px] text-slate-500">
              Upload documents to begin extraction, chunking, and semantic intelligence.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="py-2.5 px-3">Document</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Size</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Uploaded</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {stats.recent_documents.map((doc: DocumentItem) => (
                  <tr key={doc.id} className="hover:bg-slate-950/40 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-semibold text-slate-200 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                        <span className="truncate max-w-[200px]">{doc.original_filename}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono">
                        {doc.document_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400 text-[11px]">
                      {formatBytes(doc.file_size)}
                    </td>
                    <td className="py-3 px-3">
                      {getStatusBadge(doc.status)}
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px]">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        <button
                          type="button"
                          onClick={() => setInspectDocId(doc.id)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                          title="Inspect layout & text"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => setChunksDoc({ id: doc.id, filename: doc.original_filename })}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                          title="Inspect chunks & embeddings"
                        >
                          <Layers className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => downloadDocument(doc.id, doc.original_filename)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                          title="Download document"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {inspectDocId && (
        <DocumentInspectionModal
          documentId={inspectDocId}
          onClose={() => setInspectDocId(null)}
        />
      )}

      {chunksDoc && (
        <DocumentChunksModal
          documentId={chunksDoc.id}
          originalFilename={chunksDoc.filename}
          onClose={() => setChunksDoc(null)}
        />
      )}
    </div>
  )
}
