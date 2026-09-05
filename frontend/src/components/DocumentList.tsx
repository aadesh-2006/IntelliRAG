import React, { useState, useEffect, useCallback } from 'react'
import {
  FileText,
  Download,
  Trash2,
  RefreshCw,
  Filter,
  FolderOpen,
  Loader2,
  AlertCircle,
  Clock,
  HardDrive,
  Sparkles,
  ScanText,
  Database,
  Layers
} from 'lucide-react'
import {
  getDocuments,
  deleteDocument,
  downloadDocument,
  processDocument,
  embedDocument,
  DocumentItem
} from '../api/documents'
import { DocumentInspectionModal } from './DocumentInspectionModal'
import { DocumentChunksModal } from './DocumentChunksModal'

interface DocumentListProps {
  refreshTrigger: number
}

const TYPE_TABS = [
  { key: 'ALL', label: 'All Files' },
  { key: 'GENERAL', label: 'General' },
  { key: 'INVOICE', label: 'Invoices' },
  { key: 'BALANCE_SHEET', label: 'Balance Sheets' },
  { key: 'P_AND_L', label: 'P&L Statements' },
  { key: 'CRICKET_BROCHURE', label: 'Cricket' },
]

export const DocumentList: React.FC<DocumentListProps> = ({ refreshTrigger }) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [total, setTotal] = useState<number>(0)
  const [activeType, setActiveType] = useState<string>('ALL')
  const [loading, setLoading] = useState<boolean>(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [inspectDocId, setInspectDocId] = useState<string | null>(null)
  const [chunksDoc, setChunksDoc] = useState<{ id: string; name: string } | null>(null)

  const fetchDocs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getDocuments(activeType)
      setDocuments(response.items)
      setTotal(response.total)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to fetch documents')
      }
    } finally {
      setLoading(false)
    }
  }, [activeType])

  useEffect(() => {
    fetchDocs()
  }, [fetchDocs, refreshTrigger])

  const handleProcess = async (docId: string) => {
    setActionLoading(docId)
    try {
      await processDocument(docId)
      await fetchDocs()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to process document')
      }
      await fetchDocs()
    } finally {
      setActionLoading(null)
    }
  }

  const handleEmbed = async (docId: string) => {
    setActionLoading(docId)
    try {
      await embedDocument(docId)
      await fetchDocs()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to generate embeddings')
      }
      await fetchDocs()
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async (docId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return
    }
    setActionLoading(docId)
    try {
      await deleteDocument(docId)
      await fetchDocs()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to delete document')
      }
    } finally {
      setActionLoading(null)
    }
  }

  const handleDownload = async (docId: string, filename: string) => {
    setActionLoading(docId)
    try {
      await downloadDocument(docId, filename)
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to download document')
      }
    } finally {
      setActionLoading(null)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const formatDate = (dateStr: string): string => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return dateStr
    }
  }

  const formatTypeBadge = (type: string) => {
    switch (type) {
      case 'INVOICE':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      case 'BALANCE_SHEET':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
      case 'P_AND_L':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20'
      case 'CRICKET_BROCHURE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      default:
        return 'bg-slate-500/10 text-slate-300 border-slate-500/20'
    }
  }

  const renderStatusBadge = (status: string, errorMsg?: string) => {
    switch (status) {
      case 'READY':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 inline-flex items-center space-x-1">
            <span>READY · 768d</span>
          </span>
        )
      case 'EMBEDDING':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 inline-flex items-center space-x-1">
            <Loader2 className="w-2.5 h-2.5 animate-spin" />
            <span>EMBEDDING</span>
          </span>
        )
      case 'PROCESSED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 inline-flex items-center space-x-1">
            <span>PROCESSED</span>
          </span>
        )
      case 'PROCESSING':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 inline-flex items-center space-x-1">
            <Loader2 className="w-2.5 h-2.5 animate-spin" />
            <span>PROCESSING</span>
          </span>
        )
      case 'FAILED':
        return (
          <span
            title={errorMsg || 'Processing failed'}
            className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 inline-flex items-center space-x-1 cursor-help"
          >
            <span>FAILED</span>
          </span>
        )
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            UPLOADED
          </span>
        )
    }
  }

  return (
    <>
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 sm:p-8 backdrop-blur-sm shadow-xl shadow-slate-950/50 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <FolderOpen className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white tracking-tight">Your Documents</h3>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  {total}
                </span>
              </div>
              <p className="text-xs text-slate-400">Isolated document storage, AI extraction & pgvector indexing</p>
            </div>
          </div>

          <button
            onClick={fetchDocs}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-xs font-medium text-slate-300 border border-slate-700/60 hover:text-white transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-thin">
          <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          {TYPE_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveType(tab.key)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                activeType === tab.key
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                  : 'bg-slate-800/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="flex items-center space-x-2 p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading document vault...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl bg-slate-950/30">
            <HardDrive className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-300">No documents found</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              {activeType === 'ALL'
                ? 'Upload your first invoice, financial statement, or cricket brochure using the form above.'
                : `No documents categorized under "${activeType}".`}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="pb-3 pl-2">File</th>
                  <th className="pb-3 px-3">Classification</th>
                  <th className="pb-3 px-3">Size</th>
                  <th className="pb-3 px-3">Status</th>
                  <th className="pb-3 px-3">Uploaded</th>
                  <th className="pb-3 pr-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors group">
                    <td className="py-3.5 pl-2">
                      <div className="flex items-center space-x-2.5 max-w-xs sm:max-w-sm truncate">
                        <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                        <span className="font-medium text-slate-200 truncate" title={doc.original_filename}>
                          {doc.original_filename}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${formatTypeBadge(doc.document_type)}`}>
                        {doc.document_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-slate-400 font-mono whitespace-nowrap">
                      {formatFileSize(doc.file_size)}
                    </td>
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      {renderStatusBadge(doc.status, doc.processing_error)}
                    </td>
                    <td className="py-3.5 px-3 text-slate-400 whitespace-nowrap">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>{formatDate(doc.created_at)}</span>
                      </div>
                    </td>
                    <td className="py-3.5 pr-2 text-right whitespace-nowrap">
                      <div className="inline-flex items-center space-x-1.5">
                        {doc.status === 'UPLOADED' || doc.status === 'FAILED' ? (
                          <button
                            onClick={() => handleProcess(doc.id)}
                            disabled={actionLoading === doc.id}
                            title="Process Document AI"
                            className="p-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 transition-colors disabled:opacity-50"
                          >
                            {actionLoading === doc.id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : (
                              <Sparkles className="w-3.5 h-3.5" />
                            )}
                          </button>
                        ) : null}

                        {doc.status === 'PROCESSED' ? (
                          <>
                            <button
                              onClick={() => setInspectDocId(doc.id)}
                              title="Inspect extraction & layout"
                              className="p-1.5 rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 text-indigo-300 hover:text-white border border-indigo-800/40 transition-colors"
                            >
                              <ScanText className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleEmbed(doc.id)}
                              disabled={actionLoading === doc.id}
                              title="Generate Embeddings (pgvector)"
                              className="p-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600 text-cyan-300 hover:text-white border border-cyan-500/30 transition-colors disabled:opacity-50"
                            >
                              {actionLoading === doc.id ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              ) : (
                                <Database className="w-3.5 h-3.5" />
                              )}
                            </button>
                          </>
                        ) : null}

                        {doc.status === 'READY' ? (
                          <>
                            <button
                              onClick={() => setInspectDocId(doc.id)}
                              title="Inspect extraction & layout"
                              className="p-1.5 rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 text-indigo-300 hover:text-white border border-indigo-800/40 transition-colors"
                            >
                              <ScanText className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => setChunksDoc({ id: doc.id, name: doc.original_filename })}
                              title="Inspect Vector Chunks"
                              className="p-1.5 rounded-lg bg-cyan-950/40 hover:bg-cyan-900/60 text-cyan-300 hover:text-white border border-cyan-800/40 transition-colors"
                            >
                              <Layers className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleEmbed(doc.id)}
                              disabled={actionLoading === doc.id}
                              title="Re-generate Embeddings"
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                            >
                              <RefreshCw className={`w-3.5 h-3.5 ${actionLoading === doc.id ? 'animate-spin' : ''}`} />
                            </button>
                          </>
                        ) : null}

                        <button
                          onClick={() => handleDownload(doc.id, doc.original_filename)}
                          disabled={actionLoading === doc.id}
                          title="Download file"
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        >
                          {actionLoading === doc.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Download className="w-3.5 h-3.5" />
                          )}
                        </button>

                        <button
                          onClick={() => handleDelete(doc.id, doc.original_filename)}
                          disabled={actionLoading === doc.id}
                          title="Delete file"
                          className="p-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 text-rose-400 hover:text-rose-200 border border-rose-800/40 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
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
          originalFilename={chunksDoc.name}
          onClose={() => setChunksDoc(null)}
        />
      )}
    </>
  )
}
