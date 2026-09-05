import React, { useState, useEffect } from 'react'
import {
  X,
  FileText,
  Table as TableIcon,
  Layers,
  Code2,
  Copy,
  Check,
  Cpu,
  Hash,
  AlertCircle,
  Loader2,
  ScanText
} from 'lucide-react'
import { getDocumentContent, DocumentContentResponse } from '../api/documents'

interface DocumentInspectionModalProps {
  documentId: string
  onClose: () => void
}

type TabType = 'layout' | 'tables' | 'raw' | 'json'

export const DocumentInspectionModal: React.FC<DocumentInspectionModalProps> = ({
  documentId,
  onClose,
}) => {
  const [content, setContent] = useState<DocumentContentResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('layout')
  const [copied, setCopied] = useState<boolean>(false)

  useEffect(() => {
    let isMounted = true
    const fetchContent = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getDocumentContent(documentId)
        if (isMounted) {
          setContent(data)
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error) {
            setError(err.message)
          } else {
            setError('Failed to load extracted document content')
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchContent()
    return () => {
      isMounted = false
    }
  }, [documentId])

  const handleCopyText = (textToCopy: string) => {
    navigator.clipboard.writeText(textToCopy)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const meta = content?.extracted_metadata
  const pages = meta?.pages || []
  const allTables = pages.flatMap((p) => p.tables || [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl h-[88vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/50 shrink-0">
          <div className="flex items-center space-x-3 truncate">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
              <ScanText className="w-5 h-5" />
            </div>
            <div className="truncate">
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white truncate">
                  {content?.original_filename || 'Document Content'}
                </h3>
                {content?.status && (
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                      content.status === 'PROCESSED'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : content.status === 'FAILED'
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}
                  >
                    {content.status}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                ID: {documentId}
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

        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading extracted layout & data...</p>
          </div>
        ) : error ? (
          <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-950/50 border border-rose-800 flex items-center justify-center text-rose-400">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">Extraction Inspection Unavailable</p>
              <p className="text-xs text-slate-400 max-w-md mt-1">{error}</p>
            </div>
          </div>
        ) : content?.status === 'FAILED' ? (
          <div className="flex-1 p-8 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-950/50 border border-rose-800 flex items-center justify-center text-rose-400">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">Document Processing Failed</p>
              <p className="text-xs text-rose-400 max-w-md mt-1 bg-rose-950/30 p-3 rounded-lg border border-rose-900/40 font-mono">
                {content.processing_error || 'Unknown error occurred during extraction'}
              </p>
            </div>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-950/30 border-b border-slate-800 shrink-0 text-xs">
              <div className="flex items-center space-x-2.5 p-2 rounded-lg bg-slate-800/40">
                <Cpu className="w-4 h-4 text-indigo-400 shrink-0" />
                <div className="truncate">
                  <span className="text-slate-500 block text-[10px]">PROCESSOR</span>
                  <span className="font-semibold text-slate-200 truncate block">
                    {meta?.processor || 'Standard'}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2.5 p-2 rounded-lg bg-slate-800/40">
                <Layers className="w-4 h-4 text-cyan-400 shrink-0" />
                <div>
                  <span className="text-slate-500 block text-[10px]">PAGES</span>
                  <span className="font-semibold text-slate-200">
                    {meta?.page_count || 1}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2.5 p-2 rounded-lg bg-slate-800/40">
                <Hash className="w-4 h-4 text-emerald-400 shrink-0" />
                <div>
                  <span className="text-slate-500 block text-[10px]">TEXT BLOCKS</span>
                  <span className="font-semibold text-slate-200">
                    {meta?.total_text_blocks || 0}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2.5 p-2 rounded-lg bg-slate-800/40">
                <TableIcon className="w-4 h-4 text-purple-400 shrink-0" />
                <div>
                  <span className="text-slate-500 block text-[10px]">TABLES</span>
                  <span className="font-semibold text-slate-200">
                    {meta?.total_tables || 0}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between px-4 border-b border-slate-800 bg-slate-900 shrink-0">
              <div className="flex space-x-1 py-2 overflow-x-auto">
                <button
                  onClick={() => setActiveTab('layout')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'layout'
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Structured Layout ({pages.length} Pages)</span>
                </button>

                <button
                  onClick={() => setActiveTab('tables')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'tables'
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <TableIcon className="w-3.5 h-3.5" />
                  <span>Extracted Tables ({allTables.length})</span>
                </button>

                <button
                  onClick={() => setActiveTab('raw')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'raw'
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Normalized Text</span>
                </button>

                <button
                  onClick={() => setActiveTab('json')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'json'
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>AST Metadata JSON</span>
                </button>
              </div>

              {activeTab === 'raw' && (
                <button
                  onClick={() => handleCopyText(content?.extracted_text || '')}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors shrink-0"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Text</span>
                    </>
                  )}
                </button>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              {activeTab === 'layout' && (
                <div className="space-y-6">
                  {pages.length === 0 ? (
                    <div className="text-center py-12 text-slate-500 text-xs">
                      No layout pages parsed.
                    </div>
                  ) : (
                    pages.map((page) => (
                      <div
                        key={page.page_number}
                        className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-4"
                      >
                        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-bold text-white uppercase tracking-wider">
                              Page {page.page_number}
                            </span>
                            {page.has_ocr && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                                OCR Processed
                              </span>
                            )}
                          </div>
                          {page.width && page.height && (
                            <span className="text-[10px] text-slate-500 font-mono">
                              {Math.round(page.width)} × {Math.round(page.height)} pt
                            </span>
                          )}
                        </div>

                        <div className="space-y-3">
                          {page.text_blocks.map((block) => (
                            <div
                              key={block.block_id}
                              className={`p-3 rounded-lg text-xs leading-relaxed ${
                                block.block_type === 'heading'
                                  ? 'bg-indigo-950/30 border border-indigo-800/40 text-indigo-200 font-semibold'
                                  : 'bg-slate-900/50 border border-slate-800/50 text-slate-300'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-[9px] uppercase font-mono tracking-wider text-slate-500">
                                  {block.block_type}
                                </span>
                                {block.confidence !== undefined && (
                                  <span className="text-[9px] font-mono text-slate-400">
                                    Conf: {block.confidence}%
                                  </span>
                                )}
                              </div>
                              <p className="whitespace-pre-wrap">{block.text}</p>
                            </div>
                          ))}

                          {page.tables.map((table) => (
                            <div
                              key={table.table_index}
                              className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-900/80 p-3"
                            >
                              <div className="text-[10px] uppercase font-mono text-purple-400 mb-2 font-semibold">
                                Table {table.table_index} ({table.rows.length} rows)
                              </div>
                              <table className="w-full text-left text-xs">
                                <thead>
                                  <tr className="border-b border-slate-800 text-slate-400">
                                    {table.headers.map((h, i) => (
                                      <th key={i} className="pb-2 px-2.5 font-semibold text-slate-300">
                                        {h}
                                      </th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/50">
                                  {table.rows.slice(table.headers.length > 0 ? 1 : 0).map((r, ri) => (
                                    <tr key={ri} className="hover:bg-slate-800/30">
                                      {r.cells.map((c, ci) => (
                                        <td key={ci} className="py-2 px-2.5 text-slate-300">
                                          {c.content}
                                        </td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'tables' && (
                <div className="space-y-6">
                  {allTables.length === 0 ? (
                    <div className="text-center py-12 text-slate-500 text-xs">
                      No tables detected or extracted from this document.
                    </div>
                  ) : (
                    allTables.map((table, tIdx) => (
                      <div
                        key={tIdx}
                        className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3"
                      >
                        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                          <div className="flex items-center space-x-2">
                            <TableIcon className="w-4 h-4 text-purple-400" />
                            <span className="text-xs font-bold text-white">
                              Table #{tIdx + 1} (Page {table.page_number})
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {table.rows.length} rows × {table.headers.length || (table.rows[0]?.cells.length ?? 0)} cols
                          </span>
                        </div>

                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs">
                            {table.headers.length > 0 && (
                              <thead>
                                <tr className="border-b border-slate-800 text-slate-300 bg-slate-900/60">
                                  {table.headers.map((h, i) => (
                                    <th key={i} className="py-2.5 px-3 font-semibold">
                                      {h}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                            )}
                            <tbody className="divide-y divide-slate-800/50">
                              {table.rows.map((r, ri) => (
                                <tr key={ri} className="hover:bg-slate-800/40 transition-colors">
                                  {r.cells.map((c, ci) => (
                                    <td key={ci} className="py-2.5 px-3 text-slate-300">
                                      {c.content}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'raw' && (
                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5">
                  <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
                    {content?.extracted_text || 'No raw text available.'}
                  </pre>
                </div>
              )}

              {activeTab === 'json' && (
                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5">
                  <pre className="text-xs font-mono text-emerald-400 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                    {JSON.stringify(meta || content, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
