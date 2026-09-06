import React, { useState, useEffect, useCallback } from 'react'
import {
  Bell,
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Sparkles,
  Plus,
  Trash2,
  Check,
  RefreshCw,
  FileText,
  Filter,
  Loader2,
  AlertCircle,
  Zap
} from 'lucide-react'
import {
  getReminders,
  getRemindersSummary,
  createReminder,
  completeReminder,
  deleteReminder,
  processDueReminders,
  scanDocumentActionableDates,
  ReminderItem,
  ReminderSummary,
  ActionableDateCandidate,
  ActionableDatesListResponse
} from '../api/reminders'
import { getDocuments, DocumentItem } from '../api/documents'

interface RemindersOverviewProps {
  refreshTrigger?: number
}

const TYPE_FILTERS = [
  { key: 'ALL', label: 'All Types' },
  { key: 'EXPIRY', label: 'Expiries' },
  { key: 'WARRANTY', label: 'Warranties' },
  { key: 'RENEWAL', label: 'Renewals' },
  { key: 'PAYMENT', label: 'Payments' },
  { key: 'DEADLINE', label: 'Deadlines' },
  { key: 'CUSTOM', label: 'Custom' },
]

export const RemindersOverview: React.FC<RemindersOverviewProps> = ({ refreshTrigger = 0 }) => {
  const [reminders, setReminders] = useState<ReminderItem[]>([])
  const [summary, setSummary] = useState<ReminderSummary | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('ALL')
  const [typeFilter, setTypeFilter] = useState<string>('ALL')
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const [showCreateModal, setShowCreateModal] = useState<boolean>(false)
  const [showScanModal, setShowScanModal] = useState<boolean>(false)

  const [availableDocs, setAvailableDocs] = useState<DocumentItem[]>([])
  const [selectedScanDocId, setSelectedScanDocId] = useState<string>('')
  const [scanResult, setScanResult] = useState<ActionableDatesListResponse | null>(null)
  const [scanLoading, setScanLoading] = useState<boolean>(false)

  const [newTitle, setNewTitle] = useState<string>('')
  const [newDescription, setNewDescription] = useState<string>('')
  const [newType, setNewType] = useState<string>('EXPIRY')
  const [newDueDate, setNewDueDate] = useState<string>('')
  const [newLeadDays, setNewLeadDays] = useState<number>(3)
  const [newDocId, setNewDocId] = useState<string>('')
  const [newSourceText, setNewSourceText] = useState<string>('')
  const [newSourcePage, setNewSourcePage] = useState<number | undefined>(undefined)

  const fetchRemindersData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const isUpcoming = statusFilter === 'UPCOMING'
      const isOverdue = statusFilter === 'OVERDUE'
      const apiStatus = ['PENDING', 'DUE', 'COMPLETED'].includes(statusFilter) ? statusFilter : undefined

      const [listData, summaryData] = await Promise.all([
        getReminders({
          status: apiStatus,
          reminder_type: typeFilter,
          upcoming: isUpcoming ? true : undefined,
          overdue: isOverdue ? true : undefined,
        }),
        getRemindersSummary()
      ])
      setReminders(listData)
      setSummary(summaryData)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to load reminders')
      }
    } finally {
      setLoading(false)
    }
  }, [statusFilter, typeFilter])

  useEffect(() => {
    fetchRemindersData()
  }, [fetchRemindersData, refreshTrigger])

  const fetchProcessedDocs = async () => {
    try {
      const res = await getDocuments('ALL')
      const processed = res.items.filter((d) => d.status === 'PROCESSED' || d.status === 'READY')
      setAvailableDocs(processed)
      if (processed.length > 0 && !selectedScanDocId) {
        setSelectedScanDocId(processed[0].id)
      }
    } catch {
      setAvailableDocs([])
    }
  }

  const handleOpenScan = () => {
    setShowScanModal(true)
    setScanResult(null)
    fetchProcessedDocs()
  }

  const handleRunScan = async () => {
    if (!selectedScanDocId) return
    setScanLoading(true)
    try {
      const res = await scanDocumentActionableDates(selectedScanDocId)
      setScanResult(res)
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to scan document for actionable dates')
      }
    } finally {
      setScanLoading(false)
    }
  }

  const handleAddCandidate = async (candidate: ActionableDateCandidate) => {
    try {
      const dueIso = new Date(candidate.date).toISOString()
      await createReminder({
        document_id: scanResult?.document_id,
        title: candidate.title,
        reminder_type: candidate.type,
        due_at: dueIso,
        lead_time_days: 3,
        source_text: candidate.source_text,
        source_page: candidate.page,
        source_section: candidate.section
      })
      alert(`Reminder created for "${candidate.title}"`)
      fetchRemindersData()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to create reminder')
      }
    }
  }

  const handleCreateManualReminder = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim() || !newDueDate) {
      alert('Please provide a title and due date')
      return
    }

    try {
      const dueIso = new Date(newDueDate).toISOString()
      await createReminder({
        title: newTitle.trim(),
        description: newDescription.trim() || undefined,
        reminder_type: newType,
        due_at: dueIso,
        lead_time_days: newLeadDays,
        document_id: newDocId || undefined,
        source_text: newSourceText || undefined,
        source_page: newSourcePage
      })
      setShowCreateModal(false)
      setNewTitle('')
      setNewDescription('')
      setNewDueDate('')
      setNewDocId('')
      setNewSourceText('')
      setNewSourcePage(undefined)
      fetchRemindersData()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to create reminder')
      }
    }
  }

  const handleComplete = async (id: string) => {
    setActionLoading(id)
    try {
      await completeReminder(id)
      await fetchRemindersData()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to complete reminder')
      }
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async (id: string, title: string) => {
    if (!window.confirm(`Delete reminder "${title}"?`)) return
    setActionLoading(id)
    try {
      await deleteReminder(id)
      await fetchRemindersData()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to delete reminder')
      }
    } finally {
      setActionLoading(null)
    }
  }

  const handleProcessDue = async () => {
    setActionLoading('process-due')
    try {
      const res = await processDueReminders()
      alert(`Evaluated reminders. ${res.transitioned_due_count} transitioned to DUE status.`)
      await fetchRemindersData()
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message)
      } else {
        alert('Failed to evaluate due reminders')
      }
    } finally {
      setActionLoading(null)
    }
  }

  const formatDate = (dateStr: string): string => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    } catch {
      return dateStr
    }
  }

  const formatBadgeType = (type: string) => {
    switch (type) {
      case 'WARRANTY':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      case 'EXPIRY':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20'
      case 'RENEWAL':
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
      case 'PAYMENT':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      case 'DEADLINE':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
      default:
        return 'bg-slate-500/10 text-slate-300 border-slate-500/20'
    }
  }

  const formatStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      case 'DUE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      default:
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 sm:p-8 backdrop-blur-sm shadow-xl shadow-slate-950/50 space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white tracking-tight">Actionable Reminders & Expiries</h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Module 11
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Context-aware date extraction, warranty tracking, renewal alerts & lead time scheduling
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleOpenScan}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all shadow-sm"
            >
              <Sparkles className="w-4 h-4" />
              <span>Scan Document Dates</span>
            </button>

            <button
              onClick={() => {
                fetchProcessedDocs()
                setShowCreateModal(true)
              }}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-sm shadow-indigo-500/20"
            >
              <Plus className="w-4 h-4" />
              <span>New Reminder</span>
            </button>

            <button
              onClick={handleProcessDue}
              disabled={actionLoading === 'process-due'}
              title="Evaluate reminders against current time"
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium transition-colors"
            >
              <Zap className={`w-3.5 h-3.5 text-amber-400 ${actionLoading === 'process-due' ? 'animate-spin' : ''}`} />
              <span>Evaluate Due</span>
            </button>

            <button
              onClick={fetchRemindersData}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3.5">
          <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Pending Reminders</span>
              <Clock className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-white mt-2">
              {summary?.total_pending ?? 0}
            </div>
            <div className="text-[10px] text-slate-500 mt-1">Active scheduled items</div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-amber-400">
              <span className="text-xs font-medium">Due for Action</span>
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-amber-300 mt-2">
              {summary?.due_count ?? 0}
            </div>
            <div className="text-[10px] text-amber-400/70 mt-1">Lead time triggered</div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-rose-400">
              <span className="text-xs font-medium">Overdue Dates</span>
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-rose-300 mt-2">
              {summary?.overdue_count ?? 0}
            </div>
            <div className="text-[10px] text-rose-400/70 mt-1">Past due deadline</div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between text-cyan-400">
              <span className="text-xs font-medium">Warranties & Expiries</span>
              <Calendar className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-cyan-300 mt-2">
              {(summary?.warranty_count ?? 0) + (summary?.expiry_count ?? 0)}
            </div>
            <div className="text-[10px] text-slate-500 mt-1">
              {summary?.warranty_count ?? 0} warranties · {summary?.expiry_count ?? 0} expiries
            </div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between col-span-2 sm:col-span-4 lg:col-span-1">
            <div className="flex items-center justify-between text-emerald-400">
              <span className="text-xs font-medium">Completed</span>
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-emerald-300 mt-2">
              {summary?.completed_count ?? 0}
            </div>
            <div className="text-[10px] text-emerald-400/70 mt-1">Archived & resolved</div>
          </div>
        </div>

        {summary?.next_reminder && (
          <div className="p-4 rounded-xl bg-gradient-to-r from-amber-950/30 via-slate-900/40 to-slate-950 border border-amber-800/30 flex items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
                <Calendar className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider block">
                  Next Upcoming Reminder
                </span>
                <span className="text-xs font-bold text-white">
                  {summary.next_reminder.title}
                </span>
                <span className="text-[11px] text-slate-400 ml-2">
                  Due: <span className="font-mono text-slate-200">{formatDate(summary.next_reminder.due_at)}</span>
                </span>
              </div>
            </div>
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border shrink-0 ${formatBadgeType(summary.next_reminder.reminder_type)}`}>
              {summary.next_reminder.reminder_type}
            </span>
          </div>
        )}

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-800/80 pt-4">
          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1">
            {['ALL', 'UPCOMING', 'OVERDUE', 'DUE', 'COMPLETED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
                  statusFilter === st
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-800/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1">
            <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            {TYPE_FILTERS.map((tf) => (
              <button
                key={tf.key}
                onClick={() => setTypeFilter(tf.key)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors whitespace-nowrap ${
                  typeFilter === tf.key
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading reminders...</p>
          </div>
        ) : reminders.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-slate-800 rounded-xl bg-slate-950/30 space-y-3">
            <Bell className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">No reminders found</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Scan your processed documents to automatically extract actionable dates or click "New Reminder" to create one manually.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {reminders.map((rem) => (
              <div
                key={rem.id}
                className="bg-slate-950/60 border border-slate-800/90 rounded-xl p-4 hover:border-slate-700/80 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${formatBadgeType(rem.reminder_type)}`}>
                      {rem.reminder_type}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${formatStatusBadge(rem.status)}`}>
                      {rem.status}
                    </span>
                    <h4 className="text-sm font-bold text-white truncate">
                      {rem.title}
                    </h4>
                  </div>

                  {rem.description && (
                    <p className="text-xs text-slate-300">
                      {rem.description}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    <div className="flex items-center space-x-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      <span>Due: <span className="text-slate-200 font-mono font-medium">{formatDate(rem.due_at)}</span></span>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      <span>Remind: <span className="text-slate-300 font-mono">{formatDate(rem.remind_at)}</span></span>
                    </div>

                    {rem.document_filename && (
                      <div className="flex items-center space-x-1.5 text-indigo-300">
                        <FileText className="w-3.5 h-3.5" />
                        <span className="truncate max-w-[200px]">{rem.document_filename}</span>
                        {rem.source_page && (
                          <span className="text-[10px] text-slate-500 font-mono">p.{rem.source_page}</span>
                        )}
                      </div>
                    )}
                  </div>

                  {rem.source_text && (
                    <div className="text-[11px] text-slate-400 bg-slate-900/80 border border-slate-800/60 p-2 rounded-lg font-mono truncate">
                      "{rem.source_text}"
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 shrink-0 sm:self-center">
                  {rem.status !== 'COMPLETED' && (
                    <button
                      onClick={() => handleComplete(rem.id)}
                      disabled={actionLoading === rem.id}
                      title="Mark Completed"
                      className="p-2 rounded-xl bg-emerald-950/40 hover:bg-emerald-900/60 text-emerald-400 hover:text-emerald-200 border border-emerald-800/40 transition-colors"
                    >
                      {actionLoading === rem.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Check className="w-4 h-4" />
                      )}
                    </button>
                  )}

                  <button
                    onClick={() => handleDelete(rem.id, rem.title)}
                    disabled={actionLoading === rem.id}
                    title="Delete Reminder"
                    className="p-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-400 hover:text-rose-200 border border-rose-800/40 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showScanModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Scan Document for Actionable Dates</h3>
                  <p className="text-xs text-slate-400">
                    Extract warranties, expiries, renewals, and deadlines using the date intelligence engine
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowScanModal(false)}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6 overflow-y-auto flex-1">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300 block">
                  Select Processed Document
                </label>
                {availableDocs.length === 0 ? (
                  <p className="text-xs text-amber-400 bg-amber-950/30 p-3 rounded-lg border border-amber-900/30">
                    No processed documents found. Please process documents in Document Vault first.
                  </p>
                ) : (
                  <div className="flex gap-2">
                    <select
                      value={selectedScanDocId}
                      onChange={(e) => setSelectedScanDocId(e.target.value)}
                      className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      {availableDocs.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.original_filename} ({d.document_type})
                        </option>
                      ))}
                    </select>

                    <button
                      onClick={handleRunScan}
                      disabled={scanLoading || !selectedScanDocId}
                      className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all disabled:opacity-50 flex items-center space-x-1.5 shrink-0"
                    >
                      {scanLoading ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          <span>Scanning...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Run Scan</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {scanResult && (
                <div className="space-y-4 pt-4 border-t border-slate-800">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">
                      Detected Candidates ({scanResult.candidates_count})
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      {scanResult.document_filename}
                    </span>
                  </div>

                  {scanResult.candidates.length === 0 ? (
                    <div className="text-center py-8 text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800/60">
                      No actionable expiry, renewal, or warranty dates detected in this document.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {scanResult.candidates.map((cand, idx) => (
                        <div
                          key={idx}
                          className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                        >
                          <div className="space-y-1 text-xs">
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${formatBadgeType(cand.type)}`}>
                                {cand.type}
                              </span>
                              <span className="font-bold text-slate-200">
                                {cand.title}
                              </span>
                              <span className="text-[10px] text-slate-500 font-mono">
                                Conf: {Math.round(cand.confidence * 100)}%
                              </span>
                            </div>
                            <div className="text-slate-400 font-mono text-[11px]">
                              Date: {formatDate(cand.date)} {cand.page ? `· Page ${cand.page}` : ''}
                            </div>
                            <p className="text-[11px] text-slate-400 italic bg-slate-900/80 p-2 rounded border border-slate-800/40">
                              "{cand.source_text}"
                            </p>
                          </div>

                          <button
                            onClick={() => handleAddCandidate(cand)}
                            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shrink-0 self-start sm:self-center"
                          >
                            <Plus className="w-3.5 h-3.5" />
                            <span>Add Reminder</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                  <Plus className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Create New Reminder</h3>
                  <p className="text-xs text-slate-400">Configure actionable deadline & reminder lead time</p>
                </div>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateManualReminder} className="p-6 space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-300 block">Title *</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. AWS Cloud Contract Renewal"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-slate-300 block">Description (Optional)</label>
                <textarea
                  rows={2}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Additional context or account notes..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-300 block">Reminder Type</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="EXPIRY">EXPIRY</option>
                    <option value="WARRANTY">WARRANTY</option>
                    <option value="RENEWAL">RENEWAL</option>
                    <option value="PAYMENT">PAYMENT</option>
                    <option value="DEADLINE">DEADLINE</option>
                    <option value="CUSTOM">CUSTOM</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-slate-300 block">Lead Time Alert</label>
                  <select
                    value={newLeadDays}
                    onChange={(e) => setNewLeadDays(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value={0}>On the day (0 days before)</option>
                    <option value={1}>1 day before</option>
                    <option value={3}>3 days before</option>
                    <option value={7}>7 days before</option>
                    <option value={14}>14 days before</option>
                    <option value={30}>30 days before</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-slate-300 block">Due Date & Time *</label>
                <input
                  type="date"
                  required
                  value={newDueDate}
                  onChange={(e) => setNewDueDate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-slate-300 block">Link to Document (Optional)</label>
                <select
                  value={newDocId}
                  onChange={(e) => setNewDocId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">-- No linked document --</option>
                  {availableDocs.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.original_filename}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-all shadow-sm shadow-indigo-500/20"
                >
                  Save Reminder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
